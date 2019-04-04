/*****************************************************************************
* | File      	:   DEV_Config.c
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2018-12-19
* | Info        :

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#include "DEV_Config.h"

int fd;

/******************************************************************************
function:	
	Uart receiving and sending
******************************************************************************/
UBYTE DEV_Uart_ReceiveByte()
{ 
    return serialGetchar(fd);
}

void DEV_Uart_SendByte(char data)
{
    serialPutchar(fd, data);
}

void DEV_Uart_SendString(char *data)
{
    UWORD i;
    for(i = 0; data[i] != '\0'; i++){
        serialPutchar(fd, data[i]);
    }
    
}

void DEV_Uart_ReceiveString(char *data, UWORD Num)
{
    UWORD i;
    for(i = 0; i < Num-1; i++){
        data[i] = serialGetchar(fd);
    }
    data[i] = '\0';
}

/******************************************************************************
function:	
	Set the serial port baud rate
******************************************************************************/
void DEV_Set_Baudrate(UDOUBLE Baudrate)
{
    serialClose(fd);
    if((fd = serialOpen("/dev/ttyS0",Baudrate)) < 0){
        printf("set uart successfailed	!!! \r\n");
    }else{
        printf("set uart success  !!! \r\n");
    }  
}

void DEV_Set_GPIOMode( UWORD Pin, UWORD mode)
{
	if(mode == 1){
		pinMode(Pin, INPUT);
	}
	else if(mode == 0){
		pinMode(Pin, OUTPUT);
	}
}
/******************************************************************************
function:	
	Module initialization, BCM2835 library and initialization pins,
	uart
******************************************************************************/
UBYTE DEV_ModuleInit(void)
{
	if(wiringPiSetupGpio() < 0) { //use BCM2835 Pin number table
        printf("set wiringPi lib failed	!!! \r\n");
        return 1;
    } else {
        printf("set wiringPi lib success  !!! \r\n");
    }
	
    if((fd = serialOpen("/dev/ttyS0",115200)) < 0){
        return 1;
    }else {
        printf("set uart success  !!! \r\n");
    }

     pinMode(DEV_FORCE, INPUT);
     pinMode(DEV_STANDBY, OUTPUT);
    
     DEV_Digital_Write(DEV_STANDBY, 0);
	return 0;
}

/******************************************************************************
function:	
	Module exits
******************************************************************************/
void DEV_ModuleExit(void)
{

    serialFlush(fd);
    serialClose(fd);
    pinMode(DEV_FORCE, INPUT);
    pinMode(DEV_STANDBY, INPUT);
}


/************************************************/
