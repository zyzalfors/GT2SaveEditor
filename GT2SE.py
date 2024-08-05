import argparse, binascii, csv, os, sys

N_BLOCKS = 15
HEADER_SIZE = 128
GME_HEADER_SIZE = 3904
FIRST_BLOCK_OFFSET = 8192
DAYS_OFFSET = 760
DAYS_SIZE = 2
TOT_RACES_OFFSET = 768
TOT_RACES_SIZE = 2
TOT_WINS_OFFSET = 772
TOT_WINS_SIZE = 2
FIRST_LICENSE_OFFSET = 5657
LICENSE_OFFSETS = {"S": 0, "IA": 1640, "IB": 3280, "IC": 4920, "A": 6560, "B": 8200}
LICENSE_DELTA = 164
N_TESTS = 60
CAR_COUNT_OFFSET = 15988
FIRST_CAR_OFFSET = 15992
CAR_SIZE = 164
CASH_OFFSET = 32392
CASH_SIZE = 4
CURRENT_CAR_OFFSET = 32396
CRC32_OFFSET = 32412
CRC32_SIZE = 4
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
 "TunerCode":  [129, 1],
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
CARS_DB_PATH = os.path.join(os.path.dirname(sys.argv[0]), "carsDB.csv")

def findFirstBlockInfos(rawBytes, isGme):
 blockInfos = []
 gmeShift = GME_HEADER_SIZE if isGme else 0
 for i in range(1, N_BLOCKS + 1):
  headerBytes = rawBytes[(HEADER_SIZE * i + gmeShift):(HEADER_SIZE * (i + 1) + gmeShift)]
  gameId = headerBytes[10:26].decode("ASCII")
  if headerBytes[0] == 0x51 and gameId in GAME_IDS: blockInfos.append((i, HEADER_SIZE * i + gmeShift + 10, gameId))
 return blockInfos

def readCash(rawBytes, firstBlockIndex, isGme):
 cashOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + CASH_OFFSET
 if isGme: cashOffset += GME_HEADER_SIZE
 cashBytes = rawBytes[cashOffset:(cashOffset + CASH_SIZE)]
 return cashOffset, int.from_bytes(cashBytes, byteorder = "little")

def updateCash(rawBytes, firstBlockIndex, cash, isGme):
 if not cash: return rawBytes
 cashOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + CASH_OFFSET
 if isGme: cashOffset += GME_HEADER_SIZE
 cashBytes = int(cash).to_bytes(CASH_SIZE, byteorder = "little")
 for i in range(CASH_SIZE): rawBytes[cashOffset + i] = cashBytes[i]
 return rawBytes

def readDays(rawBytes, firstBlockIndex, isGme):
 daysOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + DAYS_OFFSET
 if isGme: daysOffset += GME_HEADER_SIZE
 daysBytes = rawBytes[daysOffset:(daysOffset + DAYS_SIZE)]
 return daysOffset, int.from_bytes(daysBytes, byteorder = "little")

def updateDays(rawBytes, firstBlockIndex, days, isGme):
 if not days: return rawBytes
 daysOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + DAYS_OFFSET
 if isGme: daysOffset += GME_HEADER_SIZE
 daysBytes = int(days).to_bytes(DAYS_SIZE, byteorder = "little")
 for i in range(DAYS_SIZE): rawBytes[daysOffset + i] = daysBytes[i]
 return rawBytes

def readTotRaces(rawBytes, firstBlockIndex, isGme):
 totRacesOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + TOT_RACES_OFFSET
 if isGme: totRacesOffset += GME_HEADER_SIZE
 totRacesBytes = rawBytes[totRacesOffset:(totRacesOffset + TOT_RACES_SIZE)]
 return totRacesOffset, int.from_bytes(totRacesBytes, byteorder = "little")

def updateTotRaces(rawBytes, firstBlockIndex, totRaces, isGme):
 if not totRaces: return rawBytes
 totRacesOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + TOT_RACES_OFFSET
 if isGme: totRacesOffset += GME_HEADER_SIZE
 totRacesBytes = int(totRaces).to_bytes(TOT_RACES_SIZE, byteorder = "little")
 for i in range(TOT_RACES_SIZE): rawBytes[totRacesOffset + i] = totRacesBytes[i]
 return rawBytes

def readTotWins(rawBytes, firstBlockIndex, isGme):
 totWinsOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + TOT_WINS_OFFSET
 if isGme: totWinsOffset += GME_HEADER_SIZE
 totWinsBytes = rawBytes[totWinsOffset:(totWinsOffset + TOT_WINS_SIZE)]
 return totWinsOffset, int.from_bytes(totWinsBytes, byteorder = "little")

def updateTotWins(rawBytes, firstBlockIndex, totWins, isGme):
 if not totWins: return rawBytes
 totWinsOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + TOT_WINS_OFFSET
 if isGme: totWinsOffset += GME_HEADER_SIZE
 totWinsBytes = int(totWins).to_bytes(TOT_WINS_SIZE, byteorder = "little")
 for i in range(TOT_WINS_SIZE): rawBytes[totWinsOffset + i] = totWinsBytes[i]
 return rawBytes

