# Soocare mi toothbrush

## General infos

This is the mi branded toothbrush, actually made by soocare. Another known toothbrush of their is the X3, which may or may not use the same code base.

The toothbrush is a standard electric toothbrush, with some BLE connectivity to set some custom settings, and get some data, such as the "score".

## Settings and informations

### Settings

* Anti splash protection (should wait 10 seconds before turning on the motor) on/off
* Brushing duration: 2.0 minutes or 2.5 minutes
* (custom) Brushing mode: beginner, gentle, standard or enhanced
* Additional features on/off
* (additional) Features: "30s extra whitening", "30s gum care" or "10s tongue cleaning". Even if the title suggest a multiple choice, you can actually only select one


### Informations

* Battery percentage
* History of brushing:
* * Score
* * Brushing duration
* * Coverage
* * Evenness
* Toothbrush head remaining (no sensor, you have to reset it on the phone)

The brush also seems to know "where" did you brush your teeth as the app seems to give advices such as where to brush more. They also advertise that the brush "monitors six areas of the upper and lower teeth" (basically, front, left right for upper and lower teeth)
They do have historical data.

I would guess that for every historic data, the brush store the time for each area, and that the score, coverage and evenness is calculated on the phone (a little bit like the scale)


## Protocol

* The toothbrush uses the proprietary xiaomi authentication mechanism (or at least one of them)
* The toothbrush also uses nordic' UART and DFU services.

### Services and characteristics

* Generic access (uuid=00001800-0000-1000-8000-00805f9b34fb)
* * Device name (uuid=00002a00-0000-1000-8000-00805f9b34fb), props=READ WRITE  handle=3
* * Appearance (uuid=00002a01-0000-1000-8000-00805f9b34fb), props=READ  handle=5
* * Peripheral Preferred Connection Parameters (uuid=00002a04-0000-1000-8000-00805f9b34fb), props=READ  handle=7
* Device Information (uuid=0000180a-0000-1000-8000-00805f9b34fb)
* * Manufacturer Name String (uuid=00002a29-0000-1000-8000-00805f9b34fb), props=READ  handle=20
* * Model Number String (uuid=00002a24-0000-1000-8000-00805f9b34fb), props=READ  handle=2
* * Serial Number String (uuid=00002a25-0000-1000-8000-00805f9b34fb), props=READ  handle=24
* * Hardware Revision String (uuid=00002a27-0000-1000-8000-00805f9b34fb), props=READ  handle=26
* * Firmware Revision String (uuid=00002a26-0000-1000-8000-00805f9b34fb), props=READ  handle=28
* * System ID (uuid=00002a23-0000-1000-8000-00805f9b34fb), props=READ  handle=30
* Battery Service
* * Battery Level (uuid=00002a19-0000-1000-8000-00805f9b34fb), props=READ NOTIFY  handle=33
* Nordic UART: uuid=6e400001-b5a3-f393-e0a9-e50e24dcca9e
* * RX (uuid=6e400003-b5a3-f393-e0a9-e50e24dcca9e), props=NOTIFY  handle=14
* * TX (uuid=6e400002-b5a3-f393-e0a9-e50e24dcca9e), props=WRITE NO RESPONSE WRITE  handle=17
* Nordic DFU (uuid=00001530-1212-efde-1523-785feabcd123)
* * DFU Packet (uuid=00001532-1212-efde-1523-785feabcd123), props=WRITE NO RESPONSE  handle=37
* * DFU Control point (uuid=00001531-1212-efde-1523-785feabcd123), props=WRITE NOTIFY  handle=39
* * DFU Version (uuid=00001534-1212-efde-1523-785feabcd123), props=READ  handle=42
* Mi service (uuid=0000fe95-0000-1000-8000-00805f9b34fb)
* * Token characteristic (uuid=00000001-0000-1000-8000-00805f9b34fb), props=WRITE NOTIFY  handle=45
* * Custom characteristic (uuid=00000002-0000-1000-8000-00805f9b34fb), props=READ  handle=48
* * Firmware version characteristic (uuid=00000004-0000-1000-8000-00805f9b34fb), props=READ  handle=50
* * Event characteristic (uuid=00000010-0000-1000-8000-00805f9b34fb), props=WRITE  handle=52
* * Serial number characteristic (uuid=00000013-0000-1000-8000-00805f9b34fb), props=READ WRITE  handle=54
* * Beacon key characteristic (uuid=00000014-0000-1000-8000-00805f9b34fb), props=READ WRITE  handle=56

