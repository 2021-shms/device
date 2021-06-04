import HatDeviceMapper
import sys
import time
from configparser import ConfigParser
from datetime import datetime
from gps import *
from gps3 import agps3
import json

class HatDeviceService:
    hatDeviceMapper = HatDeviceMapper.HatDeviceMapper()
    
    def getCode(self):
        properties = ConfigParser()
        properties.read('config.ini')
        
        code = properties["CODE"]
        
        return code["code"]
    
    def getCardInfo(self):
        return self.hatDeviceMapper.getCardInfo()
    
    def getLocation(self, new_data):
        return self.hatDeviceMapper.getLocation(new_data)
    
    def getWear(self):
        return self.hatDeviceMapper.getWear()
    
    def setLED(self, state):
        self.hatDeviceMapper.setLED(state)
        
    def sendHatInfo(self, message):        
        self.hatDeviceMapper.sendHatInfo(message)
    
    def sleep(self):
        self.hatDeviceMapper.sleep()

gps_socket = agps3.GPSDSocket()
gps_socket.connect()
gps_socket.watch()

try:
    hatDeviceService = HatDeviceService()
    cardInfo = ""
    hatCode = hatDeviceService.getCode()
    
    hatDeviceService.setLED(True)
    while (True):
        newCardInfo = hatDeviceService.getCardInfo()
        
        if (len(newCardInfo) == 8 and cardInfo == ""):
            hatDeviceService.setLED(False)
            cardInfo = newCardInfo
            newCardInfo = ""
            
        if (newCardInfo != cardInfo):
            print("send Start")
            for new_data in gps_socket:
                if new_data:
            
                    #location = hatDeviceService.getLocation(new_data)
                    data_stream = agps3.DataStream()
                    data_stream.unpack(new_data)
                    print('longitude = ', data_stream.lon)
                    print('Latitude = ', data_stream.lat)
                    #lat = str(data_stream.lat)
                    #lon = str(data_stream.lon)
                    lat = data_stream.lat
                    lon = data_stream.lon
                    
                    if data_stream.lat is None or data_stream.lat > 38.45000000 or data_stream.lat < 33.10000000 or data_stream.lon is None or data_stream.lon > 131.87222222 or data_stream.lon < 125.06666667:
                        continue
                    
                    location = []
                    location.append(lat)
                    location.append(lon)
                    
                    if (location[0] > 0.0 and location[1] > 0.0): 
                    #if ((data_stream.lat <= 38.45000000) and (data_stream.lat >= 33.10000000) and (data_stream.lon <= 131.87222222) and (data_stream.lon >= 125.06666667)):
                        isWear = hatDeviceService.getWear()
                
                        now = datetime.now()
                        now_time = str(now)
                        now_time = now_time.split('.')[0].replace(" ", "T")
                
                        message = []
                        message.append(hatCode)
                        message.append("/")
                        message.append(cardInfo)
                        message.append("/")
                        message.append(str(location[0]))
                        message.append("/")
                        message.append(str(location[1]))
                        message.append("/")
                        message.append(now_time)
                        message.append("/")
                        message.append(isWear)
                        messageStr = "".join(message)
                        print(messageStr)
                
                        hatDeviceService.sendHatInfo(messageStr)
                break;
        elif (newCardInfo == cardInfo):
            #end
            hatDeviceService.setLED(True)
            cardInfo = ""
            newCardInfo = ""

except KeyboardInterrupt:
    sys.stdout.flush()
    print("Exit")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    hatDeviceService.sleep()
    print("Exit")