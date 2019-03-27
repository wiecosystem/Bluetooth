# Bluetooth/BLE
General information on how BLE is used in Xiaomi's devices.

## General context

Xiaomi (and it's many, many sub-brands) uses several wireless protocols for their devices, mainly zigbee (aqara devices), BLE (many "standalone" devices and smartbands/smartwatches from huami and amazfit), and wifi (usually their "biggest"  devices such as the vacuum cleaner, and some yeelight devices, basically, what's guaranteed to have enough power at all times)

Xiaomi is known to share it's logistics division with it's sub-OEMs, and also it's "Mi Home" ecosystem. They also seems to share some proprietary protocols, especially in BLE and zigbee.

## BLE notes

* Almost every devices implement a similar (if not the same) firmware upgrade logic, there seems to have differences as some uses Nordic semiconductors' DFU service, and other seems to only mimic parts of it. I guess they started by using Nordic microchips and then expanded, and did reproduce the Nordic's DFU mode to their other devices so they still can share most of the code.
* Some devices implement authentication, even if it's "optional" as you can still talk to the device for some time (around a minute) before it drops the connection. The authentication is encrypted using a custom JNI, "libblecipher.so". These devices seems to include the Flora plant monitor, the Soocare toothbrush, and the temperature sensor, it isn't excluded that they use the same mechanism in other devices such as the mi bands.
* Xiaomi does have 3 16b UUIDs, but i've only seen `fe95` being used so far.

## Devices covered

If you have a xiaomi ecosystem device and did reverse engineer it, feel free to contribute. For now, for obvious reasons, i'll focus on some devices i already own:

* Yeelight bedside lamp
* Mi body composition scale
* Soocare mi toothbrush
* Yeelight Candela
* Mi band 2
* Amazfit pace

## And for other protocols?

* I also own some other devices, including the aqara hub, and will focus on it next
* You can check out the awesome work of Dennis Giese [here] https://github.com/dgiese/dustcloud
* There's also some other github repos to check out, i'll do a more complete list later
