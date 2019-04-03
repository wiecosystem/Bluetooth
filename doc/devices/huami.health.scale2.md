# Mi Body Composition Scale (MIBCS)

## Intro
The scale communicate over BLE, with some custom UUIDs, but actually, the data is sent over ad broadcasts, that's how mi fit get it's first data, the UUIDs are mostly for data history and configuration.

Huami is using a java JNI (= native code library, originally written in c++) to calculate the metrics from some parameters (weight, impedance, age, height, sex). The JNI doesn't come from Huami, it comes from holtek, the OEM for the MCU used by the scale. holtek provide the JNI and a wrapper jar library that developpers can use to get the metrics.

Mi fit doesn't use all the data provided by the JNI, it also sometime use or create it's own, for example, there's no protein calculation in the JNI, nor is the "body age" and the "body type". It also doesn't use the scales provided by the JNI as it's a pretty new feature of the holtek "sdk" and Huami already had that before, so they didn't changed to use the JNI's scales, but continued using their own (for that reason, scale data may change between the python code and what you would see on mi fit).

## Warning
This is a best-effort reverse engineering of the library, not a scientific evaluation of the library, some data may not be ideal (ideal weight for example) and there may be some bugs.

## What can we do

The current values we can calculate are:

* LBM (using the impedance)
* Fat percentage
* Water percentage
* Bone mass
* Muscle mass
* Visceral fat
* BMI
* BMR
* Ideal weight
* Fat mass to lose/gain
* Protein percentage
* Body type

## What we cannot do

The current values that cannot be calculated are:

* Body score
* Body age

## Scales

As the JNI provide some scales, here's what they mean (remember, the numbers represent the transition between two!):

* Fat percentage: very low/low/normal/high/very high
* Water percentage: unsufficient/normal/good
* Bone mass: unsufficient/normal/good
* Muscle mass: unsufficient/normal/good
* Visceral fat: normal/high/very high
* BMI: underweight/normal/overweight/obese/morbidly obese
* Ideal weight: underweight/normal/overweight/obese/morbidly obese
* BMR: unsufficient/normal

## BLE Services and Characteristics

* Generic Access (uuid=00001800-0000-1000-8000-00805f9b34fb)
* * Device Name (uuid=00002a00-0000-1000-8000-00805f9b34fb), READ WRITE handle=3
* * Appearance (uuid=00002a01-0000-1000-8000-00805f9b34fb), READ handle=5
* * Peripheral Privacy Flag (uuid=00002a02-0000-1000-8000-00805f9b34fb), READ WRITE handle=7
* * Peripheral Preferred Connection Parameters (uuid=00002a04-0000-1000-8000-00805f9b34fb), READ handle=9
* * Reconnection Address (uuid=00002a03-0000-1000-8000-00805f9b34fb), READ WRITE NO RESPONSE WRITE handle=11
* Generic Attribute (uuid=00001801-0000-1000-8000-00805f9b34fb)
* * Service Changed (uuid=00002a05-0000-1000-8000-00805f9b34fb), READ INDICATE handle=14
* Device Information (uuid=0000180a-0000-1000-8000-00805f9b34fb)
* * Serial Number String (uuid=00002a25-0000-1000-8000-00805f9b34fb), READ handle=18
* * Software Revision String (uuid=00002a28-0000-1000-8000-00805f9b34fb), READ handle=20
* * Hardware Revision String (uuid=00002a27-0000-1000-8000-00805f9b34fb), READ handle=22
* * System ID (uuid=00002a23-0000-1000-8000-00805f9b34fb), READ handle=24
* * PnP ID (uuid=00002a50-0000-1000-8000-00805f9b34fb), READ handle=26
* Body Composition (uuid=0000181b-0000-1000-8000-00805f9b34fb)
* * Current Time (uuid=00002a2b-0000-1000-8000-00805f9b34fb), READ WRITE handle=29
* * Body Composition Feature (uuid=00002a9b-0000-1000-8000-00805f9b34fb), READ handle=31
* * Body Composition Measurement (uuid=00002a9c-0000-1000-8000-00805f9b34fb), INDICATE handle=33
* * Body Composition History (uuid=00002a2f-0000-3512-2118-0009af100700), WRITE NOTIFY handle=36
* Huami Configuration Service (uuid=00001530-0000-3512-2118-0009af100700)
* * DFU Control point (uuid=00001531-0000-3512-2118-0009af100700), WRITE NOTIFY handle=40
* * DFU Packet (uuid=00001532-0000-3512-2118-0009af100700), WRITE NO RESPONSE handle=43
* * Peripheral Preferred Connection Parameters (uuid=00002a04-0000-1000-8000-00805f9b34fb), READ WRITE NOTIFY handle=45
* * Scale configuration (uuid=00001542-0000-3512-2118-0009af100700), READ WRITE NOTIFY handle=48
* * Low battery (uuid=00001543-0000-3512-2118-0009af100700), READ WRITE NOTIFY handle=51

