import numpy as np
import cv2
from utils import FacialRecoLogin

# Time before locking/unlocking (in seconds)
time_before_lock = 3


if __name__ == '__main__':

    # Facial Reco object
    reco_login = FacialRecoLogin(time_before_lock=time_before_lock)

    # Grasp webcam
    video_capture = cv2.VideoCapture(0)

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # List of names and face locations
        face_names, face_locations = reco_login.frame_match(rgb_small_frame)

        # Looping on the face detected on the frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # If user recognized
            if name in reco_login.known_face_names:
                cv2.rectangle(frame, (left, top), (right, bottom),
                            (0, 255, 0), 2)
                # center1 = int((left+right)/2)
                # center2 = int((top+bottom)/2)
                # cv2.circle(frame, (center1, center2), int(
                #     right - (left+right)/2), (0, 255, 0), 7)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left, bottom + 30),
                            font, 1.0, (0, 255, 0), 1)
                cv2.putText(frame, "Authorized... " + str(np.round(reco_login.time_recognized, 1)), (left, bottom + 60),
                            font, 1.0, (0, 255, 0), 1)
            # If unknown
            else:
                cv2.rectangle(frame, (left, top),
                            (right, bottom), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 60, bottom - 40),
                            font, 1.0, (0, 0, 255), 1)
                cv2.putText(frame, "No access... " + str(np.round(reco_login.time_unknown, 1)), (left + 60, bottom + 6),
                            font, 1.0, (0, 0, 255), 1)

        # Check for lock/unlock timing
        if reco_login.time_recognized <= 0:
            reco_login.unlock(video_capture, speaker=True)

        elif reco_login.time_unknown <= 0:
            reco_login.lock(video_capture, speaker=True)

        # Show webcam output
        cv2.imshow('Video', frame)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
