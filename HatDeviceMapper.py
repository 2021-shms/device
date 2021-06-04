#import Message
import RPi.GPIO as gpio
import time
import subprocess
from datetime import datetime
from SX127x.LoRa import *
from gps3 import agps3
from gps import *
#from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

BOARD.setup()
BOARD.reset()

class HatDeviceMapper(LoRa):
    def __init__(self, verbose=False):
        super(HatDeviceMapper, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.var=0
        
        #lora = mylora(verbose=False)
        #args = parser.parse_args(lora) # configs in LoRaArgumentParser.py

        #     Slow+long range  Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. 13 dBm
        self.set_pa_config(pa_select=1, max_power=21, output_power=15)
        self.set_bw(BW.BW125)
        self.set_coding_rate(CODING_RATE.CR4_8)
        self.set_spreading_factor(12)
        self.set_rx_crc(True)
        #lora.set_lna_gain(GAIN.G1)
        #lora.set_implicit_header_mode(False)
        self.set_low_data_rate_optim(True)
        
    def on_rx_done(self):
        BOARD.led_on()
        #print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print ("Receive: ")
        print(bytes(payload).decode("utf-8",'ignore')) # Receive DATA
        BOARD.led_off()
        time.sleep(2) # Wait for the client be ready
        print ("Send: ACK")
        self.write_payload([255, 255, 0, 0, 65, 67, 75, 0]) # Send ACK
        self.set_mode(MODE.TX)
        self.var=1

    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())
    
    def getCardInfo(self):
        fd_popen = subprocess.Popen("nfc-poll", stdout=subprocess.PIPE).stdout
        data = fd_popen.read().strip()

        start = str(data).find("UID (NFCID1):")

        uid = str(data)[start + 13 :start + 29]
        uid = uid.replace(" ", "")

        print('UID : ', uid)
        
        return uid
        
    def getLocation(self, new_data):
        data_stream = agps3.DataStream()
        data_stream.unpack(new_data)
        print('longitude = ', data_stream.lon)
        print('Latitude = ', data_stream.lat)
        lat = str(data_stream.lat)
        lon = str(data_stream.lon)
                
        location = []
        location.append(lat)
        location.append(lon)
        print(location)
                
        return location
    
    def getWear(self):
        gpio.setmode(gpio.BCM)

        trig = 13
        echo = 19

        gpio.setup(trig, gpio.OUT)
        gpio.setup(echo, gpio.IN)

        gpio.output(trig, False)
        time.sleep(0.5)
        
        gpio.output(trig, True)
        time.sleep(0.00001)
        gpio.output(trig, False)
        
        while gpio.input(echo) == 0 :
            pulse_start = time.time()

        while gpio.input(echo) == 1 :
            pulse_end = time.time()
            
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17000
        distance = round(distance, 2)
                            
        if distance > 13 and distance < 2000:
            isWear = "N"
        else:
            isWear = "Y"
        
        print ("Distance : ", distance, "cm")
        
        return isWear
    
    def setLED(self, state):
        if state:
            #on
            print("on")
            gpio.setup(12, gpio.OUT)
            
            gpio.output(12, True)
        else:
            #off
            print("off")
            gpio.setup(12, gpio.OUT)
            
            gpio.cleanup(12)
    
    def sendHatInfo(self, data):
        message = []
        for i in range(0, len(data)):
            message.append(ord(data[i]))
        self.write_payload(message)
        self.set_mode(MODE.TX)
        
    def sleep(self):
        self.set_mode(MODE.SLEEP)
        BOARD.teardown()


