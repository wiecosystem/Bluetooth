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
* BMR (basal metabolism)
* Ideal weight
* Fat mass to lose/gain
* Protein percentage
* Body type
* Body age
* Body Score
* Scales used in Mi Fit and in the native SDK

## Body Score

The body score is basically 100 - malus, where malus is the sum of a sub-score computed for every data point (bmi, muscle mass, fat percentage, etc).
Each score is mostly based on the scales (where "normal" or "good" gives no malus, being way over the limits gives you maximum malus, and being in between gives you a variable malus), but sometime, it's even more precise than the scales (for example, for body fat, even being "normal" is not enough, you need to be in the first half of "normal", or even "low").
You can refer to `body_score.py` if you want more details on the algorithms.


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
* * Battery (uuid=00001543-0000-3512-2118-0009af100700), READ WRITE NOTIFY handle=51

## Custom services/chars

### Body Composition Feature (00002a9b-0000-1000-8000-00805f9b34fb)
Apparently not used

### Body Composition Measurement (00002a9c-0000-1000-8000-00805f9b34fb)
It is used as notifications

If notified, you'll receive the same weight data as in advertisements

### Body Measurement History (00002a2f-0000-3512-2118-0009af100700)
This is the main characteristic, it gives the measurement history
The device id is randomly chosen at first start of mi fit, the scale keep track of where each device is so it doesn't send all the data each time, and don't skip any data either

#### Get data size

Send 0x01 [device id]
Si no response or response lenght is less than 3 or reponse[0] it not 1, send 0x03
Data size = response[1] and response[2], send 0x03 to end

#### Get data

Register to notifications and send 0x02
Get all notifications and send 0x03 at the end
Each notifications should have the same data as the advertisements
If you have as much data as indicated by the get data size command, send 0x04 [device id] to update your history position
If registering to notifications or sending the 0x02 failed, send 0x03 anyway

### Scale configuration (00001542-0000-3512-2118-0009af100700)

There's several commands there, but nothing really special. No idea what's the "one foot measure" but it seems useless.

#### Set unit
Send 0x06 0x04 0x00 [unit] where [unit] is 0x00 for SI, 0x01 for imperial and 0x02 for catty

#### Enable Partial measures
Send 0x06 0x10 0x00 [!enable] and you should receive a response that is 0x16 0x06 0x10 0x00 0x01

#### Erase history record
Send 0x06 0x12 0x00 0x00, you should receive a response that is 0x16 0x06 0x12 0x00 0x01

#### Enable LED display
Send 0x04 0x02 to enable, 0x04 0x03 to disable

#### Calibrate
Send 0x06 0x05 0x00 0x00

#### Self test
Send 0x04 0x01 to enable 0x04 0x04 to disable

### Set Sandglass Mode
Send 0x06 [mode] 0x00 where mode is an uint16 that equals 0x000A or 0x000B

### Get Sandglass Mode
Read and if mode is set, it is equal to 0x03 0x00

#### Start One Foot Measure
Register to notifications and send 0x06 0x0f 0x00 0x00
You should get a notification like 0x06 0x0f 0x00 [flags] [time]\*2
The only known flags are finished (0x02) and measuring (0x01)
Time is inverted (time = (time[1] << 8) | time[0]) and multiplied by 100
This feature seems pretty useless

#### Stop One Foot Measure
Send 0x06 0x11 0x00 0x00

### Date and time (00002a2b-0000-1000-8000-00805f9b34fb)
You can read and write it, format: year[0], year[1], month, day, hour, min, sec, 0x00, 0x00

### Battery (00001543-0000-3512-2118-0009af100700)
Two uint8, if both equals 0x01, then it's a low battery alert, simple as that.

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

* bit 0:   unused
* bit 1:   unused
* bit 2:   unused
* bit 3:   unused
* bit 4:   unused
* bit 5:   partial data
* bit 6:   unused
* bit 7:   weight sent in pounds
* bit 8:   finished (is there any load on the scale)
* bit 9:   weight sent in catty
* bit 10:  weight stabilised
* bit 11:  unused
* bit 12:  unused
* bit 13:  unused
* bit 14:  impedance stabilized
* bit 15:  unused

## Thanks
KailoKyra for his help, Hopper and Radare2/Cutter, shell-storm.org, gregstoll.com, openscale (and oliexdev for his knowledge), Wingjam (on github), and the poor souls who posted the JAR and some JNIs of holtek's SDK.
