import cv2
import os

# Load gesture template
gesture_template_path = 'jump.png'

# Check if the gesture template file exists
if not os.path.exists(gesture_template_path):
    print(f"Error: The file {gesture_template_path} does not exist.")
else:
    gesture_template = cv2.imread(gesture_template_path, cv2.IMREAD_GRAYSCALE)
    
    if gesture_template is None:
        print(f"Error: Unable to load the image {gesture_template_path}. Please check the file path and integrity.")
    else:
        # Initialize SIFT detector
        sift = cv2.SIFT_create()

        # Detect keypoints and descriptors for gesture template
        keypoints_template, descriptors_template = sift.detectAndCompute(gesture_template, None)

        # Read test video sequence
        test_video_path = 'jumping.mp4'
        test_video = cv2.VideoCapture(test_video_path)

        # Define the codec and create VideoWriter object
        output_video_path = 'detected.avi'
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_video = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(test_video.get(3)), int(test_video.get(4))))

        # Define the font and text to overlay
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 3
        thickness = 3
        text = 'DETECTED'
        text_color = (0, 255, 0)  # Bright green color

        # Iterate through each frame of the test video sequence
        while True:
            ret, frame = test_video.read()
            if not ret:
                break

            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect keypoints and descriptors for current frame
            keypoints_frame, descriptors_frame = sift.detectAndCompute(gray_frame, None)

            # Match descriptors between template and frame
            matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
            knn_matches = matcher.knnMatch(descriptors_template, descriptors_frame, k=2)

            # Filter matches using ratio test
            good_matches = []
            for m, n in knn_matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)

            # Check if enough good matches are found to consider gesture detected
            if len(good_matches) > 10:  # Adjust the threshold as needed
                # Overlay "DETECTED" text on the top right corner of the frame
                cv2.putText(frame, text, (frame.shape[1] - 600, 150), font, font_scale, text_color, thickness)

            # Write the frame to the output video
            output_video.write(frame)

            # Display the frame
            cv2.imshow('Frame', frame)

            # Check for exit key
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        # Release all resources
        test_video.release()
        output_video.release()
        cv2.destroyAllWindows()