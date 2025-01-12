# ------- Import Libraries ---------------------------------------------------------------------------------------------------
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import RPi.GPIO as GPIO
from time import sleep
import sys

class RspiServoControl():
    def __init__(self):
        self.x = None # Object center x
        self.y = None # Object center y

    def create_servo(self, pin_x,pin_y):
        factory = PiGPIOFactory() # Set up pigpio pin factory
        self.servo_x = AngularServo(pin_x, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)
        self.servo_y = AngularServo(pin_y, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)
        self.servo_x.angle = 0
        self.servo_y.angle = 0

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

        # GPIO config
        GPIO.setmode(GPIO.BOARD)
        for pin in self.motor_channel:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def move_motor(self,sequence):
        for step in sequence:
            for pin in range(4):
                GPIO.output(self.motor_channel[pin], step[pin])
            sleep(self.delay) # Time delay

    def kill(self):
        GPIO.cleanup()
        sys.exit(0)