## Custom services/chars

### Body Measurement History (00002a2f-0000-3512-2118-0009af100700)

This is the main characteristic, it gives the measurement history

* uint8: command
* uint8[]: data

#### Body Composition History commands/responses

* 0x01: (guess) Session start
* * uint16 (only in responses): probably confirmation, always 0x0100
* * uint32: unknown
* 0x02: Measurements (only in responses)
* * The format is the same as in the advertisements, but without the first control byte
* 0x03: Stop/End history
* 0x04: (guess) Session end
* * uint32: unknown, same value as in command 0x01

Notes
* The uint32 seems to be a "device id", which is randomly chosen, so the scale can only send measurements since last check by this device (so multiple devices can query the scale and none will lose data)
* The Mi Fit log says `{origin=01 00 00 68 c4 83 64, flag=01 , cmd=00 , code=00 , data=xx xx xx xx}`
* Also, it has logs about these flags:
* * type:1
* * isMeasurement:false
* * stable:false
* * isHistory:false
* * isFinish:true
* * isImpedanceStable:false

## Scale configuration (00001542-0000-3512-2118-0009af100700)

That's where the scale configuration happens, for now, only the scale unit configuration is known:

* uint8: unknown, always 0x06 for now
* uint8: unknown, always 0x04 for now
* uint8: unknown, always 0x00 for now
* uint8: weight unit: 0x00 for SI, 0x01 for imperial and 0x02 for catty

## Low Battery (00001543-0000-3512-2118-0009af100700)

* uint8: unknown, always 0x01
* uint8: low battery alert, 0x00 if normal, 0x01 if low battery

## Advertisement

The scale also works using advertisement packets, with a adType 0xff (OEM data) that is unknown yet, and a adType 0x16 (Service Data) that have this format:

Data is 17 bytes long, with the first 4 bytes being an UUID, the other 13 bytes are the payload

Payload format (year, impedance and weight are little endian):

* bytes 0 and 1: control bytes
* bytes 2 and 3: year
* byte 4: month
* byte 5: day
* byte 6: hours
* byte 7: minutes
* byte 8: seconds
* bytes 9 and 10: impedance
* bytes 11 and 12: weight (`*100` for pounds and catty, `*200` for kilograms)

Control bytes format (LSB first):

* bit 0:   unknown
* bit 1:   unknown
* bit 2:   unknown
* bit 3:   unknown
* bit 4:   unknown
* bit 5:   unknown
* bit 6:   unknown (always 1 on my scale)
* bit 7:   is pounds
* bit 8:   is empty load (no weight on scale)
* bit 9:   is catty
* bit 10:  is stabilized (weight confirmed, that's also when the weight on scale blinks)
* bit 11:  unknown
* bit 12:  unknown
* bit 13:  unknown (always 1 on my scale)
* bit 14:  have impedance (impedance bytes are set correctly)
* bit 15:  unknown

## Thanks

KailoKyra for his help, Hopper and Radare2/Cutter, shell-storm.org, gregstoll.com, openscale (and oliexdev for his knowledge), Wingjam (on github), and the poor souls who posted the JAR and some JNIs of holtek's SDK.
