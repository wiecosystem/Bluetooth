import sys
import datetime
import random
from struct import *
from bluepy import btle

import body


class miScale(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

        self.address = sys.argv[1]
        self.height = int(sys.argv[2])
        self.age = int(sys.argv[3])
        self.sex = sys.argv[4]

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr == self.address:
            for (adType, desc, value) in dev.getScanData():
                if adType == 22:
                    data = bytes.fromhex(value[4:])
                    ctrlByte0 = data[0]
                    ctrlByte1 = data[1]

                    emptyLoad = ctrlByte1 & (1<<7)
                    isStabilized = ctrlByte1 & (1<<5)
                    hasImpedance = ctrlByte1 & (1<<1)


                    if emptyLoad:
                        print("(no load)")

                    print("New packet")
                    if isStabilized:
                        print("New stabilized weight")
                    if hasImpedance:
                        print("New impedance")

                    print("\t Control bytes = {0:08b}/{1:08b}".format(ctrlByte0, ctrlByte1))
                    print("\t Date = {}/{}/{} {}:{}:{}".format(int(data[5]), int(data[4]), int((data[3] << 8) | data[2]), int(data[6]), int(data[7]), int(data[8])))

                    impedance = ((data[10] & 0xFF) << 8) | (data[9] & 0xFF)
                    weight = (((data[12] & 0xFF) << 8) | (data[11] & 0xFF)) / 200.0

                    print("\t impedance is {}".format(impedance))
                    print("\t weight is {}".format(weight))

                    if hasImpedance:
                        lib = body.bodyMetrics(weight, self.height, self.age, self.sex, impedance)

                        print("\t\tLBM = {}".format(lib.getLBMCoefficient()))
                        print("\t\tBody fat = {}".format(lib.getFatPercentage()))
                        print("\t\tBody fat scale = {}".format(lib.getFatPercentageScale()))
                        print("\t\tWater = {}".format(lib.getWaterPercentage()))
                        print("\t\tWater scale = {}".format(lib.getWaterPercentageScale()))
                        print("\t\tBone mass = {}".format(lib.getBoneMass()))
                        print("\t\tBone mass scale = {}".format(lib.getBoneMassScale()))
                        print("\t\tMuscle mass = {}".format(lib.getMuscleMass()))
                        print("\t\tMuscle mass scale = {}".format(lib.getMuscleMassScale()))
                        print("\t\tVisceral fat = {}".format(lib.getVisceralFat()))
                        print("\t\tVisceral fat scale = {}".format(lib.getVisceralFatScale()))
                        print("\t\tBMI = {}".format(lib.getBMI()))
                        print("\t\tBMI scale = {}".format(lib.getBMIScale()))
                        print("\t\tBMR = {}".format(lib.getBMR()))
                        print("\t\tBMR scale = {}".format(lib.getBMRScale()))
                        print("\t\tIdeal weight = {}".format(lib.getIdealWeight()))
                        return

                elif adType == 1 or adType ==  2 or adType == 9:
                    continue
                elif adType == 255:
                    continue
                else:
                    print("=> new unknown packet: type={} data={}".format(adType, value))

    def run(self):
        scanner = btle.Scanner()
        scanner.withDelegate(self)
        while True:
            scanner.start()
            scanner.process(1)
            scanner.stop()

scale = miScale()
scale.run()
