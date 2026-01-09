import argparse, os
from GT2Save import GT2Save

def readArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-path", action = "store", help = "set image path")
    parser.add_argument("-save", action = "store", help = "set save to read/edit, do not set to read/edit all saves", choices = ["0", "1", "2"])
    parser.add_argument("-read", action = "store_true", help = "read saves")
    parser.add_argument("-lang", action = "store", help = "set language", choices = list(GT2Save.LANGUAGES.keys()))
    parser.add_argument("-arc", action = "store", help = "set arcade progress", choices = list(GT2Save.ARCADE_PROGRESS.keys()))
    parser.add_argument("-car", action = "store", help = "set career progress", choices = list(GT2Save.CAREER_PROGRESS.keys()))
    parser.add_argument("-lic", action = "store", help = "set career license progress", choices = list(GT2Save.LICENSE_PROGRESS.keys()))
    parser.add_argument("-money", action = "store", help = "set career money")
    parser.add_argument("-days", action = "store", help = "set career days")
    parser.add_argument("-races", action = "store", help = "set career races")
    parser.add_argument("-wins", action = "store", help = "set career wins")
    parser.add_argument("-rank", nargs = 2, metavar = ("BEST_RANK", "RANK"), action = "store", help = "set career rankings")
    parser.add_argument("-prize", action = "store", help = "set career prize")
    parser.add_argument("-cur", metavar = ("CAR_INDEX"), action = "store", help = "set current career car (car index from 0 to car count - 1)")
    parser.add_argument("-edit", nargs = 2, metavar = ("CAR_INDEX", "HEX_STRING"), action = "store", help = "set career car bytes (bytes as little endian hex string)")

    return parser.parse_args()


def main(args):
    if not args.path or not os.path.exists(args.path):
        return

    save = GT2Save(args.path)
    if args.read:
        save.read(args.save)

    else:
        save.update(args.save, args)


if __name__ == "__main__":
    main(readArgs())