def readLicenses(rawBytes, firstBlockIndex, isGme):
 firstLicenseOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + FIRST_LICENSE_OFFSET
 if isGme: firstLicenseOffset += GME_HEADER_SIZE
 licenseData = []
 for license in LICENSE_OFFSETS:
  licenseOffset = firstLicenseOffset + LICENSE_OFFSETS[license]
  data = ["License " + license + " at " + str(licenseOffset) + ":"]
  for i in range(int(N_TESTS / 6)):
   val = rawBytes[licenseOffset + i * LICENSE_DELTA]
   type = "undone"
   match val:
    case 4: type = "gold"
    case 3: type = "silver"
    case 2: type = "bronze"
    case 1: type = "kid"
   data.append(str(type))
  licenseData.append(" ".join(data))
 return firstLicenseOffset, licenseData

def updateLicenses(rawBytes, firstBlockIndex, type, isGme):
 if not type: return rawBytes
 firstLicenseOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + FIRST_LICENSE_OFFSET
 if isGme: firstLicenseOffset += GME_HEADER_SIZE
 val = 0
 match type:
  case "g": val = 4
  case "s": val = 3
  case "b": val = 2
  case "k": val = 1
 for i in range(N_TESTS): rawBytes[firstLicenseOffset + i * LICENSE_DELTA] = val
 return rawBytes

def readCurrentCar(rawBytes, firstBlockIndex, isGme):
 currentCarOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + CURRENT_CAR_OFFSET
 if isGme: currentCarOffset += GME_HEADER_SIZE
 return currentCarOffset, rawBytes[currentCarOffset]

def readCarCount(rawBytes, firstBlockIndex, isGme):
 carCountOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + CAR_COUNT_OFFSET
 if isGme: carCountOffset += GME_HEADER_SIZE
 return carCountOffset, rawBytes[carCountOffset]

def readCars(rawBytes, firstBlockIndex, carCount, isGme):
 firstCarOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + FIRST_CAR_OFFSET
 if isGme: firstCarOffset += GME_HEADER_SIZE
 carData = ["Index,Offset,CarName," + ",".join(list(CAR_PROPERTIES.keys()))] if carCount > 0 else []
 carNames = readCarNames() if carCount > 0 else []
 for i in range(carCount):
  carOffset = firstCarOffset + CAR_SIZE * i
  carBytes = rawBytes[carOffset:(carOffset + CAR_SIZE)]
  data = [str(i), str(carOffset)]
  for attribute in CAR_PROPERTY_ATTRIBUTES: data.append(binascii.hexlify(carBytes[attribute[0]:(attribute[0] + attribute[1])]).decode("ASCII").upper())
  carName = readCarName(carNames, data[66])
  data.insert(2, carName)
  carData.append(",".join(data))
 return firstCarOffset, carData

def readCarNames():
 carNames = None
 with open(CARS_DB_PATH, encoding = "UTF-8", newline = "") as file: carNames = list(csv.reader(file, delimiter = ","))
 return carNames

def readCarName(carNames, carCode):
 for row in carNames:
  if row[0] == carCode: return row[1]
 return ""

def updateCar(rawBytes, firstBlockIndex, carIndex, carPropertyNames, carPropertyValues, isGme):
 index = int(carIndex) if carIndex else 0
 if index < 0 or not carPropertyNames or not carPropertyValues: return rawBytes
 _, carCount = readCarCount(rawBytes, firstBlockIndex, isGme)
 if index > carCount - 1: return rawBytes
 firstCarOffset = FIRST_BLOCK_OFFSET * firstBlockIndex + FIRST_CAR_OFFSET
 if isGme: firstCarOffset += GME_HEADER_SIZE
 for i in range(len(carPropertyNames)):
  propertyAttributes = CAR_PROPERTY_ATTRIBUTES[CAR_PROPERTY_NAMES.index(carPropertyNames[i])]
  propertyOffset = propertyAttributes[0]
  propertyValue = bytearray(binascii.unhexlify(carPropertyValues[i]))
  size = min([propertyAttributes[1], len(propertyValue)])
  for j in range(size): rawBytes[firstCarOffset + CAR_SIZE * index + propertyOffset + j] = propertyValue[j]
 return rawBytes

def readCrc32(rawBytes, firstBlockIndex, isGme):
 crc32Offset = FIRST_BLOCK_OFFSET * firstBlockIndex + CRC32_OFFSET
 if isGme: crc32Offset += GME_HEADER_SIZE
 crc32Bytes = rawBytes[crc32Offset:(crc32Offset + CRC32_SIZE)]
 return crc32Offset, binascii.hexlify(crc32Bytes).decode("ASCII").upper()

