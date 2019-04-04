#include "L76X.h"

char const Temp[16]={'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};

static const double pi = 3.14159265358979324;
static const double a = 6378245.0;
static const double ee = 0.00669342162296594323;
static const double x_pi = 3.14159265358979324 * 3000.0 / 180.0;

static char buff_t[BUFFSIZE]={0};

GNRMC GPS;

/******************************************************************************
function:	
	Latitude conversion
******************************************************************************/
static double transformLat(double x,double y)
{
	double ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 *sqrt(abs(x));
    ret += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0;
    ret += (20.0 * sin(y * pi) + 40.0 * sin(y / 3.0 * pi)) * 2.0 / 3.0;
    ret += (160.0 * sin(y / 12.0 * pi) + 320 * sin(y * pi / 30.0)) * 2.0 / 3.0;
    return ret;
}

/******************************************************************************
function:	
	Longitude conversion
******************************************************************************/
static double transformLon(double x,double y)
{
	double ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(abs(x));
    ret += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0;
    ret += (20.0 * sin(x * pi) + 40.0 * sin(x / 3.0 * pi)) * 2.0 / 3.0;
    ret += (150.0 * sin(x / 12.0 * pi) + 300.0 * sin(x / 30.0 * pi)) * 2.0 / 3.0;
    return ret;
}

/******************************************************************************
function:	
	GCJ-02 international standard converted to Baidu map BD-09 standard
******************************************************************************/
static Coordinates bd_encrypt(Coordinates gg)
{
	Coordinates bd;
    double x = gg.Lon, y = gg.Lat;
	double z = sqrt(x * x + y * y) + 0.00002 * sin(y * x_pi);
	double theta = atan2(y, x) + 0.000003 * cos(x * x_pi);
	bd.Lon = z * cos(theta) + 0.0065;
	bd.Lat = z * sin(theta) + 0.006;
	return bd;
}

/******************************************************************************
function:	
	GPS's WGS-84 standard is converted into GCJ-02 international standard
******************************************************************************/
static Coordinates transform(Coordinates gps)
{
	Coordinates gg;
    double dLat = transformLat(gps.Lon - 105.0, gps.Lat - 35.0);
    double dLon = transformLon(gps.Lon - 105.0, gps.Lat - 35.0);
    double radLat = gps.Lat / 180.0 * pi;
    double magic = sin(radLat);
    magic = 1 - ee * magic * magic;
    double sqrtMagic = sqrt(magic);
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * pi);
    dLon = (dLon * 180.0) / (a / sqrtMagic * cos(radLat) * pi);
    gg.Lat = gps.Lat + dLat;
    gg.Lon = gps.Lon + dLon;
	return gg;
}

/******************************************************************************
function:	
	Send a command to the L76X，Automatic calculation of the code
parameter:
    data ：The end of the command ends with ‘\0’ or it will go wrong, 
           no need to increase the validation code.
******************************************************************************/
void L76X_Send_Command(char *data)
{
    char Check = data[1], Check_char[3]={0};
    UBYTE i = 0;
    //printf(" 1i = %d Check =%x \n", i, Check);
    for(i=2; data[i] != '\0'; i++){
        Check ^= data[i];       //Calculate the check value
    }
    //printf(" i = %d Check =%x \n", i, Check);
    Check_char[0] = Temp[Check/16%16];
    Check_char[1] = Temp[Check%16];
		Check_char[2] = '\0';
    
    DEV_Uart_SendString(data);
    DEV_Uart_SendByte('*');
    DEV_Uart_SendString(Check_char);
    DEV_Uart_SendByte('\r');
    DEV_Uart_SendByte('\n');
    DEV_Delay_ms(200);
}


