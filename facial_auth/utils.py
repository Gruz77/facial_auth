import face_recognition
import cv2
import numpy as np
import pyttsx3
from datetime import datetime
import time
import os
import sys

class FacialRecoLogin(object):
    """
    Facial recognition from webcam frames, using facial_recognition lib.
    """
    def __init__(self, other_persons={}, time_before_lock=5):
        """
        Input:
            - other_persons: dictionnary with key/value pairs as "person_name": "person_name.png"
        """
        # Type check-in -> dictionnary if other users added
        if not isinstance(other_persons, dict):
            raise TypeError('other_persons must be a dictionnary.\nEvery photos must be in FaceBank folder.')

        # Encoding known users -> Allowed users (names and encodings in two list because of type constraints in face_recognition lib)
        self.faces_bank_path = os.getcwd() + "/FaceBank/"
        self.known_face_encodings = [self.enregistrer_user("me.png")]
        self.known_face_names = ['Antoine'] # to change
        if len(other_persons) != 0:
            for person_name, img_name in zip(list(other_persons.keys()), list(other_persons.values())):
                self.known_face_encodings.append(self.enregistrer_user(img_name))
                self.known_face_names.append(person_name)

        # Variables initialization
        self.all_face_names = []

        # Time running before lock/unlock -> will decrease to 0
        self.time_recognized = time_before_lock
        self.time_unknown = time_before_lock

    def enregistrer_user(self, img):
        """
        Face encoding (array of size (128,))
        Input:
            - file name (image)
        """
        load_img = face_recognition.load_image_file(
            os.path.join(self.faces_bank_path, img))
        return face_recognition.face_encodings(load_img)[0]

    def frame_match(self, frame):
        """
        Match names and faces location in current frame
        Input:
            - The current frame from webcam (opencv).
        """
        # Initialize time
        start_time = time.time()
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(frame)
        # Encoding faces from face locations
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # Let's suppose the name is unknown
            name = "Unknown"
            # matches: list of booleans -> True if the distance (euclidian) between face_encoding all all known faces encoding is <= threshold of 0.6
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            # Euclidian distances values
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            # Index of the minimal distance
            best_match_index = np.argmin(face_distances)
            # If match is True
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                self.time_recognized -= (time.time() - start_time)
                self.all_face_names.append(name)
            else:
                self.time_unknown -= (time.time() - start_time)
            face_names.append(name)
        return face_names, face_locations

    def unlock(self, video_capture, speaker=False):
        """
        Close the program. Access authorized.
        """
        video_capture.release()
        cv2.destroyAllWindows()
        if speaker:
            speaker = Speaker()
            speaker.unlock(self.all_face_names[-1])
        sys.exit()

    def lock(self, video_capture, speaker=False):
        """
        Close the program. Lock the laptop.
        """
        # Magic formula
        os.system("osascript -e 'tell app \"loginwindow\" to  «event aevtrlgo»'")
        video_capture.release()
        cv2.destroyAllWindows()
        if speaker:
            speaker = Speaker()
            speaker.lock()
        sys.exit()


class Speaker(object):
    """
    Speaker class, using the driver with pyttsx3.
    Inputs (Feel free to change):
        - Language: 'en_US' by default.
        - Gender: Female by default. For each language, 'VoiceGenderFemale' for female and 'VoiceGenderMale' for male gender.
    Feel free to add you own functions.
    """
    def __init__(self, language='en_US', gender='VoiceGenderFemale'):
        # Engine initialization
        self.engine = pyttsx3.init()

        for voice in self.engine.getProperty('voices'):
            if language in voice.languages and gender == voice.gender:
                self.engine.setProperty('voice', voice.id)
                break

    def lock(self):
        self.engine.say("Access denied. Locking.")
        self.engine.runAndWait()
        # self.engine.stop()

    def unlock(self, name):
        self.engine.say("Hello {}".format(name.split(" ")[0]))
        if (datetime.now().hour in range(5, 17)):
            self.engine.say("have a nice day!")
            self.engine.runAndWait()
            self.engine.stop()
        else:
            self.engine.say("Good evening !")
            self.engine.runAndWait()
            self.engine.stop()

    def joke(self):
        # ...
        pass
