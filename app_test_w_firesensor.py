from flask import Flask, render_template, Response, request, jsonify
import cv2
from tplink_smartplug import SmartPlug

app = Flask(__name__)
app.config['SERVER_NAME'] = "raspberrypi.local:80"
camera_one = cv2.VideoCapture(0)
camera_two = cv2.VideoCapture(2)
plug = SmartPlug("192.168.1.158")
face_cascade=cv2.CascadeClassifier(r"/home/pi/Desktop/Fire_Detector/temp/classifier/cascade.xml")###path of cascade file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_outlet')
def check_status():
    info_json = {'plug': ''}
    if plug.is_on:
        info_json['plug'] = "on"
    else:
        info_json['plug'] = "off"
    return info_json

@app.route('/check_fire')
def check_fire():
    info_json = {'fire': ''}
    if fire():
        info_json['fire'] = "fire"
    else:
        info_json['fire'] = "nofire"
    return info_json
        
#detects fire in video image
def fire():
    #here is code to check the output
    ret, frame = camera_one.read()    
    resized = cv2.resize(frame,(400,200))
    gray=cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
    faces=face_cascade.detectMultiScale(gray,1.1,17)#try to tune this 6.5 and 17 parameter to get good result
    ##if not getting good result try to train new cascade.xml file again deleting other file expect p and n in temp folder
    for(x,y,w,h) in faces:
        return True
    return False

#background process happening without any refreshing
@app.route('/button_toggle')
def button_toggle():
    plug_tog_stat("TOGGLE")
    return ("nothing")

#toggles the plug on off
#eventually well add a plug
#parameter so it knows which
#plug to turn on/off
def plug_tog_stat(command):
    if command == "TOGGLE":
        if plug.is_on:
            plug.turn_off()
        else:
            plug.turn_on()
    elif command == "STATUS":
        if plug.is_on:
            return True
        else:
            return False

def gen_frames_one():  
    while True:
        success, frame = camera_one.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def gen_frames_two():  
    while True:
        success, frame = camera_two.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed_one')
def video_feed_one():
    return Response(gen_frames_one(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_two')
def video_feed_two():
    return Response(gen_frames_two(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()


