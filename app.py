from flask import Flask, Response, render_template
import cv2
import argparse
import threading, os
from dataclasses import dataclass

@dataclass
class VideoLimited:
    f: cv2.VideoWriter = cv2.VideoWriter()
    t: cv2.TickMeter = cv2.TickMeter()

app = Flask(__name__)

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()

@app.route("/")
def index():
    return render_template("index.html")

def generate():
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                print("no frame")
                continue

            ok, image = cv2.imencode(".jpg", outputFrame)

            if not ok:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(image) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

def record_video(preview=True):
    global outputFrame, lock
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
        """
        if not v.f.isOpened():
            v.f.open(
                "short_video{}.avi".format(cnt),
                cv2.VideoWriter_fourcc('M','P','E','G'),
                10,
                (frame_width,frame_height)
            )
            cnt += 1
            v.t.reset()
"""
        ret,frame = cap.read()

        frame = cv2.flip(frame, 1)


        if preview:
            cv2.imshow("Frame", frame)
        with lock:
            if frame:
                outputFrame = frame.copy()
            """
        # write frame to short video
        if v.f.isOpened() and v.t.getTimeSec() < 10:
            v.f.write(frame)
        else:
            v.f.release()
            print("saved sort video file")

        # write frame to full video
        if ff.isOpened():
            ff.write(frame)
"""
        ch = cv2.waitKey(1)
        if ch & 0xFF == ord('q'):
            ff.release()
            cap.release()
            cv2.destroyAllWindows()
            
            os._exit(1)

        v.t.stop()



def main():
    ap = argparse.ArgumentParser()
    #ap.add_argument("-h", "--host", type=str)
    #ap.add_argument("-p", "--port", type=int)
    #ap.add_argument("-f", "--frame", type=int)
    ap.add_argument("-P", "--preview", action='store_true')
    args = vars(ap.parse_args())
    
    print("{}".format(args["preview"]))
    t = threading.Thread(target=record_video,args=(args["preview"],))
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port="5000", debug=True,
            threaded=True, use_reloader=False)
    print(" * Recording video (Press 'q' to quit)")


if __name__ == "__main__":
    main()

