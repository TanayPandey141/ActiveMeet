import cv2
import numpy as np
import dlib
from imutils import face_utils
import pymongo
import tkinter as tk
import threading
import time

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['meetapp']
collection = db['tester']

def delete_document(name):
    collection.delete_one({'name':name})

def on_enter():
    global name
    name = entry.get()
    StartWindow.destroy()

StartWindow = tk.Tk()
label = tk.Label(StartWindow, text="Enter your name:")
label.pack()
entry = tk.Entry(StartWindow)
entry.pack()
button = tk.Button(StartWindow, text="Enter", command=on_enter)
button.pack()

StartWindow.mainloop()
print("Name entered:", name)
#Initializing the camera and taking the instance
document={
    "name":name,
    "status":"Active",
    "active_time":0
}
collection.insert_one(document)
cap = cv2.VideoCapture(0)

#Initializing the face detector and landmark detector
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#status marking for current state
sleep = 0
drowsy = 0
active = 0
total_active = 0
status = ""
color = (0,0,0)

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    # Checking if it is blinked
    if ratio > 0.25:
        return 2
    elif ratio > 0.21 and ratio <= 0.25:
        return 1
    else:
        return 0

def update_db():
    global total_active

    while True:
        collection.update_one({"name": name}, {"$set": {"status": status, "active_time": total_active/10}})
        time.sleep(0.2)

# Start the update thread
update_thread = threading.Thread(target=update_db)
update_thread.start()

while True:
    _, frame = cap.read()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    #detected face in faces array
    face_frame = frame.copy()
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        #The numbers are actually the landmarks which will show eye
        left_blink = blinked(landmarks[36],landmarks[37], 
        	landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42],landmarks[43], 
        	landmarks[44], landmarks[47], landmarks[46], landmarks[45])
        
        #Now judge what to do for the eye blinks
        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                status = "Sleeping"
                color = (255, 0, 0)

        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 6:
                status = "Drowsy"
                color = (0, 0, 255)

        else:
            drowsy = 0
            sleep = 0
            active += 1
            total_active += 1
            if active > 6:
                status = "Active"
                color = (0, 255, 0)
        
        numerical_position = (100, 150)
        numerical_font = cv2.FONT_HERSHEY_SIMPLEX
        numerical_font_scale = 1
        numerical_color = (255, 255, 255)
        numerical_thickness = 2
        cv2.putText(frame, str(total_active/10), numerical_position, numerical_font, 
                    numerical_font_scale, numerical_color, numerical_thickness)

        cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)
    
    cv2.imshow("Frame", frame)
    cv2.imshow("Result of detector", face_frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# Wait for the update thread to finish
update_thread.join()

cv2.destroyAllWindows()
cap.release() 
delete_document(name)

