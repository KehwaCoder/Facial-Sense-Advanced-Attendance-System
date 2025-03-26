from tkinter import * 
import tkinter as tk
from tkinter import ttk
import time
import numpy as np
import cv2
import os
import dlib
import threading
from PIL import Image, ImageTk     
import pandas as pd
import sqlite3
from tensorflow.keras.models import load_model
import tkinter.messagebox as messagebox
from scipy.spatial import distance
import random
import pygame

root = tk.Tk()
root.configure(background="seashell2")
my_conn = sqlite3.connect('face.db')

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
root.title("Facial Sense")

# Background Image
image2 = Image.open('a.png')
image2 = image2.resize((w, h))
background_image = ImageTk.PhotoImage(image2)
background_label = tk.Label(root, image=background_image)
background_label.image = background_image
background_label.place(x=0, y=0)

lbl = tk.Label(root, text="Facial Sense", font=('Roboto', 40, 'bold'), height=1, width=15, bg="white", fg="black", anchor="center")
lbl.place(x=370, y=25)

frame_alpr = tk.LabelFrame(root, text=" ----------------------------Process----------------------------- ", width=480, height=500, bd=5, font=('times', 15, 'bold'), bg="white")
frame_alpr.grid(row=0, column=0, sticky='nw')
frame_alpr.place(x=170, y=157)

