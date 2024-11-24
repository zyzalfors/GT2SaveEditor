import binascii, csv, os

class GT2Save:
    N_BLOCKS = 16
    FRAME_SIZE = 128
    GME_HEADER_SIZE = 3904
    BLOCK_SIZE = 8192
    GAME_IDS = {"BESCES-02380GAME": "EU", "BESCES-12380GAME": "EU",
                "BASCUS-94455GAME": "US", "BASCUS-94488GAME": "US",
                "BISCPS-10116GAME": "JP", "BISCPS-10117GAME": "JP"}

    def __init__(self, path):
        self.path = path
        self.isMcr = path.lower().endswith(".mcr")
        self.isGme = path.lower().endswith(".gme")
        self.isPsv = path.lower().endswith(".psv")
        with open(path, "rb") as file: self.bytes = bytearray(file.read())
        self.readInfos()

    def readInfos(self):
        self.infos = []
        if self.isMcr or self.isGme:
            gmeShift = self.GME_HEADER_SIZE if self.isGme else 0
            for i in range(1, self.N_BLOCKS):
                frameOffset = self.FRAME_SIZE * i + gmeShift
                headerBytes = self.bytes[frameOffset:(frameOffset + self.FRAME_SIZE)]
                gameId = headerBytes[10:26].decode("ASCII")
                region = self.GAME_IDS[gameId] if gameId in self.GAME_IDS else "unknown"
                startOffset = self.BLOCK_SIZE * i + gmeShift
                if headerBytes[0] == 0x51 and gameId in self.GAME_IDS: self.infos.append((startOffset, frameOffset + 10, gameId, region))
        elif self.isPsv:
            gameId = self.bytes[100:116].decode("ASCII")
            region = self.GAME_IDS[gameId] if gameId in self.GAME_IDS else "unknown"
            startOffset = self.bytes[68]
            if gameId in self.GAME_IDS: self.infos.append((startOffset, 100, gameId, region))

    LANG_OFFSET = 512
    LANGUAGES = {"ja": 0, "en-us": 1, "en-gb": 2, "fr": 3, "de": 4, "it": 5, "es": 6}

    def getLanguage(self, startOffset):
        langOffset = startOffset + self.LANG_OFFSET
        langByte = self.bytes[langOffset]
        for lang, byte in self.LANGUAGES.items():
            if byte == langByte: return langOffset, lang
        return langOffset, "unknown"

    def updateLanguage(self, startOffset, lang):
        if not lang: return
        langOffset = startOffset + self.LANG_OFFSET
        langByte = self.LANGUAGES[lang] if lang in self.LANGUAGES else None
        self.bytes[langOffset] = langByte

    ARCADE_PROGRESS_OFFSET = 696
    ARCADE_PROGRESS = {"none": 0, "easy": 1, "normal": 2, "hard": 4}
    ARCADE_TRACKS = ["Rome", "Rome Short", "Rome Night", "Seattle", "Seattle Short", "Super Speedway", "Laguna Seca", "Midfield",
                     "Apricot Hill", "Red Rock Valley", "Tahiti Road", "High Speed Ring", "Autumn Ring", "Trial Mountain",
                     "Deep Forest", "Grand Valley", "Grand Valley East", "SSR5", "CSR5", "Grindelwald", "Test Course"]

    def getArcadeProgress(self, startOffset):
        progOffset, progress = startOffset + self.ARCADE_PROGRESS_OFFSET, []
        for i in range(len(self.ARCADE_TRACKS)):
            progByte = self.bytes[progOffset + i]
            for prog, byte in self.ARCADE_PROGRESS.items():
                if byte == progByte: progress.append([self.ARCADE_TRACKS[i], prog])
        return progOffset, progress

    def updateArcadeProgress(self, startOffset, prog):
        if not prog: return
        progOffset = startOffset + self.ARCADE_PROGRESS_OFFSET
        progByte = self.ARCADE_PROGRESS[prog] if prog in self.ARCADE_PROGRESS else None
        for i in range(len(self.ARCADE_TRACKS)): self.bytes[progOffset + i] = progByte

    DAYS_OFFSET = 760
    DAYS_SIZE = 4

    def getDays(self, startOffset):
        daysOffset = startOffset + self.DAYS_OFFSET
        daysBytes = self.bytes[daysOffset:(daysOffset + self.DAYS_SIZE)]
        return daysOffset, int.from_bytes(daysBytes, byteorder = "little", signed = True)

    def updateDays(self, startOffset, days):
        if not days: return
        daysOffset = startOffset + self.DAYS_OFFSET
        daysBytes = int(days).to_bytes(self.DAYS_SIZE, byteorder = "little", signed = True)
        for i in range(self.DAYS_SIZE): self.bytes[daysOffset + i] = daysBytes[i]

    TOT_RACES_OFFSET = 768
    TOT_RACES_SIZE = 4

    def getTotRaces(self, startOffset):
        totRacesOffset = startOffset + self.TOT_RACES_OFFSET
        totRacesBytes = self.bytes[totRacesOffset:(totRacesOffset + self.TOT_RACES_SIZE)]
        return totRacesOffset, int.from_bytes(totRacesBytes, byteorder = "little", signed = True)

    def updateTotRaces(self, startOffset, totRaces):
        if not totRaces: return
        totRacesOffset = startOffset + self.TOT_RACES_OFFSET
        totRacesBytes = int(totRaces).to_bytes(self.TOT_RACES_SIZE, byteorder = "little", signed = True)
        for i in range(self.TOT_RACES_SIZE): self.bytes[totRacesOffset + i] = totRacesBytes[i]

    TOT_WINS_OFFSET = 772
    TOT_WINS_SIZE = 4

    def getTotWins(self, startOffset):
        totWinsOffset = startOffset + self.TOT_WINS_OFFSET
        totWinsBytes = self.bytes[totWinsOffset:(totWinsOffset + self.TOT_WINS_SIZE)]
        return totWinsOffset, int.from_bytes(totWinsBytes, byteorder = "little", signed = True)

    def updateTotWins(self, startOffset, totWins):
        if not totWins: return
        totWinsOffset = startOffset + self.TOT_WINS_OFFSET
        totWinsBytes = int(totWins).to_bytes(self.TOT_WINS_SIZE, byteorder = "little", signed = True)
        for i in range(self.TOT_WINS_SIZE): self.bytes[totWinsOffset + i] = totWinsBytes[i]

    TOT_PRIZE_OFFSET = 788
    TOT_PRIZE_SIZE = 4

    def getTotPrize(self, startOffset):
        totPrizeOffset = startOffset + self.TOT_PRIZE_OFFSET
        totPrizeBytes = self.bytes[totPrizeOffset:(totPrizeOffset + self.TOT_PRIZE_SIZE)]
        return totPrizeOffset, int.from_bytes(totPrizeBytes, byteorder = "little", signed = True)

    def updateTotPrize(self, startOffset, totPrize):
        if not totPrize: return
        totPrizeOffset = startOffset + self.TOT_PRIZE_OFFSET
        totPrizeBytes = int(totPrize).to_bytes(self.TOT_PRIZE_SIZE, byteorder = "little", signed = True)
        for i in range(self.TOT_PRIZE_SIZE): self.bytes[totPrizeOffset + i] = totPrizeBytes[i]

    CAREER_PROGRESS_OFFSET = 792
    N_CAREER_EVENTS = 248
    CAREER_PROGRESS = {"none": 0, "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6}

    def getCareerProgress(self, startOffset):
        progOffset, progress = startOffset + self.CAREER_PROGRESS_OFFSET, []
        for i in range(int(self.N_CAREER_EVENTS / 2)):
            progByte = self.bytes[progOffset + i]
            progVal1 = progByte & 0x0F
            progVal2 = (progByte & 0xF0) >> 4
            for prog, val in self.CAREER_PROGRESS.items():
                if val == progVal1: progress.append(prog)
            for prog, val in self.CAREER_PROGRESS.items():
                if val == progVal2: progress.append(prog)
        return progOffset, progress

    def updateCareerProgress(self, startOffset, prog):
        if not prog: return
        progOffset = startOffset + self.CAREER_PROGRESS_OFFSET
        progVal1 = self.CAREER_PROGRESS[prog] if prog in self.CAREER_PROGRESS else None
        progVal2 = progVal1
        for i in range(int(self.N_CAREER_EVENTS / 2)): self.bytes[progOffset + i] = (progVal2 << 4) | progVal1

    LICENSE_OFFSETS = {"S": 5657, "IA": 7297, "IB": 8937, "IC": 10577, "A": 12217, "B": 13857}
    N_TESTS_PER_LICENSE = 10
    LICENSE_SKIP = 164
    LICENSES = {"none": 0, "kid": 1, "bronze": 2, "silver": 3, "gold": 4}

    def getLicenses(self, startOffset):
        licenses = []
        for lic in self.LICENSE_OFFSETS:
            licOffset = startOffset + self.LICENSE_OFFSETS[lic]
            data = [str(licOffset), lic]
            for i in range(self.N_TESTS_PER_LICENSE):
                licByte, licType = self.bytes[licOffset + self.LICENSE_SKIP * i], "unknown"
                for type, byte in self.LICENSES.items():
                    if byte == licByte: licType = type
                data.append(licType)
            licenses.append(data)
        return licenses

    def updateLicenses(self, startOffset, licType):
        if not licType: return
        firstLicOffset = startOffset + self.LICENSE_OFFSETS["S"]
        licByte = self.LICENSES[licType] if licType in self.LICENSES else None
        for i in range(self.N_TESTS_PER_LICENSE * len(self.LICENSE_OFFSETS)): self.bytes[firstLicOffset + self.LICENSE_SKIP * i] = licByte

    CAR_COUNT_OFFSET = 15988
    MAX_CAR_COUNT = 100

    def getCarCount(self, startOffset):
        carCountOffset = startOffset + self.CAR_COUNT_OFFSET
        return carCountOffset, self.bytes[carCountOffset]

    FIRST_CAR_OFFSET = 15992
    CAR_SIZE = 164
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

    def getCarName(self, carData, carCode, region):
        for data in carData:
            if data[0] == carCode and region == "EU": return data[1]
            elif data[0] == carCode and region == "US": return data[2]
            elif data[0] == carCode and region == "JP": return data[3]
        return "unknown"

    def getCars(self, startOffset):
        cars = []
        _, carCount = self.getCarCount(startOffset)
        if carCount == 0: return cars
        info = next(entry for entry in self.infos if entry[0] == startOffset)
        region, carData = info[3], None
        with open(self.CARS_DB_PATH, encoding = "UTF-8", newline = "") as file: carData = list(csv.reader(file, delimiter = ","))
        for i in range(carCount):
            carOffset = startOffset + self.FIRST_CAR_OFFSET + self.CAR_SIZE * i
            carBytes = self.bytes[carOffset:(carOffset + self.CAR_SIZE)]
            data = [str(carOffset), str(i)]
            for attr in self.CAR_PROPERTY_ATTRIBUTES: data.append(binascii.hexlify(carBytes[attr[0]:(attr[0] + attr[1])]).decode("ASCII").upper())
            carName = self.getCarName(carData, data[66], region)
            data.insert(2, carName)
            cars.append(data)
        return cars

    def updateCar(self, startOffset, carIndex, carPropNames, carPropValues):
        if not carIndex or not carPropNames or not carPropValues: return
        index = int(carIndex)
        _, carCount = self.getCarCount(startOffset)
        if index < 0 or index > carCount - 1: return
        carOffset = startOffset + self.FIRST_CAR_OFFSET + self.CAR_SIZE * index
        for i in range(len(carPropNames)):
            propAttributes = self.CAR_PROPERTY_ATTRIBUTES[self.CAR_PROPERTY_NAMES.index(carPropNames[i])]
            propOffset = propAttributes[0]
            propValue = binascii.unhexlify(carPropValues[i])
            propSize = min([propAttributes[1], len(propValue)])
            for j in range(propSize): self.bytes[carOffset + propOffset + j] = propValue[j]

    CASH_OFFSET = 32392
    CASH_SIZE = 4

    def getCash(self, startOffset):
        cashOffset = startOffset + self.CASH_OFFSET
        cashBytes = self.bytes[cashOffset:(cashOffset + self.CASH_SIZE)]
        return cashOffset, int.from_bytes(cashBytes, byteorder = "little", signed = True)

    def updateCash(self, startOffset, cash):
        if not cash: return
        cashOffset = startOffset + self.CASH_OFFSET
        cashBytes = int(cash).to_bytes(self.CASH_SIZE, byteorder = "little", signed = True)
        for i in range(self.CASH_SIZE): self.bytes[cashOffset + i] = cashBytes[i]

    CURR_CAR_OFFSET = 32396

    def getCurrCar(self, startOffset):
        currCarOffset = startOffset + self.CURR_CAR_OFFSET
        return currCarOffset, self.bytes[currCarOffset]

    def updateCurrCar(self, startOffset, carIndex):
        if not carIndex: return
        index = int(carIndex)
        _, carCount = self.getCarCount(startOffset)
        if carCount == 0: return
        if index < 0 or index > carCount - 1: index = 255
        currCarOffset = startOffset + self.CURR_CAR_OFFSET
        self.bytes[currCarOffset] = index

    CRC32_OFFSET = 32412
    CRC32_SIZE = 4

    def getCrc32(self, startOffset):
        crc32Offset = startOffset + self.CRC32_OFFSET
        crc32Bytes = self.bytes[crc32Offset:(crc32Offset + self.CRC32_SIZE)]
        return crc32Offset, int.from_bytes(crc32Bytes, byteorder = "little")

    def updateCrc32(self, startOffset):
        crc32Offset = startOffset + self.CRC32_OFFSET
        saveBytes = self.bytes[startOffset:crc32Offset]
        crc32Bytes = binascii.crc32(saveBytes).to_bytes(self.CRC32_SIZE, byteorder = "little")
        for i in range(self.CRC32_SIZE): self.bytes[crc32Offset + i] = crc32Bytes[i]

    def read(self, saveIndex):
        for i in range(len(self.infos)):
            if saveIndex and i != int(saveIndex): continue
            info = self.infos[i]
            startOffset, gameIdOffset, gameId, region = info[0], info[1], info[2], info[3]
            print("Start offset: ", startOffset, sep = "")
            print("Game Id at ", gameIdOffset, ": ", gameId, sep = "")
            print("Region: ", region, sep = "")
            crc32Offset, crc32 = self.getCrc32(startOffset)
            print("CRC32 at ", crc32Offset, ": ", crc32, sep = "")
            cashOffset, cash = self.getCash(startOffset)
            print("Cash at ", cashOffset, ": ", cash, sep = "")
            langOffset, lang = self.getLanguage(startOffset)
            print("Language at ", langOffset, ": ", lang, sep = "")
            daysOffset, days = self.getDays(startOffset)
            print("Days at ", daysOffset, ": ", days, sep = "")
            totRacesOffset, totRaces = self.getTotRaces(startOffset)
            print("Total races at ", totRacesOffset, ": ", totRaces, sep = "")
            totWinsOffset, totWins = self.getTotWins(startOffset)
            print("Total wins at ", totWinsOffset, ": ", totWins, sep = "")
            totPrizeOffset, totPrize = self.getTotPrize(startOffset)
            print("Total prize at ", totPrizeOffset, ": ", totPrize, sep = "")
            arcadeProgOffset, arcadeProgress = self.getArcadeProgress(startOffset)
            licenses = self.getLicenses(startOffset)
            for lic in licenses: print("License ", lic[1], " at ", lic[0], ": ", ",".join(lic[2:]), sep = "")
            print("Arcade progress at ", arcadeProgOffset, ":", sep = "")
            for prog in arcadeProgress: print(prog[0], ": ", prog[1], sep = "")
            careerProgOffset, careerProgress = self.getCareerProgress(startOffset)
            print("Career progress at ", careerProgOffset, ": ", ",".join(careerProgress), sep = "")
            carCountOffset, carCount = self.getCarCount(startOffset)
            print("Car count at ", carCountOffset, ": ", carCount, sep = "")
            currCarOffset, currCar = self.getCurrCar(startOffset)
            if currCar < self.MAX_CAR_COUNT: print("Current car at ", currCarOffset, ": ", currCar, sep = "")
            else: print("Current car at ", currCarOffset, ": none", sep = "")
            cars = self.getCars(startOffset)
            if len(cars) > 0: print("Offset,", "Index,", "CarName,", ",".join(list(self.CAR_PROPERTIES.keys())), sep = "")
            for car in cars: print(",".join(car))

    def update(self, saveIndex, vals):
        for i in range(len(self.infos)):
            if saveIndex and i != int(saveIndex): continue
            info = self.infos[i]
            startOffset = info[0]
            self.updateLanguage(startOffset, vals.lang)
            self.updateArcadeProgress(startOffset, vals.aprog)
            self.updateDays(startOffset, vals.days)
            self.updateTotRaces(startOffset, vals.races)
            self.updateTotWins(startOffset, vals.wins)
            self.updateTotPrize(startOffset, vals.prize)
            self.updateCareerProgress(startOffset, vals.cprog)
            self.updateLicenses(startOffset, vals.lic)
            self.updateCar(startOffset, vals.car, vals.prop, vals.val)
            self.updateCash(startOffset, vals.cash)
            self.updateCurrCar(startOffset, vals.curr)
            self.updateCrc32(startOffset)
        with open(self.path, "wb") as file: file.write(self.bytes)