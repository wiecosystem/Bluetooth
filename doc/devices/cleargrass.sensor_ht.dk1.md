# Mijia temperature/humidity monitor

## Intro

This is a simple temperature + humidity sensor (amazingly called "humiture" by the OEM) with a LCD (and there seems to have an e-ink variant) screen.

The device seems actually that simple, it has the nordic DFU protocol, it send it's data via advertisement, and it has some debug services/char, that's it.

## Services and characteristics

* Generic Access (uuid=00001800-0000-1000-8000-00805f9b34fb)
* * Device Name (uuid=00002a00-0000-1000-8000-00805f9b34fb), props=READ WRITE  handle=3
* * Appearance (uuid=00002a01-0000-1000-8000-00805f9b34fb), props=READ  handle=5
* * Peripheral Preferred Connection Parameters (uuid=00002a04-0000-1000-8000-00805f9b34fb), props=READ  handle=7
* Generic Attribute (uuid=00001801-0000-1000-8000-00805f9b34fb)
* * Service Changed (uuid=00002a05-0000-1000-8000-00805f9b34fb), props=INDICATE  handle=10
* Message Service (uuid=226c0000-6476-4566-7562-66734470666d)
* * Humiture (uuid=226caa55-6476-4566-7562-66734470666d), props=NOTIFY  handle=14
* * Message (uuid=226cbb55-6476-4566-7562-66734470666d), props=WRITE NOTIFY  handle=19
* Battery Service (uuid=0000180f-0000-1000-8000-00805f9b34fb)
* * Battery Level (uuid=00002a19-0000-1000-8000-00805f9b34fb), props=READ NOTIFY  handle=24
* Device Information (uuid=0000180a-0000-1000-8000-00805f9b34fb)
* * Manufacturer Name (uuid=00002a29-0000-1000-8000-00805f9b34fb), props=READ  handle=28
* * Model Number (uuid=00002a24-0000-1000-8000-00805f9b34fb), props=READ  handle=30
* * Serial Number (uuid=00002a25-0000-1000-8000-00805f9b34fb), props=READ  handle=32
* * Hardware Revision (uuid=00002a27-0000-1000-8000-00805f9b34fb), props=READ  handle=34
* * Firmware Revision (uuid=00002a26-0000-1000-8000-00805f9b34fb), props=READ  handle=36
* Nordic DFU (uuid=00001530-1212-efde-1523-785feabcd123)
* * DFU Packet (uuid=00001532-1212-efde-1523-785feabcd123), props=WRITE NO RESPONSE  handle=39
* * DFU Control point (uuid=00001531-1212-efde-1523-785feabcd123), props=WRITE NOTIFY  handle=41
* * DFU Version (uuid=00001534-1212-efde-1523-785feabcd123), props=READ  handle=44
* Mi Service (uuid=0000fe95-0000-1000-8000-00805f9b34fb)
* * Token characteristic (uuid=00000001-0000-1000-8000-00805f9b34fb), props=WRITE NOTIFY  handle=47
* * Custom characteristic (uuid=00000002-0000-1000-8000-00805f9b34fb), props=READ  handle=50
* * Firmware version characteristic (uuid=00000004-0000-1000-8000-00805f9b34fb), props=READ  handle=52
* * Event characteristic (uuid=00000010-0000-1000-8000-00805f9b34fb), props=WRITE  handle=54
* * Serial number characteristic (uuid=00000013-0000-1000-8000-00805f9b34fb), props=READ WRITE  handle=56
* * Beacon key characteristic (uuid=00000014-0000-1000-8000-00805f9b34fb), props=READ WRITE  handle=58


### Message service

That's the only custom service (beside the DFU and the MI service, but these aren't specific to this device), it seems to be used only in the debug activity

#### Humiture characteristic

Humiture = Humidity + Temperature, this isn't from me, it's from the OEM.
You can subscibe to it's notifications (real time data) and the data is as such:

* parse = ParseValueUtil.parseHumitureValue(datainhexstring)
* temp = parse[0] # float
* humidity = parse[1] # float
* if parse[2] == 0.0f # which should always be the case?!?
* * text = "unknown"
* if parse[2] != 1.0f and parse[2] != -1.0f
* * text = "near"

* parseHumitureValue(String str):
* * match = Pattern.compile("\\w=(-?\\d*\\.?\\d*)\\s\\w=(\\d*\\.?\\d*)").matcher(str)
* * temp = match[1]
* * humidity = match[2]
=> data = w(?)='-'?(int)'.'?(int)(space)w(?)=(int)'.'?(int)
=> data = `[a-zA-Z_0-9]=(-?[0-9]+.?[0-9]+)[[:space:]][a-zA-Z_0-9]=([0-9]+.?[0-9]+)`

#### Message characteristic

* if clicked on "Restart", send 43470006
* if clicked on "screentest send 4347000104
* if clicked on "screentestend" send 4347000105
* You can subscribe to notifications, data:
* * if data.startswith('4347'):
* * * if data[4-8] = '0002':
* * * * substr = data[8-10]
* * * * if substr != '00' and substr != '01':
* * * * * display substr1

### Broadcast data

The temperature sensor mainly work with broadcast data

It first check if the data starts with '95fe5020', and if the "type" is either 0d10 or 0a10
* If it's 0d10, it parses the humidity and temperature from it
* If it's 0a10, it simply return the bytes after it's size (it's the battery percentage)

* if (str.indexOf("95FE5020") == 10):
* * if (str.indexOf("0D10") == 36):
* * * return parseHexTemperatureHumidity(str.substring(42, (Integer.parseInt(str.substring(40, 42), 16) * 2) + 42));
* * if (str.indexOf("0A10") == 36):
* * * return new float[]{(float) Integer.parseInt(str.substring(42, 44), 16)};

parseHexTemperatureHumidity(String str):
* if ("56046F".equals(str) || "56045604".equals(str)):
* * return new float[]{99999.0f, 99999.0f}