/******************************************************************************
function:	
	Analyze GNRMC data in L76x, latitude and longitude, time
******************************************************************************/
GNRMC L76X_Gat_GNRMC()
{
    UWORD add = 0, x = 0, z = 0, i = 0;
    UDOUBLE Time = 0, latitude = 0, longitude = 0;

    GPS.Status = 0;

	GPS.Time_H = 0;
    GPS.Time_M = 0;
    GPS.Time_S = 0;
	
    DEV_Uart_ReceiveString(buff_t, BUFFSIZE);
    printf("%s\r\n", buff_t);
    add = 0; 
    while(add < BUFFSIZE-71){
        if(buff_t[add] == '$' && buff_t[add+1] == 'G' && (buff_t[add+2] == 'N' || buff_t[add+2] == 'P')\
            && buff_t[add+3] == 'R' && buff_t[add+4] == 'M' && buff_t[add+5] == 'C'){
            x = 0;
            for(z = 0; x < 12; z++){
                if(buff_t[add+z]=='\0'){
                    break;
                }
                if(buff_t[add+z]==','){
                    x++;
                    if(x == 1){//The first comma is followed by time
                        Time = 0;
                        for(i = 0; buff_t[add+z+i+1] != '.'; i++){
                            if(buff_t[add+z+i+1]=='\0'){
                                break;
                            }   
                            if(buff_t[add+z+i+1] == ',')
                                break;
                            Time = (buff_t[add+z+i+1]-'0') + Time*10;
                        }
                        
                        GPS.Time_H = Time/10000+8;
                        GPS.Time_M = Time/100%100;
                        GPS.Time_S = Time%100;
                        if(GPS.Time_H >= 24)
                            GPS.Time_H = GPS.Time_H - 24;
                    }else if(x == 2){
                     //A indicates that it has been positioned
                     //V indicates that there is no positioning.
                        if(buff_t[add+z+1] == 'A'){
                             GPS.Status = 1;
                        }else{
                             GPS.Status = 0;
                        }
                    }else if(x == 3){
                        latitude = 0;
                        //If you need to modify, please re-edit the calculation method below.
                        for(i = 0; buff_t[add+z+i+1] != ','; i++){
                            if(buff_t[add+z+i+1] == '\0'){
                                break;
                            } 
                            if(buff_t[add+z+i+1] == '.'){
                                continue;
                            }
                            latitude = (buff_t[add+z+i+1]-'0') + latitude*10;
                        }
                        GPS.Lat = latitude/1000000.0;
                    }else if(x == 4){
                        GPS.Lat_area = buff_t[add+z+1];
                    }
                    else if(x == 5){
                        longitude = 0;
                        for(i = 0; buff_t[add+z+i+1] != ','; i++){
                            if(buff_t[add+z+i+1] == '\0'){
                                break;
                            } 
                            if(buff_t[add+z+i+1] == '.')
                                continue;
                            longitude = (buff_t[add+z+i+1]-'0') + longitude*10;
                        }
                        GPS.Lon = longitude/1000000.0;
                    }else if(x == 6){
                        GPS.Lon_area = buff_t[add+z+1];
                    }
                }
            }
            add = 0;
            break;
        }
        if(buff_t[add+5] == '\0'){
            add = 0;
						break;
        }
        add++;
        if(add > BUFFSIZE){
            add = 0;
            break;
        }
    }
    return GPS;
}

/******************************************************************************
function:	
	Convert GPS latitude and longitude into Baidu map coordinates
******************************************************************************/
Coordinates L76X_Baidu_Coordinates()
{
    Coordinates temp;
    temp.Lat =((int)(GPS.Lat)) + (GPS.Lat - ((int)(GPS.Lat)))*100 / 60;
    temp.Lon =((int)(GPS.Lon)) + (GPS.Lon - ((int)(GPS.Lon)))*100 / 60;
    temp = transform(temp);
    temp = bd_encrypt(temp);
    return temp;
}

/******************************************************************************
function:	
	Convert GPS latitude and longitude into Google Maps coordinates
******************************************************************************/
Coordinates L76X_Google_Coordinates()
{
    Coordinates temp;
    GPS.Lat =((int)(GPS.Lat)) + (GPS.Lat - ((int)(GPS.Lat)))*100 / 60;
    GPS.Lon =((int)(GPS.Lon)) + (GPS.Lon - ((int)(GPS.Lon)))*100 / 60;
    temp = transform(temp);
    return temp;
}
