import RPi.GPIO as GPIO
import config
import math
import time
from micropyGPS import MicropyGPS

g = MicropyGPS(+8)

Temp = '0123456789ABCDEF*'
BUFFSIZE = 1100


pi = 3.14159265358979324
a = 6378245.0
ee = 0.00669342162296594323
x_pi = 3.14159265358979324 * 3000.0 / 180.0


class L76X(object):
    Lon = 0.0
    Lat = 0.0
    Lon_area = 'E'
    Lat_area = 'W'
    Time_H = 0
    Time_M = 0
    Time_S = 0
    Status = 0
    Lon_Baidu = 0.0
    Lat_Baidu = 0.0
    Lon_Google = 0.0
    Lat_Google = 0.0
    
    GPS_Lon = 0
    GPS_Lat = 0
    
    #Startup mode
    SET_HOT_START       = '$PMTK101'
    SET_WARM_START      = '$PMTK102'
    SET_COLD_START      = '$PMTK103'
    SET_FULL_COLD_START = '$PMTK104'

    #Standby mode -- Exit requires high level trigger
    SET_PERPETUAL_STANDBY_MODE      = '$PMTK161'

    SET_PERIODIC_MODE               = '$PMTK225'
    SET_NORMAL_MODE                 = '$PMTK225,0'
    SET_PERIODIC_BACKUP_MODE        = '$PMTK225,1,1000,2000'
    SET_PERIODIC_STANDBY_MODE       = '$PMTK225,2,1000,2000'
    SET_PERPETUAL_BACKUP_MODE       = '$PMTK225,4'
    SET_ALWAYSLOCATE_STANDBY_MODE   = '$PMTK225,8'
    SET_ALWAYSLOCATE_BACKUP_MODE    = '$PMTK225,9'

    #Set the message interval,100ms~10000ms
    SET_POS_FIX         = '$PMTK220'
    SET_POS_FIX_100MS   = '$PMTK220,100'
    SET_POS_FIX_200MS   = '$PMTK220,200'
    SET_POS_FIX_400MS   = '$PMTK220,400'
    SET_POS_FIX_800MS   = '$PMTK220,800'
    SET_POS_FIX_1S      = '$PMTK220,1000'
    SET_POS_FIX_2S      = '$PMTK220,2000'
    SET_POS_FIX_4S      = '$PMTK220,4000'
    SET_POS_FIX_8S      = '$PMTK220,8000'
    SET_POS_FIX_10S     = '$PMTK220,10000'

    #Switching time output
    SET_SYNC_PPS_NMEA_OFF   = '$PMTK255,0'
    SET_SYNC_PPS_NMEA_ON    = '$PMTK255,1'

    #To restore the system default setting
    SET_REDUCTION               = '$PMTK314,-1'

    #Set NMEA sentence output frequencies 
    SET_NMEA_OUTPUT = '$PMTK314,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,0'
    #Baud rate
    SET_NMEA_BAUDRATE          = '$PMTK251'
    SET_NMEA_BAUDRATE_115200   = '$PMTK251,115200'
    SET_NMEA_BAUDRATE_57600    = '$PMTK251,57600'
    SET_NMEA_BAUDRATE_38400    = '$PMTK251,38400'
    SET_NMEA_BAUDRATE_19200    = '$PMTK251,19200'
    SET_NMEA_BAUDRATE_14400    = '$PMTK251,14400'
    SET_NMEA_BAUDRATE_9600     = '$PMTK251,9600'
    SET_NMEA_BAUDRATE_4800     = '$PMTK251,4800'

    def __init__(self):
        self.config = config.config(9600)
    
    def L76X_Send_Command(self, data):
        Check = ord(data[1]) 
        for i in range(2, len(data)):
            Check = Check ^ ord(data[i]) 
        data = data + Temp[16]
        data = data + Temp[(Check//16)]
        data = data + Temp[(Check%16)]
        self.config.Uart_SendString(data.encode())
        self.config.Uart_SendByte('\r'.encode())
        self.config.Uart_SendByte('\n'.encode())
        print (data)
        
    def L76X_Gat_GNRMC(self):
        data=''
        while 1:
            if g.valid:
                self.Status = 1
            else:
                self.Status = 0
            x=self.config.Uart_ReceiveByte()
            if x==b'$':
                while (x!=b'\r'):
                    data+=x.decode()
                    g.update(x.decode())
                    x=self.config.Uart_ReceiveByte()
                data+='\r\n'
                if '$GNGLL' in data:
                    break
        self.Lat=g.latitude[0]+g.latitude[1]/100
        self.Lon=g.longitude[0]+g.longitude[1]/100
        if g.latitude[2]!='N':
            self.Lat=self.Lat*(-1)
        if g.longitude[2]!='E':
            self.Lon=self.Lon*(-1)
        self.Time_H = g.timestamp[0]
        self.Time_M = g.timestamp[1]
        self.Time_S = g.timestamp[2]
        print(data)
        data='\r\n'

    def  transformLat(self, x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 *math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * pi) + 40.0 * math.sin(y / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * pi) + 320 * math.sin(y * pi / 30.0)) * 2.0 / 3.0
        return ret

    def transformLon(self, x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * pi) + 40.0 * math.sin(x / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * pi) + 300.0 * math.sin(x / 30.0 * pi)) * 2.0 / 3.0
        return ret

    def bd_encrypt(self):
        x = self.Lon_Goodle
        y = self.Lat_Goodle
        z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi)
        self.Lon_Baidu = z * math.cos(theta) + 0.0065
        self.Lat_Baidu = z * math.sin(theta) + 0.006

    def transform(self):
        dLat = self.transformLat(self.GPS_Lon - 105.0, self.GPS_Lat - 35.0)
        dLon = self.transformLon(self.GPS_Lon - 105.0, self.GPS_Lat - 35.0)
        radLat = self.GPS_Lat / 180.0 * pi
        magic = math.sin(radLat)
        magic = 1 - ee * magic * magic
        math.sqrtMagic = math.sqrt(magic)
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * math.sqrtMagic) * pi)
        dLon = (dLon * 180.0) / (a / math.sqrtMagic * math.cos(radLat) * pi)
        self.Lat_Goodle = self.GPS_Lat + dLat
        self.Lon_Goodle = self.GPS_Lon + dLon

    def L76X_Baidu_Coordinates(self, U_Lat, U_Lon):
        self.GPS_Lat = U_Lat % 1 *100 / 60 + math.floor(U_Lat)
        self.GPS_Lon = U_Lon % 1 *100 / 60 + math.floor(U_Lon)
        self.transform()
        self.bd_encrypt()

    def L76X_Google_Coordinates(self, U_Lat, U_Lon):
        self.GPS_Lat = U_Lat % 1 / 60 + U_Lat/1
        self.GPS_Lon = U_Lon % 1 / 60 + U_Lon/1
        self.transform()

    def L76X_Set_Baudrate(self, Baudrate):
        self.config.Uart_Set_Baudrate(Baudrate)

    def L76X_Exit_BackupMode(self):
        GPIO.setup(self.config.FORCE, GPIO.OUT)
        time.sleep(1)
        GPIO.output(self.config.FORCE, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.config.FORCE, GPIO.LOW)
        time.sleep(1)
        GPIO.setup(self.config.FORCE, GPIO.IN)


    



