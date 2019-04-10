# Xiaomi BLE kettle

## Intro

The yunmi kettles (v1 and v2, they seems to use the same protocol) are just kettles with some additional features and monitoring using BLE.

These devices use the proprietary auth mechanism.

WARNING: I don't own the device, hence, this documentation is theorical. If you have a kettle, contributions to correct this documentation are welcome!

## Limitations

* Cannot heat water if "keep warm" is off
* Cannot remotely enable "keep warm"
* The maximum time for "keep warm" is 12h
* If the temperature drops (eg you add cold water), "keep warm" will turn off
* If the water level is low, "keep warm" will turn off
* The minimum temperature for "keep warm" is 40 degrees celsius

## Services & Characteristics

* Mi service (uuid=0000fe95-0000-1000-8000-00805f9b34fb)
* * Token characteristic (uuid=00000001-0000-1000-8000-00805f9b34fb), props=WRITE NOTIFY  handle=45
* * Firmware version characteristic (uuid=00000004-0000-1000-8000-00805f9b34fb), props=READ  handle=50
* * Event characteristic (uuid=00000010-0000-1000-8000-00805f9b34fb), props=WRITE  handle=52
* * Setup characteristic (uuid=aa01), props=WRITE handle=
* * Status characteristic (uuid=aa02), props=NOTIFY handle=
* * Time characteristic (uuid=aa04), props=READ WRITE handle=
* * Boil mode characteristic (uuid=aa05), props=READ WRITE handle=
* * MCU Version characteristic (uuid=2a28), props=READ handle=

## Protocol

### Setup characteristic

* uint8: type (0 = boil and cool down to set temperature, 1 = heat to set temperature)
* uint8: temperature (40 to 95)

### Boil mode characteristic

* uint8: turn off after boil (boolean)

### Time characteristic

* uint8: time to keep warm (0 to 12, multiplied by 2)

### MCU Version characteristic

* char[]: version

### Status characteristic

* uint8: action (0 = idle, 1 = heating, 2 = cooling, 3 = keeping warm)
* uint8: mode (1 = boil, 2 = keep warm, 255 = none)
* uint16: unknown
* uint8: keep warm temperature (40 to 95 degrees celsius)
* uint8: current temperature (0 to 100 degrees celsius)
* uint8: keep warm type (0 = boil and cool down to set temperature, 1 = heat to set temperature)
* uint16: keep warm time (minutes since keep warm was enabled)


## Thanks
This documentation is largely based on https://github.com/aprosvetova/xiaomi-kettle and https://github.com/drndos/mikettle, a huge thanks to them!
