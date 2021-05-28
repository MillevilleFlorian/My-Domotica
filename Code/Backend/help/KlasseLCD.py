from RPi import GPIO
import time

DS = 22  # serial data
OE = 5  # output enable (active low)
STCP = 6  # storage register clock pulse
SHCP = 13  # shift register clock pulse
MR = 19  # master reset (active low)

DELAY = 0.001

class LCD:
    def __init__(self):
        self.E = 27
        self.RS = 17
        GPIO.setup([self.E,self.RS], GPIO.OUT)
        GPIO.output(self.E,GPIO.HIGH)
        self.ds_pin = DS
        self.shcp_pin = SHCP
        self.stcp_pin = STCP
        self.mr_pin = MR
        self.oe_pin = OE
        GPIO.setup([self.ds_pin, self.oe_pin, self.shcp_pin,
                    self.stcp_pin, self.mr_pin], GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(self.mr_pin, GPIO.HIGH)

    def write_bit(self, value):
        GPIO.output(DS, value)
        time.sleep(DELAY)
        GPIO.output(SHCP, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(DS, GPIO.LOW)
        GPIO.output(SHCP, GPIO.LOW)
        time.sleep(DELAY)

    def copy_to_storage_register(self):
        GPIO.output(STCP, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STCP, GPIO.LOW)
        time.sleep(DELAY)

    def write_byte(self, value):
        mask = 0x80
        for i in range(0, 8):
            if value & (mask >> i):
                self.write_bit(True)
            else:
                self.write_bit(False)

    @property
    def output_enabled(self):
        return not GPIO.input(self.oe_pin)

    @output_enabled.setter
    def output_enabled(self, value):
        GPIO.output(self.oe_pin, not value)

    def reset_shift_register(self):
        GPIO.output(self.mr_pin, GPIO.LOW)
        time.sleep(DELAY)
        GPIO.output(self.mr_pin, GPIO.HIGH)
        time.sleep(DELAY)

    def reset_storage_register(self):
        self.reset_shift_register()
        self.copy_to_storage_register()


    # ----------------------------

    def send_instruction(self,value):
        GPIO.output(self.RS, GPIO.LOW)
        self.write_byte(value)
        self.copy_to_storage_register()
        GPIO.output(self.E, GPIO.LOW)
        GPIO.output(self.E , GPIO.HIGH)
        time.sleep(DELAY)

    def send_character(self,value):
        GPIO.output(self.RS, GPIO.HIGH)
        self.write_byte(value)
        self.copy_to_storage_register()
        GPIO.output(self.E, GPIO.LOW)
        GPIO.output(self.E, GPIO.HIGH)
        time.sleep(DELAY)

    def send_message(self,message):
        self.send_instruction(0x1)
        leng = 0
        for char in message:
            leng += 1
            if leng > 16:
                bit_op = 0x80 | 0x40
                self.send_instruction(bit_op)
                self.send_character(ord(char))
                leng = 0
            else:
                self.send_character(ord(char))

    def init_LCD(self):
        self.send_instruction(0b00111000)  # function set
        self.send_instruction(0b00001111)  # display on
        self.send_instruction(0b00000001)  # clear display/cursor home
