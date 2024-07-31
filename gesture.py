import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize the Pycaw for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get the volume range
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Function to calculate the distance between two points
def calculate_distance(lm1, lm2):
    return ((lm1.x - lm2.x) ** 2 + (lm1.y - lm2.y) ** 2) ** 0.5

# Initialize variables for smoothing
smooth_factor = 0.9
current_vol = volume.GetMasterVolumeLevel()

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and find hands
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = hand_landmarks.landmark
            
            # Drawing landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get coordinates of thumb tip and index finger tip
            thumb_tip = lm_list[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = lm_list[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            
            # Calculate the distance between thumb tip and index finger tip
            distance = calculate_distance(thumb_tip, index_tip)
            
            # Convert distance to volume level
            vol = np.interp(distance, [0.02, 0.2], [min_vol, max_vol])
            
            # Smooth the volume changes
            current_vol = smooth_factor * current_vol + (1 - smooth_factor) * vol
            
            # Set the volume
            volume.SetMasterVolumeLevel(current_vol, None)
    
    # Display the frame
    cv2.imshow('Gesture Volume Control', frame)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
