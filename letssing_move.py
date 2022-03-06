import argparse
import csv
import sys
import os
import shutil
# check auf sonderzeichen im namen
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--folder', required=False, default="atmosphere/contents/")
#parser.add_argument('--basefiles', help='name.txt, SongsDlc.tsv')
parser.add_argument('--titleid', required=True)
parser.add_argument('--dlcid', required=True)
parser.add_argument('--song', required=True)
parser.add_argument("--artist", default=None)
parser.add_argument("--title", default=None)
parser.add_argument("--genre", default=None)
parser.add_argument("--year", default=None)
parser.add_argument("--difficulty", default="Difficulty3")
parser.add_argument("--lineone", default=None)
parser.add_argument("--linetwo", default=None)
args = parser.parse_args()
Song = args.song
SongFolder = "songs/" + args.song
BaseFilesFolder = "songs/basefiles"

BaseFilesFolderAtmosphere = "songs/basefiles_atmosphere"
if os.path.exists(BaseFilesFolderAtmosphere):
    shutil.rmtree(BaseFilesFolderAtmosphere)
    os.makedirs(BaseFilesFolderAtmosphere)
if not os.path.isfile(f"{SongFolder}/{Song}.mp4"):
    print("No mp4 found")
    sys.exit(1)
if not os.path.isfile(f"{SongFolder}/{Song}.ogg"):
    print("No ogg found")
    sys.exit(1)
if not os.path.isfile(f"{SongFolder}/{Song}.png"):
    print("No png found")
    sys.exit(1)
if not os.path.isfile(f"{SongFolder}/{Song}.txt"):
    print("No txt found")
if not os.path.isfile(f"{SongFolder}/{Song}.vxla"):
    print("No vxla found")
    sys.exit(1)
if not os.path.isfile(f"{SongFolder}/{Song}_InGameLoading.png"):
    print("No InGameLoading found")
    sys.exit(1)
if not os.path.isfile(f"{SongFolder}/{Song}_Result.png"):
    print("No Result found")
    sys.exit(1)
SongTXT = f"{SongFolder}/{Song}.txt"
SongXML = f"{SongFolder}/{Song}_meta.xml"
SongMediaFolder = f"{SongFolder}/atmosphere/contents/{args.dlcid}/romfs/Songs"
overwrite = False
#NameTXT = f"{args.folder}/{args.dlcid}/romfs/name.txt"
NameTXT = f"{BaseFilesFolder}/name.txt"
DLCROOT = f"{BaseFilesFolderAtmosphere}/atmosphere/contents/{args.dlcid}/romfs/"
SongMeta = {}
#SongMeta = {"ARTIST": "", "TITLE": "", "GENRE": "", "YEAR": ""}

#SongsDLC_Path = f"{args.folder}/{args.titleid}/romfs/Data/StreamingAssets/SongsDLC.tsv"
SongsDLC_Path = f"{BaseFilesFolder}/SongsDLC.tsv"
BASEROOT = f"{BaseFilesFolderAtmosphere}/atmosphere/contents/{args.titleid}/romfs/Data/StreamingAssets/"
SongsDLC_File = open(SongsDLC_Path, "r")
SongsDLC = csv.reader(SongsDLC_File, delimiter = "	")
SongsDLC_Array = []

for line in SongsDLC:
    SongsDLC_Array.append(line)
    if args.song in line:
        SongMeta.update({"UID": line[1]})
        SongMeta.update({"ID": line[2]})
        overwrite = True
SongsDLC_Last = SongsDLC_Array[(len(SongsDLC_File.readlines()))-1]
if overwrite != True:
    if int(SongsDLC_Last[1])-1 == 899:
        print("100 Customssongs full")
        sys.exit(1)
    if int(SongsDLC_Last[1])-1 < 900:
        SongMeta.update({"UID": int(999)})
    else:
        SongMeta.update({"UID": int(SongsDLC_Last[1])-1})
    SongMeta.update({"ID": args.song})
for line in open(SongTXT).readlines():
    line=line.replace("\n", "").replace(":", " ")
    if line.startswith("#") == False:
        continue
    if line.startswith("#ARTIST") and args.artist is None:
        SongMeta.update({"ARTIST": line.replace("#ARTIST ", "")})
        continue
    if line.startswith("#TITLE"):
        SongMeta.update({"TITLE": line.replace("#TITLE ", "")})
        print(line)
        continue
    if line.startswith("#GENRE") and args.genre is None:
        SongMeta.update({"GENRE": line.replace("#GENRE ", "")})
        continue
    if line.startswith("#YEAR") and args.year is None:
        SongMeta.update({"YEAR": line.replace("#YEAR ", "")})
        continue
if args.artist is not None:
    SongMeta.update({"ARTIST": args.artist})
if args.title is not None:
    SongMeta.update({"TITLE": args.title})
if args.genre is not None:
    SongMeta.update({"GENRE": args.genre})
if args.year is not None:
    SongMeta.update({"YEAR": args.year})

for entry in ["ARTIST", "TITLE", "GENRE", "YEAR"]:
    try:
        SongMeta[entry]
    except:
        print(f"Missing Metadata {entry}")
        sys.exit(1)
