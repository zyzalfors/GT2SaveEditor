# Gran Turismo 2 Save Editor
This command-line tool allows users to read and edit save files for the PlayStation game Gran Turismo 2. It supports all save versions and regions, with partial compatibility for [GT2+](https://www.gtplanet.net/forum/threads/mod-gran-turismo-2-plus-bug-fixes-restored-content-and-new-content-beta-7-released.378282/) and [GT2AS](https://x.com/projectaspec) saves.

It supports .mcr, .gme, and .psv formats but cannot resign .psv saves after editing.

The tool can read various properties such as game id, checksum, money, language, days, races, wins, rankings, prize, licenses, car count, current car, car data, career/arcade progress, and career percentage.

It also allows editing of properties like money, language, days, races, wins, rankings, prize, licenses, current car, car data, and career/arcade progress.

```
usage: GT2SaveEditor.py.py [-h] [-path PATH] [-save {0,1,2}] [-read] [-lang {ja,en-us,en-gb,fr,de,it,es}]
                           [-arc {none,easy,normal,hard}] [-car {none,1st,2nd,3rd,4th,5th,6th}]
                           [-lic {none,kid,bronze,silver,gold}] [-money MONEY]
                           [-days DAYS] [-races RACES] [-wins WINS] [-rank BEST_RANK RANK]
                           [-prize PRIZE] [-cur CAR_INDEX] [-edit CAR_INDEX HEX_STRING]

options:
  -h, --help                          show this help message and exit
  -path PATH                          set image path
  -save {0,1,2}                       set save to read/edit, do not set to read/edit all saves read saves
  -lang {ja,en-us,en-gb,fr,de,it,es}  set language
  -arc {none,easy,normal,hard}        set arcade progress
  -car {none,1st,2nd,3rd,4th,5th,6th} set career progress
  -lic {none,kid,bronze,silver,gold}  set career license progress
  -money MONEY                        set career money
  -days DAYS                          set career days
  -races RACES                        set career races
  -wins WINS                          set career wins
  -rank BEST_RANK RANK                set career rankings
  -prize PRIZE                        set career prize
  -cur CAR_INDEX                      set current career car (car index from 0 to car count - 1)
  -edit CAR_INDEX HEX_STRING          set career car bytes (bytes as little endian hex string)
```

More details about Gran Turismo 2 save files can be found in the following resources:
- https://adamdadeh.github.io/fun/2019/03/28/binary_files
- https://web.archive.org/web/20010613205439/http://ubb.granturismo.com/Forum18/HTML/000929.html
- https://web.archive.org/web/20080221203449/http://www.rogs.dial.pipex.com/indexref.htm
- https://web.archive.org/web/20190823163405/http://www.angelfire.com/fl4/JuanDon/SaveFileFormat.html

Similar repositories:
- https://github.com/iComputer7/GT2Bizhawk
- https://github.com/pez2k/gt2tools/tree/master/GT2SaveEditor/GT2SaveEditor

General information about raw PlayStation memory card format can be found here:
- https://github.com/ShendoXT/memcardrex
- https://www.psdevwiki.com/ps3/PS1_Savedata

Mappings between car names and car codes are available at:
- https://web.archive.org/web/20080223151654/http://www.rogs.dial.pipex.com/carsb.htm
- https://docs.google.com/spreadsheets/d/15gqtU6hOl-Y_k7bpX_aHBed6I4xjeRF4tTFuY19AoUI/edit?gid=2038508433#gid=2038508433
- https://web.archive.org/web/20210618040725/http://www.lecoyote.net/gtweboldbc/gt2actio.htm
