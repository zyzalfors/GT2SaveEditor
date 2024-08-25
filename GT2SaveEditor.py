import argparse
from GT2Save import GT2Save

def readArgs():
 parser = argparse.ArgumentParser()
 parser.add_argument("-path", action = "store", help = "set file's path")
 parser.add_argument("-save", action = "store", help = "set save to read/edit, don't set to read/edit all saves", choices = ["0", "1", "2"])
 parser.add_argument("-read", action = "store_true", help = "read save(s)")
 parser.add_argument("-cash", action = "store", help = "set cash")
 parser.add_argument("-lang", action = "store", help = "set language", choices = ["ja", "en-us", "en-gb", "fr", "de", "it", "es"])
 parser.add_argument("-days", action = "store", help = "set days")
 parser.add_argument("-races", action = "store", help = "set total races")
 parser.add_argument("-wins", action = "store", help = "set total wins")
 parser.add_argument("-prize", action = "store", help = "set total prize")
 parser.add_argument("-lic", action = "store", help = "set licenses", choices = ["none", "kid", "bronze", "silver", "gold"])
 parser.add_argument("-curr", action = "store", help = "set index (from 0 to 99) of current car")
 parser.add_argument("-car", action = "store", help = "set index (from 0 to 99) of car to edit")
 parser.add_argument("-prop", action = "append", help = "set car property to edit", choices = GT2Save.CAR_PROPERTY_NAMES)
 parser.add_argument("-val", action = "append", help = "set car property's value (hex string)")
 return parser.parse_args()

def main(args):
 if not args.path: return
 save = GT2Save(args.path)
 if args.read: save.print(args.save)
 else:
  save.update(args.save, args)
  save.save(save.path)

main(readArgs())