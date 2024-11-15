/*
 * sd_card_raw_library.h
 *
 *  @author Dawson Bancroft
 */

#ifndef SD_CARD_RAW_LIBRARY_SD_CARD_RAW_LIBRARY_H_
#define SD_CARD_RAW_LIBRARY_SD_CARD_RAW_LIBRARY_H_
extern unsigned int address_error;

// IF USING DIFFERENT PINS OR A DIFFERENT MICROCONTROLLER CHANGE THE NEXT 6 LINES
#include <msp430.h>

// CLOCK
#define SPI_CLK_PORT_DIR                P3DIR
#define SPI_CLK_PORT_OUT                P3OUT
#define SPI_CLK_PORT_IN                 P3IN
#define SPI_CLK_PORT_REN                P3REN
#define SPI_CLK                         BIT3

// CHIP SELECT
#define SPI_SEL_PORT_DIR                P3DIR
#define SPI_SEL_PORT_OUT                P3OUT
#define SPI_SEL_PORT_IN                 P3IN
#define SPI_SEL_PORT_REN                P3REN
#define SPI_SEL                         BIT0

// MOSI
#define SPI_MOSI_PORT_DIR               P3DIR
#define SPI_MOSI_PORT_OUT               P3OUT
#define SPI_MOSI_PORT_IN                P3IN
#define SPI_MOSI_PORT_REN               P3REN
#define SPI_MOSI                        BIT1

// MISO
#define SPI_MISO_PORT_DIR               P3DIR
#define SPI_MISO_PORT_OUT               P3OUT
#define SPI_MISO_PORT_IN                P3IN
#define SPI_MISO_PORT_REN               P3REN
#define SPI_MISO                        BIT2

// CARD DETECT
#define SPI_CD_PORT_DIR                 P3DIR
#define SPI_CD_PORT_OUT                 P3OUT
#define SPI_CD_PORT_IN                  P3IN
#define SPI_CD_PORT_REN                 P3REN
#define SPI_CD                          BIT0

// ANYTHING AFTER THIS SHOULD BE FINE

// FUNCTION DEFS
char sendByteSPI(char data);
void stopSPI(void);
void pulseClock(int num);
void sendDataSPI(unsigned char* buffer, unsigned int size);
void sendCommandWithoutPullingCSHigh(char cmd, long data, char crc);
void sendCommand(char cmd, long data, char crc, unsigned char* received);
void SPIInit(void);
void sdCardInit(void);
void sendData(unsigned long address, unsigned char* data);
void receiveData(unsigned long address, unsigned char* data);

#endif /* SD_CARD_RAW_LIBRARY_SD_CARD_RAW_LIBRARY_H_ */
