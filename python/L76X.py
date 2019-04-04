import RPi.GPIO as GPIO
import config
import math
import time

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
    Lon_Goodle = 0.0
    Lat_Goodle = 0.0
    
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
        data = data + Temp[(Check/16)]
        data = data + Temp[(Check%16)]
        self.config.Uart_SendString(data)
        self.config.Uart_SendByte('\r')
        self.config.Uart_SendByte('\n')
        print data
        
    def L76X_Gat_GNRMC(self):
        data = self.config.Uart_ReceiveString(BUFFSIZE)
        print data
        print '\n'
        add=0
        self.Status = 0
        for i in range(0, BUFFSIZE-71):
            if(ord(data[add]) == 36 and ord(data[add+1]) == 71 and (ord(data[add+2]) == 78 \
            or ord(data[add+2]) == 80) and ord(data[add+3]) == 82 and ord(data[add+4]) == 77\
            and ord(data[add+5]) == 67):
                    x = 0
                    z = 0
                    while(x < 12):
                        if(add+z >= BUFFSIZE-1):
                            return
                        if(ord(data[add+z]) == 44):#,
                            x = x + 1
                            if(x == 1):
                                Time = 0
                                for k in range(0, BUFFSIZE-1):
                                    if(add+z+k >= BUFFSIZE-1):
                                        return
                                    if(ord(data[add+z+k+1]) == 44):#,
                                        break
                                    if(ord(data[add+z+k+1]) == 46):#.
                                        break
                                    Time = (ord(data[add+z+k+1]) - 48) + Time*10
                                self.Time_H = Time/10000 + 8
                                self.Time_M = Time/100%100
                                self.Time_S = Time%100
                                if(self.Time_H >= 24):
                                     self.Time_H =  self.Time_H - 24
                            elif(x == 2):
                                if(ord(data[add+z+1]) == 65):#A
                                    self.Status = 1
                                else:
                                    self.Status = 0
                            elif(x == 3):
                                latitude = 0
                                for k in range(0, BUFFSIZE-1):
                                    if(add+z+k >= BUFFSIZE-1):
                                        return
                                    if(ord(data[add+z+k+1]) == 44):#,
                                        break
                                    if(ord(data[add+z+k+1]) == 46):#.
                                        continue
                                    latitude = (ord(data[add+z+k+1]) - 48) + latitude*10
                                self.Lat = latitude / 1000000.0
                            elif(x == 4):
                                self.Lat_area = data[add+z+1]
                            elif(x == 5):
                                longitude = 0
                                for k in range(0, BUFFSIZE-1):
                                    if(add+z+k >= BUFFSIZE-1):
                                        return
                                    if(ord(data[add+z+k+1]) == 44):#,
                                        break
                                    if(ord(data[add+z+k+1]) == 46):#.
                                        continue
                                    longitude = (ord(data[add+z+k+1]) - 48) + longitude*10
                                
                                self.Lon = longitude / 1000000.0
                            elif(x == 6):
                                self.Lon_area = data[add+z+1]
                                return#Completion calculation
                        z = z + 1
            add = add + 1

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


    