if args.difficulty not in ["Difficulty1", "Difficulty2", "Difficulty3", "Difficulty4", "Difficulty5"]:
    print(f'{args.difficulty} is not a valid Difficulty')
    sys.exit(1)
else:
    SongMeta.update({"DIFF": args.difficulty})
if SongMeta["GENRE"] not in ["Rock", "rock", "Pop", "pop"]:
    print(f'{SongMeta["GENRE"]} is not a valid Genre')
    sys.exit(1)

if args.lineone == None:
    SongMeta.update({"LINEONE": SongMeta["TITLE"]})
else:
    SongMeta.update({"LINEONE": args.lineone})
if args.linetwo == None:
    SongMeta.update({"LINETWO": ""})
else:
    SongMeta.update({"LINETWO": args.linetwo})
output = ""
first = True

# for line in SongsDLC_Array:
#     print(line[4])
#     if line[4] == SongMeta["TITLE"]:
#         print(f'Title "{SongMeta["TITLE"]}" already used')
#         sys.exit(2)
for line in SongsDLC_Array:
    print(line[2])
    if line[2] == SongMeta["ID"]:
        overwrite = True
        # print(f'ID "{SongMeta["ID"]}" already used')
        # sys.exit(2)
SongsDLC_File.close()
for line in open(NameTXT, "r").readlines():
    line = line.replace("\n", "")
    if line == SongMeta["ID"]:
        overwrite = True
        # print(f'ID "{SongMeta["ID"]}" already used IN NAME.TXT')
        # sys.exit(2)
with open(NameTXT, "a") as writefile:
    writefile.write(SongMeta["ID"] + "\r\n")

for entry in ['x', SongMeta["UID"], args.song, SongMeta["ARTIST"], SongMeta["TITLE"], SongMeta["YEAR"], '1', 'x', 'x', 'x', 'x', '1', 'RATIO_4_3', '', '', '', 'x', 'x', '', '', '', 'x', '', '', 'x', '', '', 'x', 'x']:
    if first == True:
        output = output + str(entry)
        first = False
        continue
    output = output + "	" + str(entry)
SongsDLC_File_Lines = open(SongsDLC_Path, "r").readlines()
SongsDLC_File = open(SongsDLC_Path, "w")
for line in SongsDLC_File_Lines:
    if overwrite == True and SongMeta["ID"] in line:
        SongsDLC_File.write(output + "\n")
    else:
        SongsDLC_File.write(line)
SongsDLC_File.close()
SongXML_File = open(f"{SongXML}", "w+")
SongXML_File.write(f"""﻿<?xml version="1.0" encoding="utf-8"?>
<DLCSong xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Genre>{SongMeta["GENRE"]}</Genre>
  <Id>{SongMeta["ID"]}</Id>
  <Uid>{SongMeta["UID"]}</Uid>
  <Artist>{SongMeta["ARTIST"]}</Artist>
  <Title>{SongMeta["TITLE"]}</Title>
  <Year>{SongMeta["YEAR"]}</Year>
  <Ratio>Ratio_16_9</Ratio>
  <Difficulty>{SongMeta["DIFF"]}</Difficulty>
  <Feat />
  <Line1>{SongMeta["LINEONE"]}</Line1>
  <Line2>{SongMeta["LINETWO"]}</Line2>
</DLCSong>
""")
SongXML_File.close()

if not os.path.exists(SongMediaFolder):
    os.makedirs(SongMediaFolder)
    for folder in ["audio", "audio_preview", "backgrounds", "covers", "videos", "vxla"]:
        os.makedirs(f"{SongMediaFolder}/{folder}")
        if folder == "backgrounds":
            for background_folder in ["Results", "InGameLoading"]:
                os.makedirs(f"{SongMediaFolder}/backgrounds/{background_folder}")
if not os.path.exists(DLCROOT):
    os.makedirs(DLCROOT)
if not os.path.exists(BASEROOT):
    os.makedirs(BASEROOT)
shutil.copy(f"{SongFolder}/{Song}.ogg", f"{SongMediaFolder}/audio/{Song}.ogg" )
shutil.copy(f"{SongFolder}/{Song}.ogg", f"{SongMediaFolder}/audio_preview/{Song}_preview.ogg" )
shutil.copy(f"{SongFolder}/{Song}_InGameLoading.png", f"{SongMediaFolder}/backgrounds/InGameLoading/{Song}_InGameLoading.png")
shutil.copy(f"{SongFolder}/{Song}_Result.png", f"{SongMediaFolder}/backgrounds/Results/{Song}_Result.png")
shutil.copy(f"{SongFolder}/{Song}.png", f"{SongMediaFolder}/covers/{Song}.png")
shutil.copy(f"{SongFolder}/{Song}.vxla", f"{SongMediaFolder}/vxla/{Song}.vxla" )
shutil.copy(f"{SongFolder}/{Song}.mp4", f"{SongMediaFolder}/videos/{Song}.mp4")
shutil.copy(f"{BaseFilesFolder}/name.txt", f"{DLCROOT}/name.txt")
shutil.copy(f"{BaseFilesFolder}/SongsDLC.tsv", f"{BASEROOT}/SongsDLC.tsv")
shutil.copy(f"{SongXML}", f"{DLCROOT}/{Song}_meta.xml")
print(SongXML)
print(SongMeta)
# for line in SongsDLC:
#     print(line)
