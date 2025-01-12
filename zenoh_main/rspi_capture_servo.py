# ------- Advise ---------------------------------------------------------------------------------------------------
#### Run ###
# sudo pigpiod

# ------- Import ---------------------------------------------------------------------------------------------------
import cv2
import json
import time
import zenoh
import socket
import imutils
import argparse
from email.policy import default
from imutils.video import VideoStream
from utils_main.utils_RSPI_dummy import*
# from utils_main.utils_RSPI import*

# ------- Parser ---------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(prog='z_raspi_capture_send.',description='video capture')
parser.add_argument('-s', '--sub', type=str, default='tcp/0.0.0.0:7441',
                    help='zenoh endpoints to listen on.')
parser.add_argument('-p', '--pub', type=str, default='tcp/0.0.0.0:7447',
                    help='zenoh endpoints to listen on.')
parser.add_argument('-ks', '--key_sub', type=str, default='drone/servo',
                    help='key sub expression')
parser.add_argument('-kp', '--key_pub', type=str, default='drone/frame',
                    help='key pub expression')
parser.add_argument('-d', '--delay', type=float, default=0.05,
                    help='delay between each frame in seconds')
parser.add_argument('-q', '--quality', type=int, default=95,
                    help='quality of the published frames (0 - 100)')
parser.add_argument('-w', '--width', type=int, default=500,
                    help='width of the published frames')
parser.add_argument('-pin', '--pins', type=str, default='2,3',
                    help='width of the published frames')
args = parser.parse_args()

# ------- Servo ---------------------------------------------------------------------------------------------------
rspi_tracker = RspiServoControl()
pin_x, pin_y = map(int, args.pins.split(','))
rspi_tracker.create_servo(pin_x, pin_y) # Create servo on pins

# ------- Motor Pas a Pas ---------------------------------------------------------------------------------------------------
pas_a_pas = MotorPasaPas()

# ------- Zenoh ---------------------------------------------------------------------------------------------------

# Zenoh SUB
def callback(sample: zenoh.Sample):
    x, y, d = map(float, sample.payload.decode('utf-8').split(','))
    rspi_tracker.adjust(x,y)
    if d == 1.0:
        for _ in range(10):
            pas_a_pas.move_motor(pas_a_pas.step_seq)
    elif d == -1.0:
        for _ in range(10):
            pas_a_pas.move_motor(pas_a_pas.step_seq[::-1])
    print(rspi_tracker.servo_x.angle, rspi_tracker.servo_y.angle, d)

conf = zenoh.Config()
conf.insert_json5(zenoh.config.MODE_KEY, json.dumps('peer'))
conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps([args.sub]))
print(f'[INFO] Open zenoh session at {args.sub} as SUB...')
zenoh.init_logger()
session = zenoh.open(conf) # open session
sub = session.declare_subscriber(args.key_sub, callback, reliability=zenoh.Reliability.RELIABLE()) # declare subscriber

# Zenoh PUB
conf = zenoh.Config()
conf.insert_json5(zenoh.config.MODE_KEY, json.dumps('peer'))
conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps([args.pub]))
print(f'[INFO] Open zenoh session at {args.pub} as PUB...')
zenoh.init_logger()
z = zenoh.open(conf)

# ------- Send Data ---------------------------------------------------------------------------------------------------
CAMERA_ID = 0
print('[INFO] Open camera...')
vs = VideoStream(src=CAMERA_ID).start()
jpeg_opts = [int(cv2.IMWRITE_JPEG_QUALITY), args.quality]
print(f'[INFO] All done. Endpoint at {socket.gethostbyname(socket.gethostname())}')

try:
    while True:

        # Frame preparation
        raw = vs.read()
        if raw is not None:
            frame = imutils.resize(raw, width=args.width)
            _, jpeg = cv2.imencode('.jpg', frame, jpeg_opts)
            z.put(args.key_pub, jpeg.tobytes())
        time.sleep(args.delay)
except:
    pass

# ------- EXIT ---------------------------------------------------------------------------------------------------
print('[INFO] Quiting ...')
rspi_tracker.kill() # Kill tra
sub.undeclare() # Quit zenoh
z.close()
pas_a_pas.kill() # Kill pas a pas
