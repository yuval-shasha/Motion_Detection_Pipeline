import string
from datetime import datetime
from time import sleep

import cv2 as cv
import numpy as np
import multiprocessing as mp
import imutils


def streamer(out_conn, video_file_name):
    captured_video = cv.VideoCapture(video_file_name)

    if not captured_video.isOpened():
        out_conn.send("END")
        out_conn.close()
        raise ValueError(f"Could not open video {video_file_name}.")

    fps_rate = captured_video.get(cv.CAP_PROP_FPS)

    while True:
        ret, frame = captured_video.read()
        if not ret:
            out_conn.send("END")
            out_conn.close()
            break
        out_conn.send(frame)
        sleep(1/fps_rate)

def detector(in_conn, out_conn):
    count = 0
    prev_frame = None
    while True:
        if in_conn.poll(0.5):
            curr_frame = in_conn.recv()
            if isinstance(curr_frame, str) and curr_frame == "END":
                in_conn.close()
                out_conn.send("END")
                out_conn.close()
                break

            gray_frame = cv.cvtColor(curr_frame, cv.COLOR_BGR2GRAY)
            if count == 0:
                prev_frame = gray_frame
                count += 1
            else:
                diff = cv.absdiff(gray_frame, prev_frame)
                thresh = cv.threshold(diff, 25, 255, cv.THRESH_BINARY)[1]
                thresh = cv.dilate(thresh, None, iterations=2)
                contours = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(contours)
                prev_frame = gray_frame
                count += 1
                detections = []
                for c in contours:
                    x, y, w, h = cv.boundingRect(c)
                    detections.append((x, y, w, h))
                out_conn.send((curr_frame, detections))


def presenter(in_conn):
    while True:
        if in_conn.poll(0.5):
            curr_data = in_conn.recv()
            if isinstance(curr_data, str) and curr_data == "END":
                in_conn.close()
                break

            curr_frame, curr_detections = curr_data
            for detection in curr_detections:
                x, y, w, h = detection
                green_color = (0, 255, 0)
                cv.rectangle(curr_frame, (x, y), (x+w, y+h), green_color, 2)

            timestamp = datetime.now().strftime("%H:%M:%S")
            red_color = (0, 0, 255)
            cv.putText(curr_frame, timestamp, (0,25), cv.FONT_HERSHEY_SIMPLEX, 1, red_color, 2)

            cv.imshow("Video with detections", curr_frame)
            if cv.waitKey(1) & 0xFF == ord("q"):
                in_conn.close()
                break


if __name__ == '__main__':
    video_name = "People - 6387.mp4"
    write_conn_streamer, read_conn_detector = mp.Pipe()
    write_conn_detector, read_conn_presenter = mp.Pipe()

    streamer_process = mp.Process(target=streamer, args=(write_conn_streamer, video_name))
    detector_process = mp.Process(target=detector, args=(read_conn_detector, write_conn_detector))
    presenter_process = mp.Process(target=presenter, args=(read_conn_presenter,))

    # streamer(write_conn_streamer, video_name)
    # detector(read_conn_detector, write_conn_detector)
    # presenter(read_conn_presenter)

    streamer_process.start()
    detector_process.start()
    presenter_process.start()

    streamer_process.join()
    detector_process.join()
    presenter_process.join()