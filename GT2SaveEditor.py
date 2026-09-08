import binascii, csv, os

class GT2SaveEditor:
    RAW_MAGIC = b"\xAC\x14"
    SC_MAGIC = b"\x53\x43"
    MC_MAGIC = b"\x4D\x43"
    PSV_MAGIC = b"\x00\x56\x53\x50"
    GME_MAGIC = b"\x31\x32\x33\x2D\x34\x35\x36\x2D\x53\x54\x44"

    SC_HEADER_SIZE = 512
    MC_HEADER_SIZE = 128
    PSV_HEADER_SIZE = 132
    GME_HEADER_SIZE = 3904

    MC_BLOCK_COUNT = 16
    MC_BLOCK_SIZE = 8192
    MC_SIZE = 131072

    RAW_SAVE_SIZE = 31904

    SERIALS = {"SCES-02380GAME": "EU", "SCES-12380GAME": "EU", "SCUS-94455GAME": "US", "SCUS-94488GAME": "US", "SCPS-10116GAME": "JP", "SCPS-10117GAME": "JP"}

    LANG_OFFSET = 0
    LANGUAGES = {"ja": 0, "en-us": 1, "en-gb": 2, "fr": 3, "de": 4, "it": 5, "es": 6}

    ARCADE_PROGRESS_OFFSET = 184
    ARCADE_PROGRESS = {"none": 0, "easy": 1, "normal": 2, "hard": 4}
    ARCADE_TRACKS = ["Rome", "Rome Short", "Rome Night", "Seattle", "Seattle Short", "Super Speedway", "Laguna Seca",
                     "Midfield", "Apricot Hill", "Red Rock Valley", "Tahiti Road", "High Speed Ring", "Autumn Ring", "Trial Mountain",
                     "Deep Forest", "Grand Valley", "Grand Valley East", "Special Stage Route 5", "Clubman Stage Route 5", "Grindelwald", "Test Course"]

    DAYS_OFFSET = 248
    DAYS_SIZE = 4

    RACES_OFFSET = 256
    RACES_SIZE = 4

    WINS_OFFSET = 260
    WINS_SIZE = 4

    SUM_OF_BEST_RANKINGS_OFFSET = 264
    SUM_OF_BEST_RANKINGS_SIZE = 4

    SUM_OF_RANKINGS_OFFSET = 268
    SUM_OF_RANKINGS_SIZE = 4

    PRIZE_OFFSET = 276
    PRIZE_SIZE = 4

    CAREER_PROGRESS_OFFSET = 280
    CAREER_PROGRESS = {"none": 0, "1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6}
    CAREER_EVENTS = 248
    CAREER_EVENTS_FOR_100 = 219

    ENDING_MOVIE_OFFSET = 533
    ENDING_MOVIE_SIZE = 1

    LICENSE_OFFSETS = {"S": 5145, "IA": 6785, "IB": 8425, "IC": 10065, "A": 11705, "B": 13345}
    LICENSE_PROGRESS = {"none": 0, "kid": 1, "bronze": 2, "silver": 3, "gold": 4}
    TESTS_PER_LICENSE = 10
    LICENSE_SKIP = 164

    CAR_COUNT_OFFSET = 15476
    CAR_COUNT_SIZE = 1
    MAX_CAR_COUNT = 100

    FIRST_CAR_OFFSET = 15480
    CAR_SIZE = 164
    CAR_PROPERTIES = {"Code": (0, 4)}
    CARS_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carsDB.csv")

    MONEY_OFFSET = 31880
    MONEY_SIZE = 4

    CURR_CAR_OFFSET = 31884
    CURR_CAR_SIZE = 1

    CRC32_OFFSET = 31900
    CRC32_SIZE = 4

    INVALID_STR = "invalid"


    def __init__(self, path):
        self.path = path

        with open(self.path, "rb") as f:
            self.data = bytearray(f.read())

        self.parse()


    def parse(self):
        self.format = "Unknown"
        self.saves = []

        if len(self.data) >= self.SC_HEADER_SIZE + self.RAW_SAVE_SIZE:
            if self.data.startswith(self.SC_MAGIC):
                self.format = "SC"
                self.saves.append((self.SC_HEADER_SIZE, None, None, None))
                return

        if len(self.data) >= self.PSV_HEADER_SIZE + self.SC_HEADER_SIZE + self.RAW_SAVE_SIZE:
            if self.data.startswith(self.PSV_MAGIC):
                serial = self.data[102:116].decode("ASCII")

                if serial in self.SERIALS:
                    self.format = "PSV"
                    self.saves.append((self.PSV_HEADER_SIZE + self.SC_HEADER_SIZE, 102, serial, self.SERIALS[serial]))
                    return

        gmeShift = None
        if len(self.data) >= self.MC_SIZE and self.data.startswith(self.MC_MAGIC):
            self.format = "MC"
            gmeShift = 0

        if len(self.data) >= self.GME_HEADER_SIZE + self.MC_SIZE and self.data.startswith(self.GME_MAGIC):
            self.format = "GME"
            gmeShift = self.GME_HEADER_SIZE

        if gmeShift is not None:
            for i in range(1, self.MC_BLOCK_COUNT):
                headerOffset = gmeShift + self.MC_HEADER_SIZE * i
                headerBytes = self.data[headerOffset:headerOffset + self.MC_HEADER_SIZE]
                serial = headerBytes[12:26].decode("ASCII")

                if headerBytes[0] == 0x51 and serial in self.SERIALS:
                    self.saves.append((gmeShift + self.MC_BLOCK_SIZE * i + self.SC_HEADER_SIZE, headerOffset + 12, serial, self.SERIALS[serial]))


    def getLang(self, startOffset):
        offset = startOffset + self.LANG_OFFSET
        byte = self.data[offset]
        return offset, next((lang for lang, langByte in self.LANGUAGES.items() if byte == langByte), self.INVALID_STR)


    def updateLang(self, startOffset, lang):
        if not lang in self.LANGUAGES:
            return

        self.data[startOffset + self.LANG_OFFSET] = self.LANGUAGES[lang]


    def getArcadeProg(self, startOffset):
        offset = startOffset + self.ARCADE_PROGRESS_OFFSET
        progress = []

        for i in range(len(self.ARCADE_TRACKS)):
            byte = self.data[offset + i]
            prog = next((prog for prog, progByte in self.ARCADE_PROGRESS.items() if byte == progByte), self.INVALID_STR)
            progress.append((self.ARCADE_TRACKS[i], prog))

        return offset, progress


    def updateArcadeProg(self, startOffset, prog):
        if not prog in self.ARCADE_PROGRESS:
            return

        offset = startOffset + self.ARCADE_PROGRESS_OFFSET
        byte = self.ARCADE_PROGRESS[prog]

        for i in range(len(self.ARCADE_TRACKS)):
            self.data[offset + i] = byte


    def getVal(self, startOffset, valOffset, valSize, signed):
        offset = startOffset + valOffset
        data = self.data[offset:offset + valSize]
        return offset, int.from_bytes(data, byteorder = "little", signed = signed)


    def updateVal(self, startOffset, valOffset, valSize, signed, val):
        if val is None:
            return

        offset = startOffset + valOffset
        data = int(val).to_bytes(valSize, byteorder = "little", signed = signed)

        for i in range(valSize):
            self.data[offset + i] = data[i]


    def getCareerProg(self, startOffset):
        offset = startOffset + self.CAREER_PROGRESS_OFFSET
        progress = []
        completion = 0

        for i in range(int(self.CAREER_EVENTS / 2)):
            byte = self.data[offset + i]

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
            self.data[offset + i] = (nibble << 4) | nibble


    def getLicenseProg(self, startOffset):
        licenses = []

        for lic in self.LICENSE_OFFSETS:
            offset = startOffset + self.LICENSE_OFFSETS[lic]
            licData = [str(offset), lic]

            for i in range(self.TESTS_PER_LICENSE):
                byte = self.data[offset + self.LICENSE_SKIP * i]
                licData.append(next((prog for prog, progByte in self.LICENSE_PROGRESS.items() if byte == progByte), self.INVALID_STR))

            licenses.append(licData)

        return licenses


    def updateLicenseProg(self, startOffset, prog):
        if not prog in self.LICENSE_PROGRESS:
            return

        offset = startOffset + self.LICENSE_OFFSETS["S"]
        byte = self.LICENSE_PROGRESS[prog]

        for i in range(self.TESTS_PER_LICENSE * len(self.LICENSE_OFFSETS)):
            self.data[offset + self.LICENSE_SKIP * i] = byte


    def getCars(self, startOffset):
        def getCarName(csvData, code, region):
            for entry in csvData:
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

        csvData = None
        with open(self.CARS_DB_PATH, encoding = "UTF-8", newline = "") as f:
            csvData = list(csv.reader(f, delimiter = ","))

        save = next(save for save in self.saves if save[0] == startOffset)
        region = save[3] if save[3] else "EU"
        codeAttr = self.CAR_PROPERTIES["Code"]

        for i in range(carCount):
            offset = startOffset + self.FIRST_CAR_OFFSET + self.CAR_SIZE * i
            data = self.data[offset:offset + self.CAR_SIZE]

            hexBytes = binascii.hexlify(data).decode("ASCII").upper()
            code = binascii.hexlify(data[codeAttr[0]:codeAttr[0] + codeAttr[1]]).decode("ASCII").upper()

            cars.append((str(offset), str(i), getCarName(csvData, code, region), hexBytes))

        return cars


    def updateCar(self, startOffset, index, hexBytes):
        if index is None or not hexBytes or len(hexBytes) % 2 != 0:
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
        data = binascii.unhexlify(hexBytes)
        size = min(len(data), self.CAR_SIZE)

        for i in range(size):
            self.data[offset + i] = data[i]


    def updateCurrCar(self, startOffset, index):
        if index is None:
            return

        index = int(index)
        _, carCount = self.getVal(startOffset, self.CAR_COUNT_OFFSET, self.CAR_COUNT_SIZE, False)

        if carCount > self.MAX_CAR_COUNT:
            carCount = self.MAX_CAR_COUNT

        if index < 0 or index > carCount - 1:
            index = 255

        self.updateVal(startOffset, self.CURR_CAR_OFFSET, self.CURR_CAR_SIZE, False, index)


    def calcCrc32(self, startOffset):
        data = self.data[startOffset - self.SC_HEADER_SIZE:startOffset + self.CRC32_OFFSET]
        return binascii.crc32(data)


    def updateCrc32(self, startOffset):
        crc32 = self.calcCrc32(startOffset)
        self.updateVal(startOffset, self.CRC32_OFFSET, self.CRC32_SIZE, False, crc32)


    def checkCrc32(self, startOffset):
        _, crc32 = self.getVal(startOffset, self.CRC32_OFFSET, self.CRC32_SIZE, False)
        calcCrc32 = self.calcCrc32(startOffset)
        return crc32 == calcCrc32


    def read(self, index):
        index = int(index) if index is not None else -1

        for i in range(len(self.saves)):
            if index >= 0 and i != index:
                continue

            save = self.saves[i]
            startOffset = save[0]

            print(f"Format: {self.format}")
            print(f"Start offset: {startOffset}")

            if save[1] and save[2] and save[3]:
                print(f"Game serial at {save[1]}: {save[2]}")
                print(f"Region: {save[3]}")

            offset, val = self.getVal(startOffset, self.CRC32_OFFSET, self.CRC32_SIZE, False)
            print(f"Checksum at {offset}: {val}")

            val = self.checkCrc32(startOffset)
            print(f"Valid checksum: {str(val).lower()}")

            offset, val = self.getLang(startOffset)
            print(f"Language at {offset}: {val}")

            offset, val = self.getVal(startOffset, self.MONEY_OFFSET, self.MONEY_SIZE, True)
            print(f"Money at {offset}: {val}")

            offset, val = self.getVal(startOffset, self.DAYS_OFFSET, self.DAYS_SIZE, True)
            print(f"Days at {offset}: {val}")

            offset, val = self.getVal(startOffset, self.RACES_OFFSET, self.RACES_SIZE, True)
            print(f"Races at {offset}: {val}")

            offset, val = self.getVal(startOffset, self.WINS_OFFSET, self.WINS_SIZE, True)
            print(f"Wins at {offset}: {val}")

            offset, val = self.getVal(startOffset, self.SUM_OF_BEST_RANKINGS_OFFSET, self.SUM_OF_BEST_RANKINGS_SIZE, True)
            print(f"Sum of best race rankings at {offset}: {val}")
            bestRankings = val

            offset, val = self.getVal(startOffset, self.SUM_OF_RANKINGS_OFFSET, self.SUM_OF_RANKINGS_SIZE, True)
            print(f"Sum of race rankings at {offset}: {val}")
            rankings = val

            average = bestRankings / rankings if rankings != 0 else 0
            print(f"Average race ranking: {average}")

            offset, val = self.getVal(startOffset, self.PRIZE_OFFSET, self.PRIZE_SIZE, True)
            print(f"Prize at {offset}: {val}")

            val = self.getLicenseProg(startOffset)
            for entry in val:
                print(f"License {entry[1]} at {entry[0]}: {','.join(entry[2:])}")

            offset, val = self.getArcadeProg(startOffset)
            print(f"Arcade progress at {offset}:")
            for entry in val:
                print(f"{entry[0]}: {entry[1]}")

            offset, val1, val2 = self.getCareerProg(startOffset)
            print(f"Career progress at {offset}: {','.join(val1)}")
            print(f"Career percentage: {val2}")

            offset, val = self.getVal(startOffset, self.ENDING_MOVIE_OFFSET, self.ENDING_MOVIE_SIZE, False)
            print(f"Ending movie unlocked at {offset}: {str(val > 0).lower()}")

            offset, val = self.getVal(startOffset, self.CAR_COUNT_OFFSET, self.CAR_COUNT_SIZE, False)
            print(f"Car count at {offset}: {val}")

            offset, val = self.getVal(startOffset, self.CURR_CAR_OFFSET, self.CURR_CAR_SIZE, False)
            if val >= self.MAX_CAR_COUNT:
                val = "none"

            print(f"Current car at {offset}: {val}")

            val = self.getCars(startOffset)
            if len(val) > 0:
                print("Offset,Position,Name,Bytes")

            for entry in val:
                print(f"{','.join(entry)}")

            print()


    def update(self, index, vals):
        index = int(index) if index is not None else -1

        for i in range(len(self.saves)):
            if index >= 0 and i != index:
                continue

            save = self.saves[i]
            startOffset = save[0]

            self.updateLang(startOffset, vals.lang)
            self.updateArcadeProg(startOffset, vals.arc)
            self.updateVal(startOffset, self.DAYS_OFFSET, self.DAYS_SIZE, True, vals.days)
            self.updateVal(startOffset, self.RACES_OFFSET, self.RACES_SIZE, True, vals.races)
            self.updateVal(startOffset, self.WINS_OFFSET, self.WINS_SIZE, True, vals.wins)
            self.updateVal(startOffset, self.SUM_OF_BEST_RANKINGS_OFFSET, self.SUM_OF_BEST_RANKINGS_SIZE, True, vals.rank[0] if vals.rank else None)
            self.updateVal(startOffset, self.SUM_OF_RANKINGS_OFFSET, self.SUM_OF_RANKINGS_SIZE, True, vals.rank[1] if vals.rank else None)
            self.updateVal(startOffset, self.PRIZE_OFFSET, self.PRIZE_SIZE, True, vals.prize)
            self.updateCareerProg(startOffset, vals.car)
            self.updateLicenseProg(startOffset, vals.lic)
            self.updateCar(startOffset, vals.edit[0] if vals.edit else None, vals.edit[1] if vals.edit else None)
            self.updateVal(startOffset, self.MONEY_OFFSET, self.MONEY_SIZE, True, vals.money)
            self.updateCurrCar(startOffset, vals.cur)
            self.updateCrc32(startOffset)

        with open(self.path, "wb") as f:
            f.write(self.data)