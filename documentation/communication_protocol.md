# Lily System™ Communication Protocol

This document describes the communication protocol for the Lily System™.
This protocol works with the LS-1400 (see: https://lilytronics.nl/lily-system).


## Connection

The Lily System™ works with an RS485 two wire bus.
The bus is equipped with proper termination and biasing.
The bus can work with most USB to RS485 converters (like FTDI USB-RS485).
The communication module from LilyTronics (LS-CM) is provided with such an interface.
The following settings apply:

| Parameter    | Value   |
|--------------|---------|
| Baud rate    | 1 MBaud |
| Data bits    | 8       |
| Parity       | None    |
| Stop bits    | 1       |
| Flow control | Off     |

With the given speed sending one byte takes 10us.
A maximum speed of 100000 bytes per second can be reached.


## Slot numbers

The modules in the rack are identified by their slot number. The most left is slot number 1.
Next to that is number 2 and so on. At the most right is the final slot number 9.
Per rack 9 modules can be addressed using their slot number.
There are two reserved slot numbers: 0 and 255 (0xFF).
Slot number 0 is reserver for the PC. Slot number 255 is the wildcard slot number.
This is used to send a command to all the modules in the rack.


## Packet format

The packet has the following format:

```
<STX><DSN><SSN><PID><DATA><CRC><ETX>
```

The fields are described in the table below.

| Field | Bytes  | Description                                                                |
|-------|--------|----------------------------------------------------------------------------|
| STX   | 1      | Start of packet: always 0x02.                                              |
| DSN   | 1      | Destination slot number.                                                   |
| SSN   | 1      | Source slot number.                                                        |
| PID   | 2      | Packet ID. Start at 0x0001. When 0xFFFF is reached, wrap around to 0x0001. |
| DATA  | 1...35 | Data bytes.                                                                |
| CRC   | 1      | 8 bit CRC with polynome 0x07.                                              |
| ETX   | 1      | End of packet: always 0x04.                                                |

The packet size can vary between 8 and 42 bytes (including STX and ETX).
The CRC is calculated over the fields: DSN, SSN, PID and DATA.

When sending DSN, SSN, PID and DATA, the values 0x02 and 0x04 can occur.
If these values are send the communication will fail, because there will be a confusion.
Example: sending data 0x04 to slot 2 will look like this:

```
0x02 0x02 0x00 0x00 0x01 0x04 CRC 0x04
```

There are two things confusing: where the packet starts and where it ends.
To prevent this confusing byte stuffing is applied to a packet when sending.

This means that whenever STX or ETX is being sent as a value in the packet,
they are replaced by a special sequence: DLE (0x20) following by the inverted value of the byte.
This means that if DLE is found in the data, this also must be replaced.
The following table shows the byte stuffing:

| Value to send | Values being send |
|---------------|-------------------|
| 0x02 (STX)    | 0x20 0xFD         |
| 0x04 (ETX)    | 0x20 0xFB         |
| 0x20 (DLE)    | 0x20 0xDF         |

At the receiver side the process is reversed. When a DLE (0x20) is received,
the DLE byte is discarded and the next byte is inverted.
The packet from the previous example will look like this with byte stuffing applied:

```
0x02 0x20 0xFD 0x00 0x00 0x01 0x20 0xFB CRC 0x04
```

At the sender, the CRC is calculated before byte stuffing.
At the receiver, the CRC us checked after removing the byte stuffing.


## Commands 

Command are divided into two groups: generic commands and specific commands.

### Generic commands

The generic commands are commands that must be supported by every module and
are mostly used to identify a module.

The commands are one byte and have a range of 0x01...0x32 (maximum of 50 commands)

| Command     | Value | Description                                            |
|-------------|-------|--------------------------------------------------------|
| Get ID      | 0x01  | Request the ID of the module (see below)               |
| Get name    | 0x02  | Request the name of the module (ASCII string)          |
| Get serial  | 0x03  | Request the serial number of the module (ASCII string) |
| Get version | 0x04  | Request the version of the module.                     |  

The ID of the module is a 4 byte number identifying the module type.
This number is used by the application to provide the proper interface for that module.
Note that two modules with the same functionality (like the LS-CM) have the same module ID.
The serial number must be unique for every module.
The ASCII strings should not be longer than 32 characters.

### Specific commands

The specific commands depends on the module.

The specific commands are one byte and have a range of 0x33...0xFF (maximum of 205 commands).

## Module IDs

Below are the module IDs and names stated for the LilyTronics modules.

| Module ID | Module name                |
|-----------|----------------------------|
| 047C-0001 | LS-CM Communication Module |
|           |                            |
| 047C-FFFF | Special test board         |


© 2024 LilyTronics
