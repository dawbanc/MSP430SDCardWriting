# MSP430RawSD
 Writing to a SD card with an MSP430 then reading it on Windows!
 
 # MSP430 Side
 The files in this repository under MSP430FR2355Software are able to write to an SD card in raw data. It will also has an example of code to be able to write the register addresses for each block. It will work on other MSP430FRs along with other MSP430's with a little changes in the header file.
 
 # Windows Side
 The SD card can then be inserted into a Windows (or Linux) machine. Then a configuration file can be created to read the SD card values into a CSV file. You can even do math between several cells and have configuration data in the first block on the SD card.
 
 # Action Items
- [ ] Add an installer for the GUI
- [ ] Get a pure Windows SD Card reading process
