
# Reverse engineered from amazfit's app (also known as Mi Fit)

class body_score:

    def __init__(self, age, sex, height, bmi, bodyfat):
        self.age = age
        self.sex = sex
        self.height = height
        self.bmi = bmi
        self.bodyfat = bodyfat

    def getBodyScore(self):
        score = 100
        score -= self.getBmiDeductScore()
        score -= self.getBodyFatDeductScore()
        score -= self.getMuscleDeductScore()
        score -= self.getWaterDeductScore()
        score -= self.getVisceralFatDeductScore()
        score -= self.getBoneDeductScore()
        score -= self.getBasalMetabolismDeductScore()
        score -= self.getProteinDeductScore()

        return score

    def getBodyScoreScale(self):
        # very bad, bad, normal, good, better
        return [50.0, 60.0, 80.0, 90.0]

    def calculate(data, a, b, c, d):
        result = ((data - b) / (a - b)) * float(c - d)
        if result >= 0.0:
            return result
        return 0.0

    def getBmiDeductScore():
        if not self.height >= 90:
            # "BMI is not reasonable
            return 0.0

        arr = [14.0, 15.0]
        if self.bmi >= arr[1]:
            if self.bmi >= 18.5 or self.age < 18:
                return value
            else:
                return self.calculate(self.bmi, arr[1], 18.5, 15, 5) + 5.0

        # Perfect range (bmi >= 18.5 and bodyfat not high for adults, bmi >= 15.0 for kids
        if self.bmi >= 18.5 and self.age >= 18 and self.bodyfat < normalfat[2]:
            return 0.0
        if self.bmi >= arr[1] and self.age < 18 and self.bodyfat < normalfat[2]:
            return 0.0
        # Deadly skinny
        elif self.bmi <= arr[0]:
            return 30.0
        else:
            # Too skinny
            if self.bmi > arr[0] and self.bmi < arr[1]:
                return self.calculate(self.bmi, arr[0], arr[1], 30, 15) + 15.0
            # Low but not too skinny
            if self.bmi >= arr[1] and self.bmi < 18.5 and self.age >= 18:
                return self.calculate(self.bmi, 15.0, 18.5, 15, 5) + 5.0

            # Normal or high bmi but too much bodyfat
            if self.bmi >= arr[1] and self.bodyfat >= normalfat[2]:
                if self.bmi >= 32.0:
                    return 10.0
                if self.bmi > 28.0:
                    return self.calculate(self.bmi, 28.0, 25.0, 5, 10) + 5.0
                else:
                    return 0.0

    def getBodyFatDeductScore():
        normal = []
        if sex == 'male':
            if age < 18:
                normal = [7.0, 16.0, 25.0, 30.0]
            elif age < 40:
                normal = [11.0, 17.0, 22.0, 27.0]
            elif age < 60:
                normal = [12.0, 18.0, 23.0, 28.0]
            else:
                normal = [14.0, 20.0, 25.0, 30.0]
        elif sex == 'female':
            if age < 12:
                normal = [12.0, 21.0, 30.0, 34.0]
            elif age < 14:
                normal = [15.0, 24.0, 33.0, 37.0]
            elif age < 16:
                normal = [18.0, 27.0, 36.0, 40.0]
            elif age < 18:
                normal = [20.0, 28.0, 37.0, 41.0]
            elif age < 40:
                normal = [21.0, 28.0, 35.0, 40.0]
            elif age < 60:
                normal = [22.0, 29.0, 36.0, 41.0]
            else:
                normal = [23.0, 30.0, 37.0, 42.0]

        best = 0.0
        if self.sex == 'male':
            best = normal[2] - 3.0
        elif self.sex == 'female':
            best = normal[2] - 2.0


        # Slighly low in fat or low part or normal fat
        if self.bodyfat >= normal[0] and self.bodyfat < best:
            return 0.0
        elif self.bodyfat >= normal[3]:
            return 20.0
        else:
            # Sightly high body fat
            if self.bodyfat < normal[3]:
                return self.calculate(self.bodyfat, normal[3], normal[2], 20, 10) + 10.0
            # High part of normal fat
            elif self.bodyfat <= normal[2]:
                return self.calculate(self.bodyfat, normal[2], best, 3, 9) + 3.0
            # Very low in fat
            elif self.bodyfat < normal[0]:
                return self.calculate(self.bodyfat, 1.0, normal[0], 3, 10) + 3.0


    def getMuscleDeductScore():
        normal = []
        if self.sex == 'male':
            if self.height < 160:
                normal = [38.5, 46.6]
            elif self.height < 170:
                normal = [44.0, 52.5]
            else:
                normal = [49.4, 59.5]
        elif self.sex == 'female':
            if self.height < 150:
                normal = [29.1, 34.8]
            elif self.height < 160:
                normal = [32.9, 37.6]
            else:
                normal = [36.5, 42.6]

        # For some reason, there's code to return self.calculate(muscle, normal[0], normal[0]+2.0, 3, 5) + 3.0
        # if your muscle is between normal[0] and normal[0] + 2.0, but it's overwritten with 0.0 before return
        if self.muscle >= normal[0]:
            return 0.0
        elif self.muscle < (normal[0] - 5.0):
            return 10.0
        else:
            return self.calculate(self.muscle, normal[0] - 5.0, normal[0], 10, 5) + 5.0

    # No malus = normal or good; maximum malus (10.0) = less than normal-5.0;
    # malus = between 5 and 10, on your water being between normal-5.0 and normal
    def getWaterDeductScore():
        normal = []
        if self.sex == 'male':
            normal = [55.0, 65.1]
        elif self.sex == 'female':
            normal = [45.0, 60.1]

        if self.water >= normal[0]:
            return 0.0
        elif self.water <= (normal[0] - 5.0):
            return 10.0
        else:
            return self.calculate(self.water, normal[0] - 5.0, normal[0], 10, 5) + 5.0

    # No malus = normal; maximum malus (15.0) = very high; malus = between 10 and 15
    # with your visceral fat in your high range
    def getVisceralFatDeductScore():
        normal = [10.0, 15.0]
        if self.visceral_fat < normal[0]:
            # For some reason, the original app would try to
            # return 3.0 if vfat == 8 and 5.0 if vfat == 9
            # but i's overwritten with 0.0 anyway before return
            return 0.0
        elif self.visceral_fat >= normal[1]:
            return 15.0
        else:
            return self.calculate(self.visceral_fat, normal[1], normal[0], 15, 10) + 10.0

    def getBoneDeductScore():
        normal = []
        if self.sex == 'male':
            if self.weight < 60.0:
                normal = [1.6, 3.9]
            elif self.weight < 75.0:
                normal = [1.9, 4.1]
            else:
                normal = [2.0, 4.2]
        elif self.sex == 'female':
            if self.weight < 45.0:
                normal = [1.3, 3.6]
            elif self.weight < 60.0:
                normal = [1.5, 3.8]
            else:
                normal: [1.8, 3.9]

        if self.bone_mass >= normal[0]:
            return 0.0
        elif self.bone_mass <= (normal[0] - 0.3):
            return 10.0
        else:
            return self.calculate(self.bone_mass, normal[0] - 0.3, normal[0], 10, 5) + 5.0

    def getBasalMetabolismDeductScore():
        # Get normal BMR
        normal = 0
        if sex == 'male':
            if age <= 29:
                normal = 21.6 * self.weight
            elif age <= 49:
                normal = 20.07 * self.weight
            else:
                normal = 19.35 * self.weight
        elif sex == 'female':
            if age <= 29:
                normal = 21.24 * self.weight
            elif age <= 49:
                normal = 19.53 * self.weight
            else:
                normal = 18.63 * self.weight

        if self.basal_metabolism >= normal:
            return 0.0
        elif self.basal_metabolism <= (normal - 300):
            return 6.0
        else:
            # It's really + 5.0 in the app, but it's probably a mistake, should be 3.0
            return self.calculate(self.basal_metabolism, normal - 300, normal, 6, 3) + 5.0


    # Get protein percentage malus
    def getProteinDeductScore():
        # low: 10,16; normal: 16,17
        # Check age or return 0

        # Check limits
        if self.protein > 17.0:
            return 0.0
        elif self.protein < 10.0:
            return 10.0
        else:
            # Return values for low proteins or normal proteins
            if self.protein <= 16.0:
                return self.calculate(self.protein, 10.0, 16.0, 10, 5) + 5.0
            elif self.protein <= 17.0:
                return self.calculate(self.protein, 16.0, 17.0, 5, 3) + 3.0
