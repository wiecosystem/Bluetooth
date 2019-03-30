# Mi Body Composition Scale (MIBCS)

## Warning
Taken straight from MIBCS-Reverse-Engineering, this will be rewritten soon.

## Intro
The scale communicate over BLE, with some custom UUIDs, but actually, the data is sent over ad broadcasts, that's how mi fit get it's first data, the UUIDs are mostly for history data, configuration, and the like.

Xiaomi is using a java JNI (= native code library, originally written in c++) to calculate the metrics from some parameters (weight, impedance, age, height, sex). The JNI doesn't come from xiaomi, it comes from holtek, the OEM for the MCU used by the scale. holtek provide the JNI and a wrapper jar library that developpers can use to get the metrics.

Mi fit doesn't use all the data provided by the JNI though, it also sometime use or create it's own, for example, there's no protein calculation in the JNI, nor is the "body age", the "body type" or some minor data. thus they aren't here either, as the python code is derived from the reverse engineering of the JNI, not mi fit. It also doesn't use the scales provided by the JNI as it's a pretty new feature of the holtek "sdk" and xiaomi already did that before, so they didn't changed to use the JNI's scales, but continued using their own (for that reason, scale data may change between the python code and what you would see on mi fit).

## A bit of warning
Take the informations this will give with a grain of salt, i couldn't try every case possible to be sure there's no bugs in the calculations, some are correct from mi fit, but the library mi fit uses didn't got the best way to calculate things (ideal weight), and some are guessed from mi fit, and maybe not the exact same formula (protein percentage, body type). In any case, the scale gives an indication more than an precise down to the 0.1% data.

## What can it do

The current values body.py can calculate are:

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

## What can't it do

The current values that cannot be calculated (because they're in mi fit and not in holtek's SDK) are:

* Body score (we don't really care about this)
* Body age (we probably don't care either)

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

## BLE protocol

The scale use few services and descriptors, along with the usual ones, we also have

* Body composition (standard) service: 0000181b-0000-1000-8000-00805f9b34fb
* * Current time (standard)characteristic: 00002a2b-0000-1000-8000-00805f9b34fb
* * Body composition feature (standard) characteristic: 00002a9b-0000-1000-8000-00805f9b34fb
* * Body composition measurement (standard) characteristic: 00002a9c-0000-1000-8000-00805f9b34fb
* * Body measurement history (custom) characteristic: 00002a2f-0000-3512-2118-0009af100700
* Custom service: 00001530-0000-3512-2118-0009af100700
* * Custom characteristic 1: 00001531-0000-3512-2118-0009af100700
* * Custom characteristic 2: 00001532-0000-3512-2118-0009af100700
* * Preferred connection parameters (standard) characteristic: 00002a04-0000-1000-8000-00805f9b34fb
* * Scale configuration (custom) characteristic: 00001542-0000-3512-2118-0009af100700
* * Custom characteristic 3: 00001543-0000-3512-2118-0009af100700

## Body composition service

### Current time (00002a2b-0000-1000-8000-00805f9b34fb) read/write

Can be configured with `{ year_msb, year_lsb, month, day, hour, minute, second, 0x03, 0x00, 0x00}`
(0x03 for manual time update + external reference time update, per https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.current_time.xml)
Invalid dates are ignored.

### Body measurement history (00002a2f-0000-3512-2118-0009af100700) write/notify

It seems to handle the history of measurements, as they're saved in the scale

Write format (alleged, from openscale):
* Get only last measurement: `{0x01, 0xff, 0xff, unique_id_lsb, unique_id_msb}`
* Get all unread measurements: `{0x01, 0xff, 0xff, 0xff, 0xff}`
* Get history data: `{0x02}`

I suspect that the write format is `{ command, data }` where command = 0x01 (configure history), 0x02 (get history), 0x03 (stop notifications), 0x04 (enable full history, send 0x02 after) and maybe more also.

It uses BLE notifications to send the last measurement.
The notifications is either `{0x01, 0x01, 0x00, 0xff, 0xff, x0ff, 0xff`}, `{ raw data from measurement, same format as  the ad packets without the uuid before }` or `{0x03}` (end of history)

## Custom service

Mostly unknown currently
Called "Weight service" apparently.

### Custom characteristic 1 (00001531-0000-3512-2118-0009af100700) write/notify

Currently unknown, they use the same UUID for the firmware characteristic of the mi band
Maybe used for firmware updates.

### Custom characteristic 2 (00001532-0000-3512-2118-0009af100700) write/no response

Currently unknown, they use the same UUID for the firmware characteristic of the mi band
Maybe used for firmware updates.

### Scale configuration (00001542-0000-3512-2118-0009af100700) read/write/notify

It seems to handle the configuration of the scale, such as the unit

Current known format (from openscale): `{0x06, 0x04, 0x00, weight_unit}`, where `weight_unit` = 0 for Kilogram, 1 for pounds, 2 for catty (chinese unit)

Apparently, called "Control point"

It gives 0x03, 0x01 when read

### Custom characteristic 3 (00001543-0000-3512-2118-0009af100700) read/write/notify

Currently unknown

It gives 0x01, 0x00 when read 

Maybe battery service, it gives 0x01, 0x01 when low battery.

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

Alleged control bits:

* Should have a battery status bit somewhere (low battery indication)
* Recalibration bit?



## Thanks

KailoKyra for his help, Hopper and Radare2/Cutter, shell-storm.org, gregstoll.com, openscale (and oliexdev for his knowledge), Wingjam (on github), and the poor souls who posted the JAR and some JNIs of holtek's SDK.
