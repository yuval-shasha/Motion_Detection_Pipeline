
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

    while True:
        ret, frame = captured_video.read()
        if not ret:
            out_conn.send("END")
            out_conn.close()
            break
        out_conn.send(frame)

def detector(in_conn, out_conn):
    count = 0
    prev_frame = None
    while True:
        if in_conn.poll():
            curr_frame = in_conn.recv()
            if curr_frame == "END":
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
                out_conn.send(curr_frame, detections)


def presenter(in_conn):
    print()

if __name__ == '__main__':
    """do main function"""