#include <stdio.h>      //printf()
#include <stdlib.h>     //exit()
#include <signal.h>

 #include <stdio.h>
 #include <string.h>

#include "DEV_Config.h"
#include "L76X.h"

void  Handler(int signo)
{
    //System Exit
    printf("\r\nHandler:Program stop\r\n"); 

    DEV_ModuleExit();

    exit(0);
}

int main(int argc, char **argv)
{
    GNRMC GPS;
    Coordinates Baidu;
    
	if (DEV_ModuleInit()==1)return 1;
    // Exception handling:ctrl + c
    
    signal(SIGINT, Handler);

    DEV_Delay_ms(100); 
    DEV_Set_Baudrate(9600);
    DEV_Delay_ms(100);

    printf("Change the L76X output baud rate to 115200 \r\n");
    L76X_Send_Command(SET_NMEA_BAUDRATE_115200);
    DEV_Delay_ms(100);
    
    DEV_Delay_ms(100);
    DEV_Set_Baudrate(115200);
    DEV_Delay_ms(100);

    printf("Set the output data interval to 400ms\r\n");
    L76X_Send_Command(SET_POS_FIX_400MS);

    //Set output message
    L76X_Send_Command(SET_NMEA_OUTPUT);

    while(1){
        GPS = L76X_Gat_GNRMC();
        printf("\r\n");
        printf("Time: %d:%d:%d \r\n", GPS.Time_H, GPS.Time_M, GPS.Time_S);
        printf("Latitude and longitude: %lf  %c  %lf  %c\r\n", GPS.Lat, GPS.Lat_area, GPS.Lon, GPS.Lon_area);
        Baidu = L76X_Baidu_Coordinates();
        printf("Baudu Coordinates   %lf,%lf    \r\n", Baidu.Lat, Baidu.Lon);
    }
	DEV_ModuleExit();
    return 0; 
}