### Custom services/chars

* There's 1 custom characteristic, all under the xiaomi's custom service
* It's read only, and never used in the app

### Advertisement data

* Doesn't seems to be used

### Protocol

* The protocol is actually the xiaomi's proprietary authentication mechanism, and then everything happens in the UART adapter
* The UART is divided in subcommands

#### UART Protocol

* The UART port is "divided" in commands
* The format for commands is:
* * uint16: id of the command
* * uint16: size of the data
* * uint16: Frame number (the device doesn't seems to care much)
* * uint16: CRC16 (CCITT-FALSE algorithm) of the first 6 bytes
* * uint8[size]: data
* "Set" commands receive an acknowledge with size=0x01 and data=0x00 if ok, 0x01 if error
* "Get commands" doesn't have parameters, so tx size is always = 0x00

#### UART Commands

* 0x01: Set brushing time, tx size=0x04, format:
* * uint16: brushing time (0x78 for 120s/2mn, 0x96 for 150s/2.5mn)
* * uint16: extra time
* 0x02: Get history data, tx size=0x00, return format if there's an entry, size=0x01, data=0x00 else:
* * uint16[6]: timestamp
* * uint16: number of samples for normal brushing time (one sample per second)
* * uint16: number of samples for additional feature time (one sample per second)
* * uint8[]: array of samples for normal brushing, an uint8 per second, seemingly an number per zone
* * uint8[]: array of samples for additional feature, all zeroes (does not count for the score)
* * uint16: unknown, always {0x00, 0x00}
* 0x03: Set date/time, tx size=0x0c, format:
* * uint32: UNIX timestamp in seconds
* * uint32: Offset to UTC in seconds (raw offset from the phone)
* * uint32: uknown, always 0x000000 it seems
* * Note: It seems the app doesn't care about that, so you can just set the timestamp + all zeroes (UTC time)
* 0x04: DFU/Firmware update, tx size=0
* 0x05: Get battery level, tx size=0x00, return format:
* * uint8: battery percentage
* 0x06: Get firmware and hardware versions, tx size=0x00, return format:
* * uint8[5]: firmware version, null terminated string
* * uint8[5]: hardware version, null terminated string
* 0x07: Set anti splash protection, tx size=0x01, format:
* * uint8: enable/disable boolean, 0x00 = disable, 0x01 = enable
* * It's called "Crescendo" in the app, apparently, it does makes the brush go crescendo for around 10s
* 0x08: Set additional feature, tx size=0x01, format:
* * uint8: feature (0x00 = disable, 0x01 = 30s extra whitening, 0x02 = 30s gum care, 0x04 = 10s tongue cleaning)
* * Note: the time seems to be set in 0x01 instead, this will likely only set the force
* * Note: the modes are called "no", "polish", "nurse", "tongue" in the app
* 0x09: Set brushing mode, tx size=0x04, format:
* * uint32: brushing mode (0x0322013c = beginner, 0x0318013c = gentle, 0x03040150 = standard, 0x03e60032 = enhanced), format:
* * uint8: motor gear, 1 to 5
* * uint16: motor frequency, 10 to 400 / 0x0b to 0x8f (limited to 100 to 400 in the app!)
* * uint8: motor duty cycle, 1 to 99 / 0x01 to 0x63 (in percentage)
* * 0x0a: Bind
* * Doesn't seems to do much
* * 0x0b: GetID
* * Just ask to return the ID
* * 0x0c: SetID
* * Just set the ID

#### History entry

* The history entry is a timestamp, the number of seconds and the areas brushed (per second) basically (see the uart commands for more details)
* The fields are pressure, level and area
* Pressure (overpressure): boolean, 1 bit
* Level (gear usage): 0 to 3, 2 bits
* Area: 1 to 6, 5 bits, fields:
* * Zone 1 is up left
* * Zone 2 is down left
* * Zone 3 is middle up
* * Zone 4 is middle down
* * Zone 5 is up right
* * Zone 6 is down right
* * All bits to 1 is undefined
* * Every other case is "unIdentify"

## TODO

* Understand the custom characteristic 00000002-0000-1000-8000-00805f9b34fb
* Understand the format of the firmware version char
