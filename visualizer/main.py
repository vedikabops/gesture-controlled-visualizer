import moderngl_window as mglw
import numpy as np
import glm
from gesture_receiver import GestureReceiver

class Visualizer(mglw.WindowConfig):
    gl_version = (3, 3)

    def generate_targets(self, seed=None):
        if seed is not None:
            np.random.seed(seed)
        
        self.targets = np.random.uniform(-self.cluster_radius, self.cluster_radius, (20, 3)).astype('f4')


    def __init__(self, **kwargs):

        self.receiver = GestureReceiver()
        
        super().__init__(**kwargs)

        cube_vertices = np.array([
            -0.5, -0.2, -0.5,  # 0
            0.5, -0.2, -0.5,  # 1
            0.5,  0.2, -0.5,  # 2
            -0.5,  0.2, -0.5,  # 3

            -0.5, -0.2,  0.5,  # 4
            0.5, -0.2,  0.5,  # 5
            0.5,  0.2,  0.5,  # 6
            -0.5,  0.2,  0.5   # 7
        ], dtype='f4')

        cube_indices = np.array([
            0,1, 1,2, 2,3, 3,0,
            4,5, 5,6, 6,7, 7,4,
            0,4, 1,5, 2,6, 3,7
        ], dtype='i4')

        self.cluster_radius = 1
        self.prev_scale = 0.0
        self.cube_scale = 0.3
        self.prev_height = 0.0
        self.cube_height = 0.2
        self.seed = 0
        self.last_seed = 0
        self.last_cluster_radius = self.cluster_radius
        self.positions = np.random.uniform(-1.0, 1.0, (20, 3)).astype('f4')
        self.move_speed = np.random.uniform(0.01, 0.03, 20).astype("f4")
        self.generate_targets()
        self.particle_size = 100.0
        

        self.prog = self.ctx.program(
            vertex_shader = '''
            #version 330
                
            uniform mat4 projection;
            uniform mat4 view;
            uniform float cube_scale;
            uniform float cube_height;
            

            in vec3 in_position;
            in vec3 in_offset;

            void main(){
                vec3 scaled_pos = vec3(in_position.x * cube_scale, in_position.y * cube_height, in_position.z * cube_scale);
                vec3 world_pos = scaled_pos + in_offset;
                gl_Position = projection * view * vec4(world_pos, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330

            out vec4 fragColor;

            void main() {
                fragColor = vec4(1.0, 1.0, 1.0, 1.0);
            }
            '''
        )

        self.camera_pos = glm.vec3(0, 0, 3)

        self.projection = glm.perspective(glm.radians(45.0), self.wnd.aspect_ratio, 0.1, 100.0)

        self.view = glm.lookAt(self.camera_pos, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

        self.prog["projection"].write(self.projection.to_bytes())
        self.prog["view"].write(self.view.to_bytes())
        self.prog["cube_scale"] = self.cube_scale
        self.prog["cube_height"] = self.cube_height

        self.vbo = self.ctx.buffer(cube_vertices.tobytes())
        self.instance_buffer = self.ctx.buffer(self.positions.tobytes())
        self.ibo = self.ctx.buffer(cube_indices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '3f', 'in_position'), (self.instance_buffer, '3f/i', 'in_offset')], self.ibo)
    


    def on_render(self, time, frame_time):
        self.ctx.clear(0.0, 0.0, 0.0)

        self.positions += (self.targets - self.positions) * self.move_speed[:, None]

        radius = 3.0
        camera_angle = 0.0
        if self.receiver.left["pinch"]:
            camera_angle = -np.radians(self.receiver.left["pinch_angle"])

        cam_x =  np.sin(camera_angle) * radius
        cam_z = np.cos(camera_angle) * radius

        view = glm.lookAt(
            glm.vec3(cam_x, 0, cam_z),
            glm.vec3(0, 0, 0),
            glm.vec3(0, 1, 0)
        )

        # left hand
        current = self.receiver.right["pinch_distance"]
        delta = current - self.prev_scale
        noise_threshold = 0.003
        transition_threshold = 0.03
        if (self.receiver.right["pinch"] and abs(delta) > noise_threshold and abs(delta) < transition_threshold):
           self.cube_scale += delta * 5
        self.prev_scale = current
        self.cube_scale = np.clip(self.cube_scale, 0.1, 3.0)

        
        # right hand
        current_height = self.receiver.left["pinch_distance"]
        delta_height = current_height - self.prev_height
        if (self.receiver.left["pinch"] and abs(delta_height) > noise_threshold and abs(delta_height) < transition_threshold):
            self.cube_height += delta_height * 3
        self.prev_height = current_height
        self.cube_height = np.clip(self.cube_height, 0.1, 3.0)

        if self.receiver.right["open_hand"]:
            self.cluster_radius = (self.receiver.right["hand_openness"] * 2)

        if abs(self.cluster_radius - self.last_cluster_radius) > 0.05:
            self.generate_targets(seed=self.seed)
            self.last_cluster_radius = self.cluster_radius

        self.prog["view"].write(view.to_bytes())
        self.prog["cube_scale"] = self.cube_scale
        self.prog["cube_height"] = self.cube_height
        self.instance_buffer.write(self.positions.astype('f4').tobytes())
        #self.vbo.write(self.positions.astype('f4').tobytes())
        self.vao.render(mode=self.ctx.LINES, instances = 20)


if __name__ == "__main__":
    mglw.run_window_config(Visualizer)