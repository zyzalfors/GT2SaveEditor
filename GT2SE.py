import argparse, binascii, csv, os

class GT2SaveFile:
 N_BLOCKS = 15
 HEADER_SIZE = 128
 GME_HEADER_SIZE = 3904
 DAYS_SIZE = 2
 TOT_RACES_SIZE = 2
 TOT_WINS_SIZE = 2
 CAR_SIZE = 164
 CASH_SIZE = 4
 CRC32_SIZE = 4
 N_LICENSES = 6
 N_TESTS_PER_LICENSE = 10
 LICENSE_SKIP = 164
 MAX_CAR_COUNT = 100 
 FIRST_BLOCK_OFFSET = 8192
 DAYS_OFFSET = 760 
 TOT_RACES_OFFSET = 768
 TOT_WINS_OFFSET = 772
 FIRST_LICENSE_OFFSET = 5657
 LICENSE_OFFSETS = {"S": 0, "IA": 1640, "IB": 3280, "IC": 4920, "A": 6560, "B": 8200}
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
 CARS_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carsDB.csv")

 def __init__(self, path):
  self.path = path
  self.isGme = path.lower().endswith(".gme")
  with open(path, "rb") as file: self.rawBytes = bytearray(file.read()) 
  self.readFirstBlockInfos()

 def readFirstBlockInfos(self):
  self.firstBlockInfos = []
  gmeShift = self.GME_HEADER_SIZE if self.isGme else 0
  for i in range(1, self.N_BLOCKS + 1):
   headerOffset = self.HEADER_SIZE * i + gmeShift
   headerBytes = self.rawBytes[headerOffset:(headerOffset + self.HEADER_SIZE)]
   gameId = headerBytes[10:26].decode("ASCII")
   region = ""
   if gameId.startswith("BE"): region = "EU"
   elif gameId.startswith("BA"): region = "US"
   elif gameId.startswith("BI"): region = "JP"
   if headerBytes[0] == 0x51 and gameId in self.GAME_IDS: self.firstBlockInfos.append((i, headerOffset + 10, gameId, region))

 def getCash(self, firstBlockIndex):
  cashOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.CASH_OFFSET
  if self.isGme: cashOffset += self.GME_HEADER_SIZE
  cashBytes = self.rawBytes[cashOffset:(cashOffset + self.CASH_SIZE)]
  return cashOffset, int.from_bytes(cashBytes, byteorder = "little")

 def getDays(self, firstBlockIndex):
  daysOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.DAYS_OFFSET
  if self.isGme: daysOffset += self.GME_HEADER_SIZE
  daysBytes = self.rawBytes[daysOffset:(daysOffset + self.DAYS_SIZE)]
  return daysOffset, int.from_bytes(daysBytes, byteorder = "little")

 def getTotRaces(self, firstBlockIndex):
  totRacesOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.TOT_RACES_OFFSET
  if self.isGme: totRacesOffset += self.GME_HEADER_SIZE
  totRacesBytes = self.rawBytes[totRacesOffset:(totRacesOffset + self.TOT_RACES_SIZE)]
  return totRacesOffset, int.from_bytes(totRacesBytes, byteorder = "little")

 def getTotWins(self, firstBlockIndex):
  totWinsOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.TOT_WINS_OFFSET
  if self.isGme: totWinsOffset += self.GME_HEADER_SIZE
  totWinsBytes = self.rawBytes[totWinsOffset:(totWinsOffset + self.TOT_WINS_SIZE)]
  return totWinsOffset, int.from_bytes(totWinsBytes, byteorder = "little")

 def getLicenses(self, firstBlockIndex):
  firstLicenseOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.FIRST_LICENSE_OFFSET
  if self.isGme: firstLicenseOffset += self.GME_HEADER_SIZE
  licenses = []
  for license in self.LICENSE_OFFSETS:
   licenseOffset = firstLicenseOffset + self.LICENSE_OFFSETS[license]
   data = [str(licenseOffset), license]
   for i in range(self.N_TESTS_PER_LICENSE):
    val = self.rawBytes[licenseOffset + self.LICENSE_SKIP * i]
    licenseType = "undone"
    match val:
     case 4: licenseType = "gold"
     case 3: licenseType = "silver"
     case 2: licenseType = "bronze"
     case 1: licenseType = "kid"
    data.append(licenseType)
   licenses.append(data)
  return licenses

 def getCurrCar(self, firstBlockIndex):
  currCarOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.CURR_CAR_OFFSET
  if self.isGme: currCarOffset += self.GME_HEADER_SIZE
  return currCarOffset, self.rawBytes[currCarOffset]

 def getCarCount(self, firstBlockIndex):
  carCountOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.CAR_COUNT_OFFSET
  if self.isGme: carCountOffset += self.GME_HEADER_SIZE
  return carCountOffset, self.rawBytes[carCountOffset]

 def getCars(self, firstBlockIndex):
  firstCarOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.FIRST_CAR_OFFSET
  if self.isGme: firstCarOffset += self.GME_HEADER_SIZE
  _, carCount = self.getCarCount(firstBlockIndex)
  cars, carNames = [], []
  if carCount > 0:
   with open(self.CARS_DB_PATH, encoding = "UTF-8", newline = "") as file: carNames = list(csv.reader(file, delimiter = ","))
  for i in range(carCount):
   carOffset = firstCarOffset + self.CAR_SIZE * i
   carBytes = self.rawBytes[carOffset:(carOffset + self.CAR_SIZE)]
   data = [str(carOffset), str(i)]
   for attribute in self.CAR_PROPERTY_ATTRIBUTES: data.append(binascii.hexlify(carBytes[attribute[0]:(attribute[0] + attribute[1])]).decode("ASCII").upper())
   carName = self.getCarName(carNames, data[66])
   data.insert(2, carName)
   cars.append(data)
  return cars

 def getCarName(self, carNames, carCode):
  for row in carNames:
   if row[0] == carCode: return row[1]
  return ""

 def getCrc32(self, firstBlockIndex):
  crc32Offset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.CRC32_OFFSET
  if self.isGme: crc32Offset += self.GME_HEADER_SIZE
  crc32Bytes = self.rawBytes[crc32Offset:(crc32Offset + self.CRC32_SIZE)]
  return crc32Offset, binascii.hexlify(crc32Bytes).decode("ASCII").upper()

 def updateCash(self, firstBlockIndex, cash):
  if not cash: return
  cashOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.CASH_OFFSET
  if self.isGme: cashOffset += self.GME_HEADER_SIZE
  cashBytes = int(cash).to_bytes(self.CASH_SIZE, byteorder = "little")
  for i in range(self.CASH_SIZE): self.rawBytes[cashOffset + i] = cashBytes[i]

 def updateDays(self, firstBlockIndex, days):
  if not days: return
  daysOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.DAYS_OFFSET
  if self.isGme: daysOffset += self.GME_HEADER_SIZE
  daysBytes = int(days).to_bytes(self.DAYS_SIZE, byteorder = "little")
  for i in range(self.DAYS_SIZE): self.rawBytes[daysOffset + i] = daysBytes[i]

 def updateTotRaces(self, firstBlockIndex, totRaces):
  if not totRaces: return
  totRacesOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.TOT_RACES_OFFSET
  if self.isGme: totRacesOffset += self.GME_HEADER_SIZE
  totRacesBytes = int(totRaces).to_bytes(self.TOT_RACES_SIZE, byteorder = "little")
  for i in range(self.TOT_RACES_SIZE): self.rawBytes[totRacesOffset + i] = totRacesBytes[i]

 def updateTotWins(self, firstBlockIndex, totWins):
  if not totWins: return
  totWinsOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.TOT_WINS_OFFSET
  if self.isGme: totWinsOffset += self.GME_HEADER_SIZE
  totWinsBytes = int(totWins).to_bytes(self.TOT_WINS_SIZE, byteorder = "little")
  for i in range(self.TOT_WINS_SIZE): self.rawBytes[totWinsOffset + i] = totWinsBytes[i]

 def updateLicenses(self, firstBlockIndex, licenseType):
  firstLicenseOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.FIRST_LICENSE_OFFSET
  if self.isGme: firstLicenseOffset += self.GME_HEADER_SIZE
  val = 0
  match licenseType:
   case "g": val = 4
   case "s": val = 3
   case "b": val = 2
   case "k": val = 1
  for i in range(self.N_TESTS_PER_LICENSE * self.N_LICENSES): self.rawBytes[firstLicenseOffset + self.LICENSE_SKIP * i] = val

 def updateCurrCar(self, firstBlockIndex, currCar):
  val = int(currCar) if currCar else 255
  if val < 0: return
  _, carCount = self.getCarCount(firstBlockIndex)
  if val > carCount - 1 and val != 255: return
  currCarOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.CURR_CAR_OFFSET
  if self.isGme: currCarOffset += self.GME_HEADER_SIZE
  self.rawBytes[currCarOffset] = val

 def updateCar(self, firstBlockIndex, carIndex, carPropertyNames, carPropertyValues):
  index = int(carIndex) if carIndex else 0
  if index < 0 or not carPropertyNames or not carPropertyValues: return
  _, carCount = self.getCarCount(firstBlockIndex)
  if index > carCount - 1: return
  firstCarOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex + self.FIRST_CAR_OFFSET
  if self.isGme: firstCarOffset += self.GME_HEADER_SIZE
  for i in range(len(carPropertyNames)):
   propertyAttributes = self.CAR_PROPERTY_ATTRIBUTES[self.CAR_PROPERTY_NAMES.index(carPropertyNames[i])]
   propertyOffset = propertyAttributes[0]
   propertyValue = bytearray(binascii.unhexlify(carPropertyValues[i]))
   size = min([propertyAttributes[1], len(propertyValue)])
   for j in range(size): self.rawBytes[firstCarOffset + self.CAR_SIZE * index + propertyOffset + j] = propertyValue[j]

 def updateCrc32(self, firstBlockIndex):
  startOffset = self.FIRST_BLOCK_OFFSET * firstBlockIndex
  crc32Offset = startOffset + self.CRC32_OFFSET
  if self.isGme:
   startOffset += self.GME_HEADER_SIZE
   crc32Offset += self.GME_HEADER_SIZE
  saveBytes = self.rawBytes[startOffset:crc32Offset]
  crc32Bytes = binascii.crc32(saveBytes).to_bytes(self.CRC32_SIZE, byteorder = "little")
  for i in range(self.CRC32_SIZE): self.rawBytes[crc32Offset + i] = crc32Bytes[i]

 def update(self, saveIndex, vals):
  for i in range(len(self.firstBlockInfos)):
   if saveIndex and i != int(saveIndex): continue
   firstBlockInfo = self.firstBlockInfos[i]
   firstBlockIndex = firstBlockInfo[0]
   self.updateDays(firstBlockIndex, vals.days)
   self.updateTotRaces(firstBlockIndex, vals.races)
   self.updateTotWins(firstBlockIndex, vals.wins)
   self.updateLicenses(firstBlockIndex, vals.license)
   self.updateCar(firstBlockIndex, vals.index, vals.property, vals.value)
   self.updateCash(firstBlockIndex, vals.cash)
   self.updateCurrCar(firstBlockIndex, vals.curr)
   self.updateCrc32(firstBlockIndex)

 def print(self, saveIndex):
  for i in range(len(self.firstBlockInfos)):
   if saveIndex and i != int(saveIndex): continue   
   firstBlockInfo = self.firstBlockInfos[i]
   firstBlockIndex, gameIdOffset, gameId, region = firstBlockInfo[0], firstBlockInfo[1], firstBlockInfo[2], firstBlockInfo[3]
   crc32Offset, crc32 = self.getCrc32(firstBlockIndex)
   cashOffset, cash = self.getCash(firstBlockIndex)
   daysOffset, days = self.getDays(firstBlockIndex)
   totRacesOffset, totRaces = self.getTotRaces(firstBlockIndex)
   totWinsOffset, totWins = self.getTotWins(firstBlockIndex)
   licenses = self.getLicenses(firstBlockIndex)
   carCountOffset, carCount = self.getCarCount(firstBlockIndex)
   currCarOffset, currCar = self.getCurrCar(firstBlockIndex)
   cars = self.getCars(firstBlockIndex)
   print("Game Id at ", gameIdOffset, ": ", gameId, sep = "")
   print("Region: ", region, sep = "")
   print("CRC32 at ", crc32Offset, ": ", crc32, sep = "")
   print("Cash at ", cashOffset, ": ", cash, sep = "")
   print("Days at ", daysOffset, ": ", days, sep = "")
   print("Total races at ", totRacesOffset, ": ", totRaces, sep = "")
   print("Total wins at ", totWinsOffset, ": ", totWins, sep = "")
   for license in licenses: print("License ", license[1], " at ", license[0], ": ", ",".join(license[2:]), sep = "")
   print("Car count at ", carCountOffset, ": ", carCount, sep = "")
   if currCar < self.MAX_CAR_COUNT: print("Current car at ", currCarOffset, ": ", currCar, sep = "")
   else: print("Current car at ", currCarOffset, ": none", sep = "")
   if len(cars) > 0: print("Offset,", "Index,", "CarName,", ",".join(list(self.CAR_PROPERTIES.keys())), sep = "")
   for car in cars: print(",".join(car))

 def save(self, newPath):
  with open(newPath, "wb") as file: file.write(self.rawBytes)

