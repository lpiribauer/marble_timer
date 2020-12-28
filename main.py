from centroidtracker import CentroidTracker
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2

ct = CentroidTracker()
(H, W) = (None, None)
# initialize the video stream and allow the camera sensor to warmup
print("[INFO] starting video stream...")
cap = cv2.VideoCapture('2020-12-26-125652.webm')
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
time.sleep(2.0)
# loop over the frames from the video stream
backSub = cv2.createBackgroundSubtractorKNN()
backSub.setDetectShadows(False)
means = dict()
objects = None
while True:
    frame = cap.read()
    frame = frame[1]

    if frame is None:
        break
    frame = frame[0:600, 0:600, :3]
    display_frame = frame.copy()

    if W is None or H is None:
        (H, W) = frame.shape[:2]

    fgMask = backSub.apply(frame)
    fgMask = cv2.erode(fgMask, None, iterations=8)
    # cv2.imshow("fgMask", fgMask)
    cnts = cv2.findContours(fgMask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    rects = []
    if objects:
        lastObjects = objects.copy()
    else:
        lastObjects = None

    for i, c in enumerate(cnts):
        if cv2.contourArea(c) > 500:
            (x, y, w, h) = cv2.boundingRect(c)
            box = (x, y, x + w, y + h)
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            rects.append(box)
        # update our centroid tracker using the computed set of bounding
        # box rectangles
    objects = ct.update(rects)
    # loop over the tracked objects
    for (objectID, centroid) in objects.items():
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        area_size = 20
        text = "ID {} ".format(objectID)
        cv2.putText(display_frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(display_frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
        cv2.rectangle(display_frame, (centroid[0] - (area_size + 1) , centroid[1] - (area_size + 1)), (centroid[0] + (area_size + 1), centroid[1] + (area_size + 1)), (0, 0, 255), 1)
        mean_area = frame[centroid[1] - area_size : centroid[1] + area_size, centroid[0] - area_size : centroid[0] + area_size,  :3]
        cv2.imshow("area", mean_area)
        mean = cv2.mean(mean_area)
        if objectID in means:
            means[objectID].append(mean)
        else:
            means[objectID] = [mean]

    if lastObjects:
        for objectID in lastObjects:
            if objectID in objects:
                print(str(objectID) + " in frame")
            else:
                if (len(means[objectID]) > 3):
                    r = []
                    g = []
                    b = []
                    for m in means[objectID]:
                        g.append(m[0])
                        b.append(m[1])
                        r.append(m[2])
                    mean_r = np.mean(r)
                    mean_g = np.mean(g)
                    mean_b = np.mean(b)
                    object_mean = (mean_g, mean_b, mean_r)
                    color_img = np.zeros((60, 60, 3), np.uint8)
                    color_img[:] = (mean_g, mean_b, mean_r)
                    cv2.imshow("Color", color_img)


                    print(str(objectID) + " mean: " + str(object_mean))


    # show the output frame
    cv2.imshow("Frame", display_frame)
    key = cv2.waitKey(100) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
# do a bit of cleanup
cv2.destroyAllWindows()
cap.release()
