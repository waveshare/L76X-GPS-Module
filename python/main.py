import L76X
import time
import math

try:
    x=L76X.L76X()
    x.L76X_Set_Baudrate(9600)
    x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
    time.sleep(2)
    x.L76X_Set_Baudrate(115200)

    x.L76X_Send_Command(x.SET_POS_FIX_400MS);

    #Set output message
    x.L76X_Send_Command(x.SET_NMEA_OUTPUT);

    x.L76X_Exit_BackupMode();
    while(1):
        x.L76X_Gat_GNRMC()
        if(x.Status == 1):
            print 'Already positioned'
        else:
            print 'No positioning'
        print 'Time %d:'%x.Time_H,
        print '%d:'%x.Time_M,
        print '%d'%x.Time_S

        print 'Lon = %f'%x.Lon,
        print ' Lat = %f'%x.Lat
        x.L76X_Baidu_Coordinates(x.Lat, x.Lon)
        print 'Baidu coordinate %f'%x.Lat_Baidu,
        print ',%f'%x.Lon_Baidu
except:
    #GPIO.cleanup()
    print "\nProgram end"
    exit()