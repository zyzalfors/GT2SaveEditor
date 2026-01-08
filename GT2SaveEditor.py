import argparse
from GT2Save import GT2Save

def readArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-path", action = "store", help = "set image path")
    parser.add_argument("-save", action = "store", help = "set save to read/edit, do not set to read/edit all saves", choices = ["0", "1", "2"])
    parser.add_argument("-read", action = "store_true", help = "read saves")
    parser.add_argument("-lang", action = "store", help = "set language", choices = list(GT2Save.LANGUAGES.keys()))
    parser.add_argument("-arc", action = "store", help = "set arcade progress", choices = list(GT2Save.ARCADE_PROGRESS.keys()))
    parser.add_argument("-car", action = "store", help = "set career progress", choices = list(GT2Save.CAREER_PROGRESS.keys()))
    parser.add_argument("-lic", action = "store", help = "set license progress", choices = list(GT2Save.LICENSE_PROGRESS.keys()))
    parser.add_argument("-money", action = "store", help = "set money")
    parser.add_argument("-days", action = "store", help = "set days")
    parser.add_argument("-races", action = "store", help = "set races")
    parser.add_argument("-wins", action = "store", help = "set wins")
    parser.add_argument("-prize", action = "store", help = "set prize")
    parser.add_argument("-cur", action = "store", help = "set index of current car")
    parser.add_argument("-edit", nargs = 2, metavar = ("CAR_INDEX", "HEX_STRING"), action = "store", help = "set car bytes as little endian hex string")

    return parser.parse_args()


def main(args):
    if not args.path:
        return

    save = GT2Save(args.path)
    if args.read:
        save.read(args.save)

    else:
        save.update(args.save, args)


main(readArgs())