
import cv2
#from http.server import BaseHTTPRequestHandler,HTTPServer
import numpy as np
import dlib
from math import hypot
from datetime import datetime
import time

cap = cv2.VideoCapture(0)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
#capture=None
font = cv2.FONT_HERSHEY_PLAIN
count=0
key=0
def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    #hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    #ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio

def get_gaze_ratio(eye_points, facial_landmarks, frame, gray):
    left_eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),(facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),(facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),(facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),(facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),(facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)
    # cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 2)
    height, width, _ = frame.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [left_eye_region], True, 255, 2)
    cv2.fillPoly(mask, [left_eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)
    min_x = np.min(left_eye_region[:, 0])
    max_x = np.max(left_eye_region[:, 0])
    min_y = np.min(left_eye_region[:, 1])
    max_y = np.max(left_eye_region[:, 1])
    gray_eye = eye[min_y: max_y, min_x: max_x]
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    height, width = threshold_eye.shape
    left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
    left_side_white = cv2.countNonZero(left_side_threshold)
    right_side_threshold = threshold_eye[0: height, int(width / 2): width]
    right_side_white = cv2.countNonZero(right_side_threshold)

    # print("left eye >>>>>>>>>> ")
    # print(left_side_white)

    # print("  ")

    # print("right eye >>>>>>>>>> ")
    # print(right_side_white)

    # print("  ")



    if left_side_white == 0:
        gaze_ratio = 1
    elif right_side_white == 0:
        gaze_ratio = 5
    else:
        gaze_ratio = left_side_white / right_side_white

        # if gaze_ratio > 1.4:
        #     print("LEFT")

        # elif gaze_ratio < 0.8: 
        #     print("RIGHT")

        # else:
        #     print("CENTRE")

    return gaze_ratio

a=0
count=0

while True:
    _, frame = cap.read()
    new_frame = np.zeros((500, 500, 3), np.uint8)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    for face in faces:
        # x, y = face.left(), face.top()
        # x1, y1 = face.right(), face.bottom()
        # cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

        landmarks = predictor(gray, face)

        # Detect blinking
        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        gaze_ratio_left_eye = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks,frame,gray)
        gaze_ratio_right_eye = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks,frame,gray)
        gaze_ratio = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2


        #############        Circles         #############
        for i in range(12):
            cv2.circle(frame,(landmarks.part(i+36).x, landmarks.part(i+36).y), 2, (0,0,255), -1)
        
        ################       lines    #################
        # left_point_left = (landmarks.part(36).x, landmarks.part(36).y)
        # right_point_left = (landmarks.part(39).x, landmarks.part(39).y)

        # center_top_left = midpoint(landmarks.part(37), landmarks.part(38))
        # center_bottom_left = midpoint(landmarks.part(41), landmarks.part(40))
        # hor_line_left = cv2.line(frame, left_point_left, right_point_left, (0, 255, 0), 2)
        # ver_line_left = cv2.line(frame, center_top_left, center_bottom_left, (0, 255, 0), 2)

        

        # left_point_right = (landmarks.part(42).x, landmarks.part(42).y)
        # right_point_right = (landmarks.part(45).x, landmarks.part(45).y)

        # center_top_right = midpoint(landmarks.part(43), landmarks.part(44))
        # center_bottom_right = midpoint(landmarks.part(46), landmarks.part(47))    
        # hor_line_right = cv2.line(frame, left_point_right, right_point_right, (0, 255, 0), 2)
        # ver_line_right = cv2.line(frame, center_top_right, center_bottom_right, (0, 255, 0), 2)

        # print("left eye >>>>>>>>>> ")
        # print(gaze_ratio_left_eye)

        # print(" right eye >>>>>>>>>>> ")
        # print(gaze_ratio_right_eye)

        
        if blinking_ratio > 5.7:
            if count==3:
                a=0
                print("START")
            if count==5:
                a=4
                count=0
                print("END")
            count=count+1                 
        else:
            if gaze_ratio <= 0.8:
                cv2.putText(frame, "RIGHT", (50, 100), font, 2, (0, 0, 255), 3)
                new_frame[:] = (0, 0, 255)
                a=1
                print("RIGHT")
                print(gaze_ratio)
            elif 2 < gaze_ratio <= 4:
                cv2.putText(frame, "CENTER", (50, 100), font, 2, (0, 0, 255), 3)
                a=2
                print("CENTRE")
                print(gaze_ratio)
            else:
                new_frame[:] = (255, 0, 0)
                cv2.putText(frame, "LEFT", (50, 100), font, 2, (0, 0, 255), 3)
                a=3
                print("LEFT")
                print(gaze_ratio)

    cv2.imshow("Frame", frame)
    #cv2.imshow("New frame", new_frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

'''class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        rc,frame = capture.read()
        new_frame = np.zeros((500, 500, 3), np.uint8)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        a=0
        global count
        for face in faces:
            landmarks = predictor(gray, face)
            left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            gaze_ratio_left_eye = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks,frame, gray)
            gaze_ratio_right_eye = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks,frame, gray)
            gaze_ratio = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2

            if blinking_ratio > 5.7:
                if count==3:
                    a=0
                    count=0
                    key+=1
                count=count+1        
                #cv2.putText(frame, "BLINKING", (50, 150), font, 7, (255, 0, 0))
            
            else:
                if ((key%2)!=0):
                    count=0
                    if gaze_ratio <= 0.85:
                        a=1
                        print("RIGHT")
                    elif 0.85 < gaze_ratio < 2.5:
                        a=2
                        print("CENTRE")
                    else:
                        a=3
                        print("LEFT")
                else:
                    a=0
        messagetosend=bytes(str(a),"utf")
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length',len(messagetosend))
        self.end_headers()
        self.wfile.write(messagetosend)
        cv2.imshow("FRAME",frame)
        #time.sleep(1)

        return
'''

        
def main():
    global capture
    capture=cv2.VideoCapture(0)
    #capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320); 
    #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);
    k=cv2.waitKey(1)
    server = HTTPServer(('192.168.0.255',8080),CamHandler)
    print ("server started")
    server.serve_forever()
    if k==27:
        capture.release()
        server.socket.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
