import argparse
from GT2Save import GT2Save

def readArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-aprog", action = "store", help = "set arcade progress", choices = list(GT2Save.ARCADE_PROGRESS.keys()))
    parser.add_argument("-car", action = "store", help = "set index (from 0 to 99) of career car to edit")
    parser.add_argument("-cash", action = "store", help = "set career cash")
    parser.add_argument("-cprog", action = "store", help = "set career progress", choices = list(GT2Save.CAREER_PROGRESS.keys()))
    parser.add_argument("-curr", action = "store", help = "set index (from 0 to 99) of current career car")
    parser.add_argument("-days", action = "store", help = "set career days")
    parser.add_argument("-lang", action = "store", help = "set language", choices = list(GT2Save.LANGUAGES.keys()))
    parser.add_argument("-lic", action = "store", help = "set career licenses", choices = list(GT2Save.LICENSES.keys()))
    parser.add_argument("-path", action = "store", help = "set save path")
    parser.add_argument("-prize", action = "store", help = "set career total prize")
    parser.add_argument("-prop", action = "append", help = "set career car's property to edit", choices = GT2Save.CAR_PROPERTY_NAMES)
    parser.add_argument("-races", action = "store", help = "set career total races")
    parser.add_argument("-read", action = "store_true", help = "read save(s)")
    parser.add_argument("-save", action = "store", help = "set save to read/edit, don't set to read/edit all saves", choices = ["0", "1", "2"])
    parser.add_argument("-val", action = "append", help = "set career car property's value (little endian hex string)")
    parser.add_argument("-wins", action = "store", help = "set career total wins")
    return parser.parse_args()

def main(args):
    if not args.path: return
    save = GT2Save(args.path)
    if args.read: save.read(args.save)
    else: save.update(args.save, args)

main(readArgs())