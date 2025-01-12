# ------- Import Libraries ---------------------------------------------------------------------------------------------------
from gpiozero import Device, AngularServo
from gpiozero.pins.mock import MockPWMPin, MockFactory
from time import sleep

class RspiServoControl():
    def __init__(self):
        self.x = None # Object center x
        self.y = None # Object center y

    def create_servo(self, pin_x,pin_y):
        Device.pin_factory = MockFactory(pin_class=MockPWMPin) # Config mock pin factory
        self.servo_x = AngularServo(pin_x) # Servo x axis
        self.servo_y = AngularServo(pin_y) # Servo Y axis
        self.servo_x.angle = 0 # Initial angle
        self.servo_y.angle = 0 # Initial angle

    def adjust(self,x,y):
        self.servo_x.angle = max(-90,min(90,int(x)))
        self.servo_y.angle = max(-90,min(90,int(y)))

    def kill(self):
        self.servo_x.detach
        self.servo_x.close()
        self.servo_y.detach
        self.servo_y.close()

class MotorPasaPas():
    def __init__(self, motor_channel = [35, 36, 37, 38], delay = 0.0007):
        self.step_seq = [
                    [1, 0, 0, 0],
                    [1, 1, 0, 0],
                    [0, 1, 0, 0],
                    [0, 1, 1, 0],
                    [0, 0, 1, 0],
                    [0, 0, 1, 1],
                    [0, 0, 0, 1],
                    [1, 0, 0, 1]
                    ]
        self.motor_channel = motor_channel
        self.delay = delay

    def move_motor(self,sequence):
        for step in sequence:
            sleep(self.delay) # Time delay

    def kill(self):
        pass