def updateCrc32(rawBytes, firstBlockIndex, isGme):
 startOffset = FIRST_BLOCK_OFFSET * firstBlockIndex
 crc32Offset = startOffset + CRC32_OFFSET
 if isGme:
  startOffset += GME_HEADER_SIZE
  crc32Offset += GME_HEADER_SIZE
 saveBytes = rawBytes[startOffset:crc32Offset]
 crc32Bytes = binascii.crc32(saveBytes).to_bytes(CRC32_SIZE, byteorder = "little")
 for i in range(CRC32_SIZE): rawBytes[crc32Offset + i] = crc32Bytes[i]
 return rawBytes

def readSave(args):
 rawBytes = readRawBytes(args.f)
 blockInfos = findFirstBlockInfos(rawBytes, args.g)
 for blockInfo in blockInfos:
  firstBlockIndex, gameIdOffset, gameId = blockInfo[0], blockInfo[1], blockInfo[2]
  crc32Offset, crc32 = readCrc32(rawBytes, firstBlockIndex, args.g)
  cashOffset, cash = readCash(rawBytes, firstBlockIndex, args.g)
  daysOffset, days = readDays(rawBytes, firstBlockIndex, args.g)
  totRacesOffset, totRaces = readTotRaces(rawBytes, firstBlockIndex, args.g)
  totWinsOffset, totWins = readTotWins(rawBytes, firstBlockIndex, args.g)
  firstLicenseOffset, licenses = readLicenses(rawBytes, firstBlockIndex, args.g)
  carCountOffset, carCount = readCarCount(rawBytes, firstBlockIndex, args.g)
  currentCarOffset, currentCar = readCurrentCar(rawBytes, firstBlockIndex, args.g)
  firstCarOffset, cars = readCars(rawBytes, firstBlockIndex, carCount, args.g)
  print("Game Id at ", gameIdOffset, ": ", gameId, sep = "")
  print("CRC32 at ", crc32Offset, ": ", crc32, sep = "")
  print("Cash at ", cashOffset, ": ", cash, sep = "")
  print("Days at ", daysOffset, ": ", days, sep = "")
  print("Total races at ", totRacesOffset, ": ", totRaces, sep = "")
  print("Total wins at ", totWinsOffset, ": ", totWins, sep = "")
  for license in licenses: print(license)
  print("Car count at ", carCountOffset, ": ", carCount, sep = "")
  if currentCar < 100: print("Current car at ", currentCarOffset, ": ", currentCar, sep = "")
  else: print("Current car at ", currentCarOffset, ": none", sep = "")
  if carCount > 0: print("Cars at ", firstCarOffset, ":", sep = "")
  for car in cars: print(car)

def updateSave(args):
 rawBytes = readRawBytes(args.f)
 blockInfos = findFirstBlockInfos(rawBytes, args.g)
 for blockInfo in blockInfos:
  firstBlockIndex = blockInfo[0]
  rawBytes = updateCash(rawBytes, firstBlockIndex, args.c, args.g)
  rawBytes = updateDays(rawBytes, firstBlockIndex, args.d, args.g)
  rawBytes = updateTotRaces(rawBytes, firstBlockIndex, args.r, args.g)
  rawBytes = updateTotWins(rawBytes, firstBlockIndex, args.w, args.g)
  rawBytes = updateLicenses(rawBytes, firstBlockIndex, args.l, args.g)
  rawBytes = updateCar(rawBytes, firstBlockIndex, args.i, args.p, args.v, args.g)
  rawBytes = updateCrc32(rawBytes, firstBlockIndex, args.g)
 writeRawBytes(args.f, rawBytes)

def readRawBytes(path):
 rawBytes = None
 with open(path, "rb") as file: rawBytes = bytearray(file.read())
 return rawBytes

def writeRawBytes(path, rawBytes):
 newPath = os.path.join(os.path.dirname(path), "edited_" + os.path.basename(path))
 with open(newPath, "wb") as file: file.write(rawBytes)

def readArgs():
 parser = argparse.ArgumentParser()
 parser.add_argument("-f", action = "store", help = "enter path of save to read/edit")
 parser.add_argument("-g", action = "store_true", help = "enter this to read/edit GME save files")
 parser.add_argument("-c", action = "store", help = "enter cash value to set in save")
 parser.add_argument("-d", action = "store", help = "enter days value to set in save")
 parser.add_argument("-r", action = "store", help = "enter total races value to set in save")
 parser.add_argument("-w", action = "store", help = "enter total wins value to set in save")
 parser.add_argument("-l", action = "store", help = "enter type (gold, silver, bronze, kid, undone) of license trophies to set in save", choices = ["g", "s", "b", "k", "u"])
 parser.add_argument("-i", action = "store", help = "enter positonal index (from 0 to 99) of car to edit")
 parser.add_argument("-v", action = "append", help = "enter values (as hex string) of car property to edit")
 parser.add_argument("-p", action = "append", help = "enter name of car property to edit", choices = CAR_PROPERTY_NAMES)
 return parser.parse_args()

def main(args):
 if not args.f: return
 argv = list(args.__dict__.items())
 argv.pop(0)
 argv.pop(0)
 read = not any(arg[1] is not None for arg in argv)
 if read: readSave(args)
 else: updateSave(args)

main(readArgs())