def Create_database():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    id = entry2.get()

    # Check if the ID is registered in the database
    conn = sqlite3.connect('face.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE id=?", (id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        # User ID not registered
        messagebox.showinfo("Information", "Please Register First!")
        return  # Exit the function if the user ID is not registered

    # User ID is registered, prompt to continue
    if messagebox.askyesno("Confirmation", "Data Exists. Would you still continue?"):
        sampleN = 0
        
        while True:
            ret, img = cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                sampleN += 1
                cv2.imwrite("facesData/User." + str(id) + "." + str(sampleN) + ".jpg", gray[y:y+h, x:x+w])
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.waitKey(100)
            
            cv2.imshow('img', img)
            cv2.waitKey(1)
            
            if sampleN > 40:
                break
        
        cap.release()
        entry2.delete(0, 'end')
        cv2.destroyAllWindows()
    else:
        # User chose not to continue
        messagebox.showinfo("Information", "Face data capture canceled.")
def update_label(str_T, duration=5):
    result_label = tk.Label(root, text=str_T, width=40, font=("bold", 25), bg='bisque2', fg='black')
    result_label.place(x=300, y=400)
    root.after(duration * 1000, result_label.destroy)

import tkinter as tk
from tkinter import messagebox
import os
import numpy as np
import cv2
import sqlite3
from PIL import Image

def Train_database():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    path = "facesData/"
    
    def getImagesWithID(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faces = []
        IDs = []
        Names = []

        conn = sqlite3.connect('face.db')
        cursor = conn.cursor()

        for imagePath in imagePaths:
            facesImg = Image.open(imagePath).convert('L')
            faceNP = np.array(facesImg, 'uint8')
            
            try:
                ID = int(os.path.split(imagePath)[-1].split(".")[1])
                cursor.execute("SELECT Name FROM User WHERE id=?", (ID,))
                result = cursor.fetchone()
                name = result[0] if result else "Unknown"

                faces.append(faceNP)
                IDs.append(ID)
                Names.append(name)
                cv2.imshow("Adding faces for training", faceNP)
                cv2.waitKey(10)

            except (IndexError, ValueError):
                continue

        conn.close()
        return np.array(IDs), faces, Names

    def load_existing_ids(recognizer):
        """Load existing IDs from the training data."""
        try:
            recognizer.read("trainingdata.yml")
            # Extract existing labels (IDs) from the recognizer
            existing_labels = recognizer.getLabels()  # This method may vary based on your OpenCV version
            return existing_labels.flatten().tolist()  # Convert to a flat list
        except Exception as e:
            print(f"Error loading existing training data: {e}")
            return []

    def ask_user_confirmation():
        """Ask the user for confirmation to continue training."""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        response = messagebox.askyesno("No New Faces", "No new faces to train. Would you like to retrain with existing data?")
        return response

    # Load existing IDs
    existing_ids = load_existing_ids(recognizer)
    existing_ids_set = set(existing_ids)  # Use a set for faster lookup

    Ids, faces, Names = getImagesWithID(path)

    # Check if there are new faces to train
    if len(faces) > 0:
        recognizer.train(faces, Ids)
        recognizer.save("trainingdata.yml")
        print("Training completed with new data.")
        
        # Display message box when training is complete
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("Training Complete", "Face training data has been successfully updated.")
    else:
        print("No new faces to train.")
        if existing_ids_set:  # Check if there are existing IDs to retrain
            if ask_user_confirmation():
                # Proceed with retraining all data
                print("Retraining all face data.")
                # Get all images again (including existing ones)
                Ids, faces, Names = getImagesWithID(path)  # Get all images again
                recognizer.train(faces, Ids)
                recognizer.save("trainingdata.yml")
                print("Training completed with existing data.")
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                messagebox.showinfo("Training Complete", "Face training data has been successfully retrained.")
            else:
                print("Training aborted by user.")
        else:
            print("No existing data to retrain.")

    cv2.destroyAllWindows()

# Initialize pygame mixer
pygame.mixer.init()

# Define the path to your Music folder
music_directory = 'C:/Users/Aayan/Desktop/Facial Sense/Music'

# Dictionary mapping moods to folder names
mood_folder_mapping = {
    'happy': 'happy',
    'neutral': 'neutral',
    'sad': 'sad',
    'angry': 'angry',
    'fearful': 'fearful',
    'surprised': 'surprised',
}

# Dictionary to keep track of last song play time for each user
last_play_time = {}
song_play_duration = 30  # Duration to play the song in seconds
cooldown_duration = 3600  # 1 hour in seconds

# Function to play a random song from the appropriate mood folder in a separate thread
def play_mood_song_locally(mood, user_id):
    mood_folder = mood_folder_mapping.get(mood, 'happy')  # Default to 'happy' if mood is not recognized
    folder_path = os.path.join(music_directory, mood_folder)

    if os.path.exists(folder_path) and os.listdir(folder_path):  # Check if folder exists and has files
        song = random.choice(os.listdir(folder_path))  # Pick a random song from the folder
        song_path = os.path.join(folder_path, song)
        print(f"Playing {song} for mood: {mood}")

        # Load and play the song using pygame
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

        # Store the current time as the last play time for the user
        last_play_time[user_id] = time.time()

        # Play the song for the specified duration in a non-blocking way
        threading.Timer(song_play_duration, stop_song).start()

    else:
        print(f"No songs found in folder for mood: {mood}")

# Function to stop the music after the specified duration with a 5-second fadeout effect
def stop_song():
    fadeout_duration = 5000  # 5 seconds in milliseconds
    pygame.mixer.music.fadeout(fadeout_duration)

# Function to handle playing music in a separate thread
def play_song_in_background(mood, user_id):
    song_thread = threading.Thread(target=play_mood_song_locally, args=(mood, user_id))
    song_thread.start()

# Test_database function with emotion detection and attendance marking
def Test_database():
    # Load Dlib's face detector and shape predictor for facial landmarks
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    # Load the emotion detection model
    model = load_model('emotion_detection_model.keras')

    # Initialize the face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainingdata.yml')
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    font = cv2.FONT_HERSHEY_SIMPLEX
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    # Emotion labels
    labels_dict = {0: 'angry', 1: 'disgust', 2: 'fearful', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprised'}

    # Stress level mapping based on detected emotion
    stress_mapping = {
        'angry': 'high',
        'disgust': 'high',
        'fearful': 'high',
        'sad': 'moderate',
        'neutral': 'low',
        'happy': 'low',
        'surprised': 'low'
    }

    # Blink detection parameters
    blink_counter = 0
    blink_threshold = 3  # Number of blinks required to confirm liveness
    blink_state = False  # Track if the eyes are currently closed
    blink_detected = False  # Track if a blink has been detected

    # Head movement detection parameters
    head_movement_counter = 0
    head_movement_threshold = 5  # Number of head movements required to confirm liveness
    last_face_position = None
    liveness_confirmed = False

    # Load the Haar Cascade for glasses detection
    glasses_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')

    while True:  # Keep the webcam active until manually closed
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 8, minSize=(int(minW), int(minH)))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            print(f"ID: {id}, Confidence: {confidence}")  # Log the ID and confidence levels

            # Adjusted threshold for better accuracy
            min_confidence_threshold = 55  # You can adjust this value

            if confidence < min_confidence_threshold:  # If confidence is acceptable
                confidence_text = "{0}%".format(round(100 - confidence))

                # Emotion Detection
                sub_face_img = gray[y:y + h, x:x + w]
                resized = cv2.resize(sub_face_img, (48, 48))
                normalized = resized / 255.0
                reshaped = np.reshape(normalized, (1, 48, 48, 1))
                result = model.predict(reshaped)
                emotion_label = np.argmax(result, axis=1)[0]
                emotion_text = labels_dict[emotion_label]

                # Get the stress level based on the detected emotion
                stress_level = stress_mapping[emotion_text]

                # Fetch the name corresponding to the matched id from the database
                conn = sqlite3.connect('face.db')
                cursor = conn.cursor()
                cursor.execute("SELECT Name FROM User WHERE id=?", (id,))
                result = cursor.fetchone()
                name = result[0] if result else "Unknown"
                conn.close()

                if name != "Unknown":
                    # Display the name and emotion in the bounding box
                    label = f'{name}, {emotion_text}'
                    cv2.putText(img, label, (x, y - 10), font, 0.7, (255, 255, 255), 2)

                    # Liveness Detection
                    # Get facial landmarks
                    detected_faces = detector(gray)
                    if len(detected_faces) > 0:
                        landmarks = predictor(gray, detected_faces[0])
                        # Get coordinates for the left and right eye
                        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

                        # Draw rectangles around the eyes
                        cv2.polylines(img, [left_eye], isClosed=True, color=(0, 255, 0), thickness=2)
                        cv2.polylines(img, [right_eye], isClosed=True, color=(0, 255, 0), thickness=2)

                        # Calculate EAR for both eyes
                        ear_left = eye_aspect_ratio(left_eye)
                        ear_right = eye_aspect_ratio(right_eye)
                        ear = (ear_left + ear_right) / 2.0

                        # Blink detection logic
                        if ear < 0.25:
                            if not blink_state:  # If eyes were previously open
                                blink_state = True  # Set state to closed
                                blink_detected = True  # Mark that a blink has been detected
                        else:
                            if blink_state and blink_detected:  # If eyes were closed and a blink was detected
                                blink_counter += 1
                                print(f"You've blinked {blink_counter} times")
                                blink_detected = False  # Reset blink detected
                                blink_state = False  # Reset state to open

                        # Head Movement Detection
                        current_face_position = (x, y)
                        if last_face_position is not None:
                            if abs(current_face_position[0] - last_face_position[0]) > 10 or abs(current_face_position[1] - last_face_position[1]) > 10:
                                head_movement_counter += 1
                                print(f"Head Move Count: {head_movement_counter}")
                        last_face_position = current_face_position

                        if blink_counter >= blink_threshold and head_movement_counter >= head_movement_threshold:
                            liveness_confirmed = True
                            blink_counter = 0
                            head_movement_counter = 0

                        if liveness_confirmed ==True:
                            cv2.putText(img, "Live Person Detected", (x, y + h + 20), font, 0.7, (0, 255, 0), 2)
                            # Mark attendance for the matched user, including the detected emotion and stress level
                            mark_attendance(id, confidence_text, emotion_text, stress_level)
                            # Check if the user has been recognized in the last hour
                            update_label(f'User      {name} Authenticated Successfully...')
                            print(f"User     {name} recognized, marking attendance.")  # Log the attendance
                            if id not in last_play_time or time.time() - last_play_time[id] > cooldown_duration:
                                # Play music based on detected emotion in a separate thread
                                play_song_in_background(emotion_text, id)
                        else:
                            cv2.putText(img, "Please Blink and Move Your Head", (x, y + h + 20), font, 0.7, (0, 0, 255), 2)

                        # Glasses Detection
                        sub_face_img_color = img[y:y + h, x:x + w]
                        gray_face_img = cv2.cvtColor(sub_face_img_color, cv2.COLOR_BGR2GRAY)
                        glasses = glasses_cascade.detectMultiScale(gray_face_img, scaleFactor=1.1, minNeighbors=5)
                        glasses_detected = len(glasses) > 0
                        cv2.putText(img, "No Glasses: " + str(glasses_detected), (x + 5, y + h + 40), font, 0.5, (0, 255, 0), 1)

            else:  # Unidentified user case
                cv2.putText(img, 'Unauthenticated User', (x, y -  10), font, 0.7, (0, 0, 255), 2)
                update_label('Ooops!!!!!....Unauthenticated User..')
                print("User  not recognized.")  # Log for unidentified users

        cv2.imshow('camera', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to close the camera
            break

    cam.release()
    cv2.destroyAllWindows()

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])  # Vertical distance
    B = distance.euclidean(eye[2], eye[4])  # Vertical distance
    C = distance.euclidean(eye[0], eye[3])  # Horizontal distance
    return (A + B) / (2.0 * C)

def mark_attendance(id, confidence, emotion, stress):  
    filename = os.path.join(os.getcwd(), 'attendance.xlsx')  
    now = time.strftime("%Y-%m-%d %H:%M:%S")  
    today_date = time.strftime("%Y-%m-%d")  # Get current date for comparison
    
    # Retrieve the name from the database based on the ID  
    conn = sqlite3.connect('face.db')  
    cursor = conn.cursor()  
    cursor.execute("SELECT Name FROM User WHERE id=?", (id,))  
    result = cursor.fetchone()  
    name = result[0] if result else "Unknown"  
    conn.close()  
    
    # If the user is not registered, don't write to the file
    if name == "Unknown":
        print("User not recognized, skipping attendance entry.")
        return
    
    # Load the attendance file if it exists
    if os.path.isfile(filename):  
        try:
            existing_data = pd.read_excel(filename)
            
            # Check if there is already an entry for the user for the current date
            existing_entry = existing_data[
                (existing_data['ID'] == id) & 
                (existing_data['Date/Time'].str.contains(today_date))
            ]
            
            if not existing_entry.empty:  
                print(f"Attendance for {name} already taken today. Skipping entry.")
                return  # Exit the function, no need to add a new entry

        except Exception as e:
            print(f"Error reading the attendance file: {e}")
    
    # Create a new entry with the name, ID, date/time, confidence, emotion, and stress  
    new_entry = pd.DataFrame([[name, id, now, confidence, emotion, stress]], columns=['Name', 'ID', 'Date/Time', 'Confidence', 'Emotion', 'Stress'])  
    
    try:  
        if not os.path.isfile(filename):  
            print(f"File {filename} not found. Creating a new attendance file.")
            new_entry.to_excel(filename, index=False)  
        else:  
            # Append the new entry to the existing data  
            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)  
    
            # Write the updated data to the Excel file  
            updated_data.to_excel(filename, index=False)  
            print(f"Attendance recorded successfully for {name}.")

    except PermissionError:  
        print("Error: Permission denied. Please close the attendance.xlsx file and try again.")  


