#include <msp430.h> 
#include <sd_card_raw_library.h>

// Globals
unsigned long address_cnt = 0x00; // CNT for address of microSD       //temp to test values


int main(void)
{
    WDTCTL = WDTPW | WDTHOLD;   // stop watchdog timer

    // for SD Card
    SPIInit();                                          // Initialize SPI Ports

    PM5CTL0 &= ~LOCKLPM5;

    // for SD Card
    sdCardInit();                                       // Send Initialization Commands to SD Card
    unsigned char dataIn[6];
    sendCommand(0x50, 0x200, 0xFF, dataIn);             // CMD 16 : Set Block Length
    unsigned char sd_buffer[512];                       // buffer for SD card

    unsigned int i;
    for(i=0;i<512;i++){                                 // initalize with 0s
        sd_buffer[i] = i;
    }

    while(1)
    {
        sendData(address_cnt, sd_buffer);
        address_cnt++;
        __delay_cycles(10000);     // may need to increase (50000 originally)
        sendCommand(0x4D, 0, 0, dataIn);
        sendCommand(0x4D, 0, 0, dataIn);
        __delay_cycles(10000);    // this one too

        //for(i=0; i<32768; i++){}  // delay 1 second
        __delay_cycles(1000000);
        }

    return 0;
}
