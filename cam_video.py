import numpy as np
import cv2
from dataclasses import dataclass

@dataclass
class VideoLimited:
	f: cv2.VideoWriter = cv2.VideoWriter()
	t: cv2.TickMeter = cv2.TickMeter()

cap = cv2.VideoCapture(0)
if (cap.isOpened() == False): 
	print("Unable to read camera feed")

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
 
cnt = 0
ff = cv2.VideoWriter(
	"full_video.avi",
	cv2.VideoWriter_fourcc('M','P','E','G'),
	10,
	(frame_width,frame_height)
)

v = VideoLimited()

while(True):
	v.t.start()
	if not v.f.isOpened():
		print("Opened")
		v.f.open(
			"short_video{}.avi".format(cnt),
			cv2.VideoWriter_fourcc('M','P','E','G'),
			10,
			(frame_width,frame_height)
		)
		cnt += 1
		v.t.reset()

	ret,frame = cap.read()

	frame = cv2.flip(frame, 1)
	cv2.imshow("Frame", frame)

	# write frame to short video
	if v.f.isOpened() and v.t.getTimeSec() < 10:
		v.f.write(frame)
	else:
		v.f.release()
		print("saved sort video file")

	# write frame to full video
	if ff.isOpened():
		ff.write(frame)

	ch = cv2.waitKey(1)
	if ch & 0xFF == ord('q'):
		break
	
	v.t.stop()

ff.release()
cap.release()
cv2.destroyAllWindows()