def registration():
    from subprocess import call
    call(["python", "registration.py"]) 

def display():
    from subprocess import call
    call(["python", "display.py"]) 

def window():
    root.destroy()

button1 = tk.Button(frame_alpr, text="Registration Of User", command=registration, width=20, height=1, font=('Roboto', 15, 'bold'), bg="purple", fg="white")
button1.place(x=100, y=40)

button2 = tk.Button(frame_alpr, text="Create Face Data", command=Create_database, width=15, height=1, font=('Roboto', 15, 'bold'), bg="purple", fg="white")
button2.place(x=100, y=100)

button3 = tk.Button(frame_alpr, text="Train Face Data", command=Train_database, width=20, height=1, font=('Roboto', 15, 'bold'), bg="purple", fg="white")
button3.place(x=100, y=160)

button4 = tk.Button(frame_alpr, text="Face Attendance", command=Test_database, width=20, height=1, font=('Roboto', 15, 'bold'), bg="purple", fg="white")
button4.place(x=100, y=220)

entry2 = tk.Entry(frame_alpr, bd=2, width=7)
entry2.place(x=310, y=110)

exit = tk.Button(frame_alpr, text="Exit", command=window, width=12, height=1, font=('times', 15, 'bold'), bg="red", fg="black")
exit.place(x=150, y=340)

root.mainloop()
