import body
import sys

lib = body.bodyMetrics(float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]))

print("LBM = {}".format(lib.getLBMCoefficient()))
print("Body fat = {}".format(lib.getFatPercentage()))
print("Body fat scale = {}".format(lib.getFatPercentageScale()))
print("Water = {}".format(lib.getWaterPercentage()))
print("Water scale = {}".format(lib.getWaterPercentageScale()))
print("Bone mass = {}".format(lib.getBoneMass()))
print("Bone mass scale = {}".format(lib.getBoneMassScale()))
print("Muscle mass = {}".format(lib.getMuscleMass()))
print("Muscle mass scale = {}".format(lib.getMuscleMassScale()))
print("Visceral fat = {}".format(lib.getVisceralFat()))
print("Visceral fat scale = {}".format(lib.getVisceralFatScale()))
print("BMI = {}".format(lib.getBMI()))
print("BMI scale = {}".format(lib.getBMIScale()))
print("BMR = {}".format(lib.getBMR()))
print("BMR scale = {}".format(lib.getBMRScale()))
print("Ideal weight = {}".format(lib.getIdealWeight()))
print("Ideal weight scale = {}".format(lib.getIdealWeightScale()))
if lib.getFatMassToIdeal()['type'] == 'to_lose':
    print("Fat mass to lose = {}".format(lib.getFatMassToIdeal()['mass']))
else:
    print("Fat mass to gain = {}".format(lib.getFatMassToIdeal()['mass']))
print("Protein percentage = {}".format(lib.getProteinPercentage()))
print("Protein percentage scale = {}".format(lib.getProteinPercentageScale()))
print("Body type = {}".format(lib.getBodyTypeScale()[lib.getBodyType()]))
