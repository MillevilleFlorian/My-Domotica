from RPi import GPIO
import spidev

global spi


class SPi:
    def __init__(self, bus=0, device=0):
        global spi
        self.bus = bus
        self.device = device
        spi = spidev.SpiDev()

    def read_bytes(self, channel):
        global spi
        spi.open(self.bus, self.device)
        spi.max_speed_hz = 10 ** 5  # 100 kHz
        bytes_in = spi.xfer2([1, (8 | channel) << 4, 0])
        bit2 = bytes_in[1]
        bit3 = bytes_in[2]
        data = ((bit2 & 3) << 8) | bit3
        return data

    def closespi(self):
        global spi
        spi.close()
