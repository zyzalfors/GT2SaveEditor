import binascii, csv, os

class GT2Save:
    BLOCKS = 16
    BLOCK_SIZE = 8192

    HEADER_SIZE = 128
    GME_HEADER_SIZE = 3904

    GAME_IDS = {"BESCES-02380GAME": "EU", "BESCES-12380GAME": "EU",
                "BASCUS-94455GAME": "US", "BASCUS-94488GAME": "US",
                "BISCPS-10116GAME": "JP", "BISCPS-10117GAME": "JP"}

    LANG_OFFSET = 512
    LANGUAGES = {"ja": 0, "en-us": 1, "en-gb": 2, "fr": 3, "de": 4, "it": 5, "es": 6}

    ARCADE_PROGRESS_OFFSET = 696
    ARCADE_PROGRESS = {"none": 0, "easy": 1, "normal": 2, "hard": 4}
    ARCADE_TRACKS = ["Rome", "Rome Short", "Rome Night", "Seattle", "Seattle Short", "Super Speedway", "Laguna Seca",
                     "Midfield", "Apricot Hill", "Red Rock Valley", "Tahiti Road", "High Speed Ring", "Autumn Ring", "Trial Mountain",
                     "Deep Forest", "Grand Valley", "Grand Valley East", "Special Stage Route 5", "Clubman Stage Route 5", "Grindelwald", "Test Course"]

    DAYS_OFFSET = 760
    DAYS_SIZE = 4

    RACES_OFFSET = 768
    RACES_SIZE = 4

    WINS_OFFSET = 772
    WINS_SIZE = 4

    SUM_OF_BEST_RANKINGS_OFFSET = 776
    SUM_OF_BEST_RANKINGS_SIZE = 4

    SUM_OF_RANKINGS_OFFSET = 780
    SUM_OF_RANKINGS_SIZE = 4

    PRIZE_OFFSET = 788
    PRIZE_SIZE = 4

    CAREER_PROGRESS_OFFSET = 792
    CAREER_PROGRESS = {"none": 0, "1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6}
    CAREER_EVENTS = 248
    CAREER_EVENTS_FOR_100 = 219

    ENDING_MOVIE_OFFSET = 1045
    ENDING_MOVIE_SIZE = 1

    LICENSE_OFFSETS = {"S": 5657, "IA": 7297, "IB": 8937, "IC": 10577, "A": 12217, "B": 13857}
    LICENSE_PROGRESS = {"none": 0, "kid": 1, "bronze": 2, "silver": 3, "gold": 4}
    TESTS_PER_LICENSE = 10
    LICENSE_SKIP = 164

    CAR_COUNT_OFFSET = 15988
    CAR_COUNT_SIZE = 1
    MAX_CAR_COUNT = 100

    FIRST_CAR_OFFSET = 15992
    CAR_SIZE = 164
    CAR_PROPERTIES = {"Code": (0, 4)}
    CARS_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carsDB.csv")

    MONEY_OFFSET = 32392
    MONEY_SIZE = 4

    CURR_CAR_OFFSET = 32396
    CURR_CAR_SIZE = 1

    CRC32_OFFSET = 32412
    CRC32_SIZE = 4

    INVALID_STR = "invalid"


    def __init__(self, path):
        self.path = path
        path = path.lower()

        self.isMcr = path.endswith(".mcr")
        self.isGme = path.endswith(".gme")
        self.isPsv = path.endswith(".psv")

        with open(path, "rb") as f:
            self.bytes = bytearray(f.read())

        self.readBlocks()


    def readBlocks(self):
        self.blocks = []

        if self.isMcr or self.isGme:
            gmeShift = self.GME_HEADER_SIZE if self.isGme else 0

            for i in range(1, self.BLOCKS):
                headerOffset = self.HEADER_SIZE * i + gmeShift
                headerBytes = self.bytes[headerOffset:(headerOffset + self.HEADER_SIZE)]
                gameId = headerBytes[10:26].decode("ASCII")

                if headerBytes[0] == 0x51 and gameId in self.GAME_IDS:
                    startOffset = self.BLOCK_SIZE * i + gmeShift
                    region = self.GAME_IDS[gameId]
                    self.blocks.append((startOffset, headerOffset + 10, gameId, region))

        elif self.isPsv:
            gameId = self.bytes[100:116].decode("ASCII")

            if gameId in self.GAME_IDS:
                startOffset = self.bytes[68]
                region = self.GAME_IDS[gameId]
                self.blocks.append((startOffset, 100, gameId, region))


    def getLang(self, startOffset):
        offset = startOffset + self.LANG_OFFSET
        byte = self.bytes[offset]
        return offset, next((lang for lang, langByte in self.LANGUAGES.items() if byte == langByte), self.INVALID_STR)


    def updateLang(self, startOffset, lang):
        if not lang in self.LANGUAGES:
            return

        self.bytes[startOffset + self.LANG_OFFSET] = self.LANGUAGES[lang]


    def getArcadeProg(self, startOffset):
        offset = startOffset + self.ARCADE_PROGRESS_OFFSET
        progress = []

        for i in range(len(self.ARCADE_TRACKS)):
            byte = self.bytes[offset + i]
            prog = next((prog for prog, progByte in self.ARCADE_PROGRESS.items() if byte == progByte), self.INVALID_STR)
            progress.append((self.ARCADE_TRACKS[i], prog))

        return offset, progress


    def updateArcadeProg(self, startOffset, prog):
        if not prog in self.ARCADE_PROGRESS:
            return

        offset = startOffset + self.ARCADE_PROGRESS_OFFSET
        byte = self.ARCADE_PROGRESS[prog]

        for i in range(len(self.ARCADE_TRACKS)):
            self.bytes[offset + i] = byte


    def getVal(self, startOffset, valOffset, valSize, signed):
        offset = startOffset + valOffset
        bytes = self.bytes[offset:(offset + valSize)]
        return offset, int.from_bytes(bytes, byteorder = "little", signed = signed)


    def updateVal(self, startOffset, valOffset, valSize, signed, val):
        if not val:
            return

        offset = startOffset + valOffset
        bytes = int(val).to_bytes(valSize, byteorder = "little", signed = signed)

        for i in range(valSize):
            self.bytes[offset + i] = bytes[i]


    def getCareerProg(self, startOffset):
        offset = startOffset + self.CAREER_PROGRESS_OFFSET
        progress = []
        completion = 0

        for i in range(int(self.CAREER_EVENTS / 2)):
            byte = self.bytes[offset + i]

            nibble = byte & 0x0F
            ranking = next((prog for prog, progNibble in self.CAREER_PROGRESS.items() if nibble == progNibble), self.INVALID_STR)
            progress.append(ranking)

            if ranking != self.INVALID_STR and nibble != 0:
                completion += 1 / nibble

            nibble = (byte & 0xF0) >> 4
            ranking = next((prog for prog, progNibble in self.CAREER_PROGRESS.items() if nibble == progNibble), self.INVALID_STR)
            progress.append(ranking)

            if ranking != self.INVALID_STR and nibble != 0:
                completion += 1 / nibble

        return offset, progress, round(completion * 100 / self.CAREER_EVENTS_FOR_100, 2)


    def updateCareerProg(self, startOffset, prog):
        if not prog in self.CAREER_PROGRESS:
            return

        offset = startOffset + self.CAREER_PROGRESS_OFFSET
        nibble = self.CAREER_PROGRESS[prog]

        for i in range(int(self.CAREER_EVENTS / 2)):
            self.bytes[offset + i] = (nibble << 4) | nibble


    def getLicenceProg(self, startOffset):
        licenses = []

        for lic in self.LICENSE_OFFSETS:
            offset = startOffset + self.LICENSE_OFFSETS[lic]
            license = [str(offset), lic]

            for i in range(self.TESTS_PER_LICENSE):
                byte = self.bytes[offset + self.LICENSE_SKIP * i]
                license.append(next((prog for prog, progByte in self.LICENSE_PROGRESS.items() if byte == progByte), self.INVALID_STR))

            licenses.append(license)

        return licenses


    def updateLicenceProg(self, startOffset, prog):
        if not prog in self.LICENSE_PROGRESS:
            return

        offset = startOffset + self.LICENSE_OFFSETS["S"]
        byte = self.LICENSE_PROGRESS[prog]

        for i in range(self.TESTS_PER_LICENSE * len(self.LICENSE_OFFSETS)):
            self.bytes[offset + self.LICENSE_SKIP * i] = byte


    def getCars(self, startOffset):
        def getCarName(data, code, region):
            for entry in data:
                if entry[0] == code and region == "EU":
                    return entry[1]

                elif entry[0] == code and region == "US":
                    return entry[2]

                elif entry[0] == code and region == "JP":
                    return entry[3]

            return self.INVALID_STR


        cars = []
        _, carCount = self.getVal(startOffset, self.CAR_COUNT_OFFSET, self.CAR_COUNT_SIZE, False)

        if carCount > self.MAX_CAR_COUNT:
            carCount = self.MAX_CAR_COUNT

        if carCount == 0:
            return cars

        data = None
        with open(self.CARS_DB_PATH, encoding = "UTF-8", newline = "") as f:
            data = list(csv.reader(f, delimiter = ","))

        block = next(block for block in self.blocks if block[0] == startOffset)
        region = block[3]
        codeAttr = self.CAR_PROPERTIES["Code"]

        for i in range(carCount):
            offset = startOffset + self.FIRST_CAR_OFFSET + self.CAR_SIZE * i
            bytes = self.bytes[offset:(offset + self.CAR_SIZE)]

            hexBytes = binascii.hexlify(bytes).decode("ASCII").upper()
            code = binascii.hexlify(bytes[codeAttr[0]:(codeAttr[0] + codeAttr[1])]).decode("ASCII").upper()

            cars.append((str(offset), str(i), getCarName(data, code, region), hexBytes))

        return cars


    def updateCar(self, startOffset, index, hex):
        if not index or not hex or len(hex) % 2 != 0:
            return

        index = int(index)
        _, carCount = self.getVal(startOffset, self.CAR_COUNT_OFFSET, self.CAR_COUNT_SIZE, False)

        if carCount > self.MAX_CAR_COUNT:
            carCount = self.MAX_CAR_COUNT

        if index < 0 or index > carCount - 1:
            if carCount == self.MAX_CAR_COUNT:
                return

            else:
                index = carCount
                self.updateVal(startOffset, self.CAR_COUNT_OFFSET, self.CAR_COUNT_SIZE, False, carCount + 1)

        offset = startOffset + self.FIRST_CAR_OFFSET + self.CAR_SIZE * index
        bytes = binascii.unhexlify(hex)
        size = min(len(bytes), self.CAR_SIZE)

        for i in range(size):
            self.bytes[offset + i] = bytes[i]


    def updateCurrCar(self, startOffset, index):
        if not index:
            return

        index = int(index)
        _, carCount = self.getVal(startOffset, self.CAR_COUNT_OFFSET, self.CAR_COUNT_SIZE, False)

        if carCount > self.MAX_CAR_COUNT:
            carCount = self.MAX_CAR_COUNT

        if index < 0 or index > carCount - 1:
            index = 255

        self.updateVal(startOffset, self.CURR_CAR_OFFSET, self.CURR_CAR_SIZE, False, index)


    def calcCrc32(self, startOffset):
        bytes = self.bytes[startOffset:(startOffset + self.CRC32_OFFSET)]
        return binascii.crc32(bytes)


    def updateCrc32(self, startOffset):
        crc32 = self.calcCrc32(startOffset)
        self.updateVal(startOffset, self.CRC32_OFFSET, self.CRC32_SIZE, False, crc32)


    def checkCrc32(self, startOffset):
        _, crc32 = self.getVal(startOffset, self.CRC32_OFFSET, self.CRC32_SIZE, False)
        calcCrc32 = self.calcCrc32(startOffset)
        return crc32 == calcCrc32


    def read(self, index):
        index = int(index) if index else -1

        for i in range(len(self.blocks)):
            if index >= 0 and i != index:
                continue

            block = self.blocks[i]
            startOffset = block[0]

            print("Start offset: ", startOffset, sep = "")
            print("Game Id at ", block[1], ": ", block[2], sep = "")
            print("Region: ", block[3], sep = "")

            offset, val = self.getVal(startOffset, self.CRC32_OFFSET, self.CRC32_SIZE, False)
            print("Checksum at ", offset, ": ", val, sep = "")

            val = self.checkCrc32(startOffset)
            print("Valid checksum: ", str(val).lower(), sep = "")

            offset, val = self.getLang(startOffset)
            print("Language at ", offset, ": ", val, sep = "")

            offset, val = self.getVal(startOffset, self.MONEY_OFFSET, self.MONEY_SIZE, True)
            print("Money at ", offset, ": ", val, sep = "")

            offset, val = self.getVal(startOffset, self.DAYS_OFFSET, self.DAYS_SIZE, True)
            print("Days at ", offset, ": ", val, sep = "")

            offset, val = self.getVal(startOffset, self.RACES_OFFSET, self.RACES_SIZE, True)
            print("Races at ", offset, ": ", val, sep = "")

            offset, val = self.getVal(startOffset, self.WINS_OFFSET, self.WINS_SIZE, True)
            print("Wins at ", offset, ": ", val, sep = "")

            offset, val = self.getVal(startOffset, self.SUM_OF_BEST_RANKINGS_OFFSET, self.SUM_OF_BEST_RANKINGS_SIZE, True)
            print("Sum of best race rankings at ", offset, ": ", val, sep = "")
            best_rankings = val

            offset, val = self.getVal(startOffset, self.SUM_OF_RANKINGS_OFFSET, self.SUM_OF_RANKINGS_SIZE, True)
            print("Sum of race rankings at ", offset, ": ", val, sep = "")
            rankings = val

            average = best_rankings / rankings if rankings != 0 else 0
            print("Average race ranking: ", average, sep = "")

            offset, val = self.getVal(startOffset, self.PRIZE_OFFSET, self.PRIZE_SIZE, True)
            print("Prize at ", offset, ": ", val, sep = "")

            val = self.getLicenceProg(startOffset)
            for entry in val:
                print("License ", entry[1], " at ", entry[0], ": ", ",".join(entry[2:]), sep = "")

            offset, val = self.getArcadeProg(startOffset)
            print("Arcade progress at ", offset, ":", sep = "")
            for entry in val:
                print("  ", entry[0], ": ", entry[1], sep = "")

            offset, val1, val2 = self.getCareerProg(startOffset)
            print("Career progress at ", offset, ": ", ",".join(val1), sep = "")
            print("Career percentage: ", val2, sep = "")

            offset, val = self.getVal(startOffset, self.ENDING_MOVIE_OFFSET, self.ENDING_MOVIE_SIZE, False)
            print("Ending movie unlocked at ", offset, ": ", str(val > 0).lower(), sep = "")

            offset, val = self.getVal(startOffset, self.CAR_COUNT_OFFSET, self.CAR_COUNT_SIZE, False)
            print("Car count at ", offset, ": ", val, sep = "")

            offset, val = self.getVal(startOffset, self.CURR_CAR_OFFSET, self.CURR_CAR_SIZE, False)
            if val >= self.MAX_CAR_COUNT:
                val = "none"

            print("Current car at ", offset, ": ", val, sep = "")

            val = self.getCars(startOffset)
            if len(val) > 0:
                print("Offset,", "Position,", "Name,", "Bytes", sep = "")

            for entry in val:
                print(",".join(entry))

            print()


    def update(self, index, vals):
        index = int(index) if index else -1

        for i in range(len(self.blocks)):
            if index >= 0 and i != index:
                continue

            block = self.blocks[i]
            startOffset = block[0]

            self.updateLang(startOffset, vals.lang)
            self.updateArcadeProg(startOffset, vals.arc)
            self.updateVal(startOffset, self.DAYS_OFFSET, self.DAYS_SIZE, True, vals.days)
            self.updateVal(startOffset, self.RACES_OFFSET, self.RACES_SIZE, True, vals.races)
            self.updateVal(startOffset, self.WINS_OFFSET, self.WINS_SIZE, True, vals.wins)
            self.updateVal(startOffset, self.SUM_OF_BEST_RANKINGS_OFFSET, self.SUM_OF_BEST_RANKINGS_OFFSET, True, vals.rank[0] if vals.rank else None)
            self.updateVal(startOffset, self.SUM_OF_RANKINGS_OFFSET, self.SUM_OF_RANKINGS_OFFSET, True, vals.rank[1] if vals.rank else None)
            self.updateVal(startOffset, self.PRIZE_OFFSET, self.PRIZE_SIZE, True, vals.prize)
            self.updateCareerProg(startOffset, vals.car)
            self.updateLicenceProg(startOffset, vals.lic)
            self.updateCar(startOffset, vals.edit[0] if vals.edit else None, vals.edit[1] if vals.edit else None)
            self.updateVal(startOffset, self.MONEY_OFFSET, self.MONEY_SIZE, True, vals.money)
            self.updateCurrCar(startOffset, vals.cur)
            self.updateCrc32(startOffset)

        with open(self.path, "wb") as f:
            f.write(self.bytes)
