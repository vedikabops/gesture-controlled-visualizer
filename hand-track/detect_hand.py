import cv2
import mediapipe as mp
import math

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pythonosc.udp_client import SimpleUDPClient
from pathlib import Path

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9,10), (10,11), (11,12),
    (9,13), (13,14), (14,15), (15,16),
    (13,17), (17,18), (18,19), (19,20),
    (0,17)
]

def calc_dist(p1, p2):
    return math.sqrt(
        (p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2
    )

client = SimpleUDPClient(
    "127.0.0.1",
    8000
)

# load model
model_path = Path(__file__).parent / "models" / "hand_landmarker.task"
base_options = python.BaseOptions(model_asset_path=str(model_path))

options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2, running_mode=vision.RunningMode.VIDEO)

landmarker =  vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

timestamp_ms = 0

while True:
    timestamp_ms += 33
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if not success:
        print("Failed to capture image")
        break

    #convert opencv image into rgb
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #convert to mediapipe
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    result = landmarker.detect_for_video(mp_img, timestamp_ms)

    h, w, _ = img.shape
    

    for hand, handedness in zip(result.hand_landmarks, result.handedness):

        hand_label = handedness[0].category_name

        wrist = hand[0]
        thumb_tip = hand[4]
        index_tip = hand[8]
        index_mcp = hand[5]

        middle_tip = hand[12]
        middle_pip = hand[10]
        middle_mcp = hand[9]

        ring_tip = hand[16]
        ring_pip = hand[14]
        ring_mcp = hand[13]

        pinky_tip = hand[20]
        pinky_pip = hand[18]
        pinky_mcp = hand[17]

        index_tip_dist = calc_dist(wrist, index_tip)
        index_base_dist = calc_dist(wrist, index_mcp)

        mid_tip_dist = calc_dist(wrist, middle_tip)
        mid_base_dist = calc_dist(wrist, middle_mcp)

        ring_tip_dist = calc_dist(wrist, ring_tip)
        ring_base_dist = calc_dist(wrist, ring_mcp)

        pinky_tip_dist = calc_dist(wrist, pinky_tip)
        pinky_base_dist = calc_dist(wrist, pinky_mcp)

        index_curled = index_tip_dist < index_base_dist
        middle_curled = mid_tip_dist < mid_base_dist
        ring_curled = ring_tip_dist < ring_base_dist
        pinky_curled = pinky_tip_dist < pinky_base_dist

        thumb_x = int(thumb_tip.x*w)
        thumb_y = int(thumb_tip.y*h)

        index_x = int(index_tip.x*w)
        index_y = int(index_tip.y*h)

        dx = index_tip.x - thumb_tip.x
        dy = index_tip.y - thumb_tip.y

        pinch_mode = middle_curled and ring_curled and pinky_curled and not index_curled

        fist_mode = index_curled and middle_curled and ring_curled and pinky_curled

        open_hand_mode = (not index_curled and not middle_curled and not ring_curled and not pinky_curled)

        hand_openness = calc_dist(index_tip, pinky_tip)
        #print(f"Hand Openness: {hand_openness:.3f}")

        pinch_distance = calc_dist(thumb_tip, index_tip)
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        control_data = {
            "hand": hand_label,

            "pinch" : pinch_mode,
            "fist" : fist_mode,
            "open_hand" : open_hand_mode,

            "pinch_distance" : pinch_distance,
            "pinch_angle" : angle_deg,
            "hand_openness" : hand_openness
        }
        
        client.send_message(f"/{hand_label}_pinch_distance", pinch_distance)
        client.send_message(f"/{hand_label}_pinch_angle", angle_deg)
        client.send_message(f"/{hand_label}_hand_openness", hand_openness)

        client.send_message(f"/{hand_label}_pinch", int(pinch_mode))
        client.send_message(f"/{hand_label}_fist", int(fist_mode))
        client.send_message(f"/{hand_label}_open_hand", int(open_hand_mode))

        if not pinch_mode:
            for landmark in hand:
                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(img, (x, y), 5, (255, 255, 255), -1)
            
            for start_idx, end_idx in HAND_CONNECTIONS:
                
                start = hand[start_idx]
                end = hand[end_idx]

                x1 = int(start.x * w)
                y1 = int(start.y * h)

                x2 = int(end.x * w)
                y2 = int(end.y * h)

                cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
        elif pinch_mode and not fist_mode:
            
            #print(f"Pinch Distance: {pinch_distance:.3f}")

            #print(f"Pinch Angle: {angle_deg:.2f} degrees")

            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (255, 255, 255), 3)

    cv2.imshow("Image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
        break


cap.release()
cv2.destroyAllWindows()