def readArgs():
 parser = argparse.ArgumentParser()
 parser.add_argument("-file", action = "store", help = "enter path of save to read/edit")
 parser.add_argument("-save", action = "store", help = "enter index (starting from 0) of save to read/edit, don't set to read all saves")
 parser.add_argument("-cash", action = "store", help = "enter cash value to set in save")
 parser.add_argument("-days", action = "store", help = "enter days value to set in save")
 parser.add_argument("-races", action = "store", help = "enter total races value to set in save")
 parser.add_argument("-wins", action = "store", help = "enter total wins value to set in save")
 parser.add_argument("-license", action = "store", help = "enter type (gold, silver, bronze, kid, undone) of license trophies to set in save", choices = ["g", "s", "b", "k", "u"])
 parser.add_argument("-curr", action = "store", help = "enter index (starting from 0) of current car to set in save")
 parser.add_argument("-index", action = "store", help = "enter positonal index (0 to 99) of car to edit in save")
 parser.add_argument("-value", action = "append", help = "enter values (as hex string) of car property to edit in save")
 parser.add_argument("-property", action = "append", help = "enter name of car property to edit in save", choices = GT2SaveFile.CAR_PROPERTY_NAMES)
 return parser.parse_args()

def main(args):
 if not args.file: return
 argv = list(args.__dict__.items())
 argv.pop(0)
 argv.pop(0)
 save = GT2SaveFile(args.file)
 read = not any(arg[1] is not None for arg in argv)
 if read: save.print(args.save)
 else:
  save.update(args.save, args)
  save.save(save.path)

main(readArgs())