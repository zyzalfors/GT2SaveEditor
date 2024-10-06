import binascii, csv, os

class GT2Save:
    N_BLOCKS = 15
    RAW_HEADER_SIZE = 128
    GME_HEADER_SIZE = 3904
    DAYS_SIZE = 4
    TOT_RACES_SIZE = 4
    TOT_WINS_SIZE = 4
    TOT_PRIZE_SIZE = 4
    CAR_SIZE = 164
    CASH_SIZE = 4
    CRC32_SIZE = 4
    N_LICENSES = 6
    N_TESTS_PER_LICENSE = 10
    LICENSE_SKIP = 164
    MAX_CAR_COUNT = 100
    FIRST_BLOCK_OFFSET = 8192
    LANG_OFFSET = 512
    DAYS_OFFSET = 760
    TOT_RACES_OFFSET = 768
    TOT_WINS_OFFSET = 772
    TOT_PRIZE_OFFSET = 788
    LICENSE_OFFSETS = {"S": 5657, "IA": 7297, "IB": 8937, "IC": 10577, "A": 12217, "B": 13857}
    CAR_COUNT_OFFSET = 15988
    FIRST_CAR_OFFSET = 15992
    CASH_OFFSET = 32392
    CURR_CAR_OFFSET = 32396
    CRC32_OFFSET = 32412
    GAME_IDS = ["BESCES-02380GAME", "BESCES-12380GAME", "BASCUS-94455GAME", "BASCUS-94488GAME", "BISCPS-10116GAME", "BISCPS-10117GAME"]
    CAR_PROPERTIES = {
        "CarCode1": [0, 4],
        "ColorCode": [4, 1],
        "RimsCode1": [8, 4],
        "BrakesCode": [12, 2],
        "BrakesControllerCode": [14, 2],
        "BodyModifier": [18, 2],
        "EngineCode": [20, 2],
        "DrivetrainModifierCode": [22, 2],
        "TransmissionCode": [24, 2],
        "SuspensionCode": [26, 2],
        "LSDYawControlCode": [28, 2],
        "FrontTiresCode": [30, 2],
        "RearTiresCode": [32, 2],
        "WeightReductionCode": [34, 2],
        "RaceModifiedCode": [36, 2],
        "PortPolishCode": [38, 2],
        "EngineBalanceCode": [40, 2],
        "DisplacementIncreaseCode": [42, 2],
        "ComputerROMCode": [44, 2],
        "NAUpgradeCode": [46, 2],
        "TurboCode": [48, 2],
        "FlywheelCode": [50, 2],
        "ClutchCode": [52, 2],
        "DriveshaftCode": [54, 2],
        "ExhaustCode": [56, 2],
        "IntercoolerCode": [58, 2],
        "ASCCode": [60, 2],
        "TCSCode": [62, 2],
        "RimsCode2": [64, 2],
        "PowerMultiplierCode": [66, 2],
        "ReverseGearCode": [68, 2],
        "FirstGearCode": [70, 2],
        "SecondGearCode": [72, 2],
        "ThirdGearCode": [74, 2],
        "FourthGearCode": [76, 2],
        "FifthGearCode": [78, 2],
        "SixthGearCode": [80, 2],
        "SeventhGearCode": [82, 2],
        "FinalDriveCode": [84, 2],
        "AutoGearCode": [86, 2],
        "BrakeControlSettingsCode": [88, 2],
        "FrontDownforceCode": [90, 1],
        "RearDownforceCode": [91, 1],
        "TurboBlowoffCode": [92, 2],
        "TurboGaugeCode": [94, 2],
        "CamberCode": [98, 2],
        "FrontHeightCode": [100, 1],
        "RearHeightCode": [101, 1],
        "ToeCode": [102, 2],
        "SpringRateCode": [104, 2],
        "FrontBoundCode": [108, 2],
        "FrontReboundCode": [110, 2],
        "RearBoundCode": [112, 2],
        "RearReboundCode": [114, 2],
        "FrontStabilizerCode": [116, 1],
        "RearStabilizerCode": [117, 1],
        "LSDYawSystemCode": [118, 2],
        "LSDYawAccelCode": [120, 2],
        "LSDYawDecelCode": [122, 2],
        "ASCTCSSettingCode": [124, 2],
        "TunerCode": [129, 1],
        "GearModifierCode": [130, 2],
        "FinalDriveSettingCode": [132, 2],
        "ModGearsIndicatorCode": [134, 1],
        "CarCode2": [140, 4],
        "CarPriceCode": [144, 4],
        "WeightDrivetrainCode": [148, 2],
        "TorqueCode": [150, 2],
        "HorsepowerCode": [152, 2],
        "FitmentCode1": [154, 2],
        "FitmentCode2": [156, 2],
        "FitmentCode3": [158, 2],
        "FitmentCode4": [160, 1],
        "CleanlinessCode": [162, 2]
    }
    CAR_PROPERTY_NAMES = [entry.lower() for entry in list(CAR_PROPERTIES.keys())]
    CAR_PROPERTY_ATTRIBUTES = list(CAR_PROPERTIES.values())
    CARS_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carsDB.csv")

    def __init__(self, path):
        self.path = path
        self.isMcr = path.lower().endswith(".mcr")
        self.isGme = path.lower().endswith(".gme")
        self.isPsv = path.lower().endswith(".psv")
        with open(path, "rb") as file: self.rawBytes = bytearray(file.read())
        self.readInfos()

    def getRegion(self, gameId):
        if gameId.startswith("BE"): return "EU"
        elif gameId.startswith("BA"): return "US"
        elif gameId.startswith("BI"): return "JP"
        return ""

    def readInfos(self):
        self.infos = []
        if self.isMcr or self.isGme:
            gmeShift = self.GME_HEADER_SIZE if self.isGme else 0
            for i in range(1, self.N_BLOCKS + 1):
                headerOffset = self.RAW_HEADER_SIZE * i + gmeShift
                headerBytes = self.rawBytes[headerOffset:(headerOffset + self.RAW_HEADER_SIZE)]
                gameId = headerBytes[10:26].decode("ASCII")
                region = self.getRegion(gameId)
                startOffset = self.FIRST_BLOCK_OFFSET * i + gmeShift
                if headerBytes[0] == 0x51 and gameId in self.GAME_IDS: self.infos.append((startOffset, headerOffset + 10, gameId, region))
        elif self.isPsv:
            gameId = self.rawBytes[100:116].decode("ASCII")
            region = self.getRegion(gameId)
            startOffset = self.rawBytes[68]
            if gameId in self.GAME_IDS: self.infos.append((startOffset, 100, gameId, region))

    def getCash(self, startOffset):
        cashOffset = startOffset + self.CASH_OFFSET
        cashBytes = self.rawBytes[cashOffset:(cashOffset + self.CASH_SIZE)]
        return cashOffset, int.from_bytes(cashBytes, byteorder = "little", signed = True)

    def getLanguage(self, startOffset):
        langOffset = startOffset + self.LANG_OFFSET
        val, lang = self.rawBytes[langOffset], ""
        match val:
            case 0: lang = "JA"
            case 1: lang = "EN-US"
            case 2: lang = "EN-GB"
            case 3: lang = "FR"
            case 4: lang = "DE"
            case 5: lang = "IT"
            case 6: lang = "ES"
        return langOffset, lang

    def getDays(self, startOffset):
        daysOffset = startOffset + self.DAYS_OFFSET
        daysBytes = self.rawBytes[daysOffset:(daysOffset + self.DAYS_SIZE)]
        return daysOffset, int.from_bytes(daysBytes, byteorder = "little", signed = True)

    def getTotRaces(self, startOffset):
        totRacesOffset = startOffset + self.TOT_RACES_OFFSET
        totRacesBytes = self.rawBytes[totRacesOffset:(totRacesOffset + self.TOT_RACES_SIZE)]
        return totRacesOffset, int.from_bytes(totRacesBytes, byteorder = "little", signed = True)

    def getTotWins(self, startOffset):
        totWinsOffset = startOffset + self.TOT_WINS_OFFSET
        totWinsBytes = self.rawBytes[totWinsOffset:(totWinsOffset + self.TOT_WINS_SIZE)]
        return totWinsOffset, int.from_bytes(totWinsBytes, byteorder = "little", signed = True)

    def getTotPrize(self, startOffset):
        totPrizeOffset = startOffset + self.TOT_PRIZE_OFFSET
        totPrizeBytes = self.rawBytes[totPrizeOffset:(totPrizeOffset + self.TOT_PRIZE_SIZE)]
        return totPrizeOffset, int.from_bytes(totPrizeBytes, byteorder = "little", signed = True)

    def getLicenses(self, startOffset):
        licenses = []
        for license in self.LICENSE_OFFSETS:
            licenseOffset = startOffset + self.LICENSE_OFFSETS[license]
            data = [str(licenseOffset), license]
            for i in range(self.N_TESTS_PER_LICENSE):
                val, licenseType = self.rawBytes[licenseOffset + self.LICENSE_SKIP * i], ""
                match val:
                    case 0: licenseType = "none"
                    case 1: licenseType = "kid"
                    case 2: licenseType = "bronze"
                    case 3: licenseType = "silver"
                    case 4: licenseType = "gold"
                data.append(licenseType)
            licenses.append(data)
        return licenses

    def getCurrCar(self, startOffset):
        currCarOffset = startOffset + self.CURR_CAR_OFFSET
        return currCarOffset, self.rawBytes[currCarOffset]

    def getCarCount(self, startOffset):
        carCountOffset = startOffset + self.CAR_COUNT_OFFSET
        return carCountOffset, self.rawBytes[carCountOffset]

    def getCars(self, startOffset):
        cars = []
        _, carCount = self.getCarCount(startOffset)
        if carCount == 0: return cars
        info = next(entry for entry in self.infos if entry[0] == startOffset)
        region, carData = info[3], None
        with open(self.CARS_DB_PATH, encoding = "UTF-8", newline = "") as file: carData = list(csv.reader(file, delimiter = ","))
        for i in range(carCount):
            carOffset = startOffset + self.FIRST_CAR_OFFSET + self.CAR_SIZE * i
            carBytes = self.rawBytes[carOffset:(carOffset + self.CAR_SIZE)]
            data = [str(carOffset), str(i)]
            for attribute in self.CAR_PROPERTY_ATTRIBUTES: data.append(binascii.hexlify(carBytes[attribute[0]:(attribute[0] + attribute[1])]).decode("ASCII").upper())
            carName = self.getCarName(carData, data[66], region)
            data.insert(2, carName)
            cars.append(data)
        return cars

    def getCarName(self, carData, carCode, region):
        for data in carData:
            if data[0] == carCode and region == "EU": return data[1]
            elif data[0] == carCode and region == "US": return data[2]
            elif data[0] == carCode and region == "JP": return data[3]
        return ""

    def getCrc32(self, startOffset):
        crc32Offset = startOffset + self.CRC32_OFFSET
        crc32Bytes = self.rawBytes[crc32Offset:(crc32Offset + self.CRC32_SIZE)]
        return crc32Offset, int.from_bytes(crc32Bytes, byteorder = "little")

    def updateCash(self, startOffset, cash):
        if not cash: return
        cashOffset = startOffset + self.CASH_OFFSET
        cashBytes = int(cash).to_bytes(self.CASH_SIZE, byteorder = "little", signed = True)
        for i in range(self.CASH_SIZE): self.rawBytes[cashOffset + i] = cashBytes[i]

    def updateLanguage(self, startOffset, lang):
        if not lang: return
        langOffset, val = startOffset + self.LANG_OFFSET, None
        match lang:
            case "ja": val = 0
            case "en-us": val = 1
            case "en-gb": val = 2
            case "fr": val = 3
            case "de": val = 4
            case "it": val = 5
            case "es": val = 6
        self.rawBytes[langOffset] = val

    def updateDays(self, startOffset, days):
        if not days: return
        daysOffset = startOffset + self.DAYS_OFFSET
        daysBytes = int(days).to_bytes(self.DAYS_SIZE, byteorder = "little", signed = True)
        for i in range(self.DAYS_SIZE): self.rawBytes[daysOffset + i] = daysBytes[i]

    def updateTotRaces(self, startOffset, totRaces):
        if not totRaces: return
        totRacesOffset = startOffset + self.TOT_RACES_OFFSET
        totRacesBytes = int(totRaces).to_bytes(self.TOT_RACES_SIZE, byteorder = "little", signed = True)
        for i in range(self.TOT_RACES_SIZE): self.rawBytes[totRacesOffset + i] = totRacesBytes[i]

    def updateTotWins(self, startOffset, totWins):
        if not totWins: return
        totWinsOffset = startOffset + self.TOT_WINS_OFFSET
        totWinsBytes = int(totWins).to_bytes(self.TOT_WINS_SIZE, byteorder = "little", signed = True)
        for i in range(self.TOT_WINS_SIZE): self.rawBytes[totWinsOffset + i] = totWinsBytes[i]

    def updateTotPrize(self, startOffset, totPrize):
        if not totPrize: return
        totPrizeOffset = startOffset + self.TOT_PRIZE_OFFSET
        totPrizeBytes = int(totPrize).to_bytes(self.TOT_PRIZE_SIZE, byteorder = "little", signed = True)
        for i in range(self.TOT_PRIZE_SIZE): self.rawBytes[totPrizeOffset + i] = totPrizeBytes[i]

    def updateLicenses(self, startOffset, licenseType):
        if not licenseType: return
        firstLicenseOffset, val = startOffset + self.LICENSE_OFFSETS["S"], None
        match licenseType:
            case "none": val = 0
            case "kid": val = 1
            case "bronze": val = 2
            case "silver": val = 3
            case "gold": val = 4
        for i in range(self.N_TESTS_PER_LICENSE * self.N_LICENSES): self.rawBytes[firstLicenseOffset + self.LICENSE_SKIP * i] = val

    def updateCurrCar(self, startOffset, carIndex):
        if not carIndex: return
        index = int(carIndex)
        _, carCount = self.getCarCount(startOffset)
        if carCount == 0: return
        if index < 0 or index > carCount - 1: index = 255
        currCarOffset = startOffset + self.CURR_CAR_OFFSET
        self.rawBytes[currCarOffset] = index

    def updateCar(self, startOffset, carIndex, carPropertyNames, carPropertyValues):
        if not carIndex or not carPropertyNames or not carPropertyValues: return
        index = int(carIndex)
        _, carCount = self.getCarCount(startOffset)
        if index < 0 or index > carCount - 1: return
        carOffset = startOffset + self.FIRST_CAR_OFFSET + self.CAR_SIZE * index
        for i in range(len(carPropertyNames)):
            propertyAttributes = self.CAR_PROPERTY_ATTRIBUTES[self.CAR_PROPERTY_NAMES.index(carPropertyNames[i])]
            propertyOffset = propertyAttributes[0]
            propertyValue = binascii.unhexlify(carPropertyValues[i])
            size = min([propertyAttributes[1], len(propertyValue)])
            for j in range(size): self.rawBytes[carOffset + propertyOffset + j] = propertyValue[j]

    def updateCrc32(self, startOffset):
        crc32Offset = startOffset + self.CRC32_OFFSET
        saveBytes = self.rawBytes[startOffset:crc32Offset]
        crc32Bytes = binascii.crc32(saveBytes).to_bytes(self.CRC32_SIZE, byteorder = "little")
        for i in range(self.CRC32_SIZE): self.rawBytes[crc32Offset + i] = crc32Bytes[i]

    def update(self, saveIndex, vals):
        for i in range(len(self.infos)):
            if saveIndex and i != int(saveIndex): continue
            info = self.infos[i]
            startOffset = info[0]
            self.updateCash(startOffset, vals.cash)
            self.updateLanguage(startOffset, vals.lang)
            self.updateDays(startOffset, vals.days)
            self.updateTotRaces(startOffset, vals.races)
            self.updateTotWins(startOffset, vals.wins)
            self.updateTotPrize(startOffset, vals.prize)
            self.updateLicenses(startOffset, vals.lic)
            self.updateCurrCar(startOffset, vals.curr)
            self.updateCar(startOffset, vals.car, vals.prop, vals.val)
            self.updateCrc32(startOffset)

    def print(self, saveIndex):
        for i in range(len(self.infos)):
            if saveIndex and i != int(saveIndex): continue
            info = self.infos[i]
            startOffset, gameIdOffset, gameId, region = info[0], info[1], info[2], info[3]
            crc32Offset, crc32 = self.getCrc32(startOffset)
            cashOffset, cash = self.getCash(startOffset)
            langOffset, lang = self.getLanguage(startOffset)
            daysOffset, days = self.getDays(startOffset)
            totRacesOffset, totRaces = self.getTotRaces(startOffset)
            totWinsOffset, totWins = self.getTotWins(startOffset)
            totPrizeOffset, totPrize = self.getTotPrize(startOffset)
            licenses = self.getLicenses(startOffset)
            carCountOffset, carCount = self.getCarCount(startOffset)
            currCarOffset, currCar = self.getCurrCar(startOffset)
            cars = self.getCars(startOffset)
            print("Game Id at ", gameIdOffset, ": ", gameId, sep = "")
            print("Region: ", region, sep = "")
            print("CRC32 at ", crc32Offset, ": ", crc32, sep = "")
            print("Cash at ", cashOffset, ": ", cash, sep = "")
            print("Language at ", langOffset, ": ", lang, sep = "")
            print("Days at ", daysOffset, ": ", days, sep = "")
            print("Total races at ", totRacesOffset, ": ", totRaces, sep = "")
            print("Total wins at ", totWinsOffset, ": ", totWins, sep = "")
            print("Total prize at ", totPrizeOffset, ": ", totPrize, sep = "")
            for license in licenses: print("License ", license[1], " at ", license[0], ": ", ",".join(license[2:]), sep = "")
            print("Car count at ", carCountOffset, ": ", carCount, sep = "")
            if currCar < self.MAX_CAR_COUNT: print("Current car at ", currCarOffset, ": ", currCar, sep = "")
            else: print("Current car at ", currCarOffset, ": none", sep = "")
            if len(cars) > 0: print("Offset,", "Index,", "CarName,", ",".join(list(self.CAR_PROPERTIES.keys())), sep = "")
            for car in cars: print(",".join(car))

    def save(self, newPath):
        with open(newPath, "wb") as file: file.write(self.rawBytes)