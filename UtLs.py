from __future__ import unicode_literals
import yt_dlp
import ffmpeg
import argparse
import os
import shutil
import subprocess, json
import random
import sys
import csv
import io
import xml.etree.cElementTree as ET
from xml.dom import minidom
import re
from PIL import Image

# TODO: CHECK DATA AFTER SONDERZEICHEN
# TODO: FIX RESULT SCREEN PICTURE
# TODO: FIX NAME FILE GENERATION (Fixed, but not tested)
# TODO: FIX LYRICS
# TODO: REMOVE FUNCTION
# TODO: FIX HELPPAGE AND FILL WITH MORE INFORMATIONS
# TODO: ADD README
# TODO: IMPLEMENT TXT DOWNLOADER
# TODO: ADD API FOR ULTRASTAR DBs (?)
# TODO: REMOVE DEBUG OUTPUT / ADD VERBOSE (?)
# TODO: REMOVE 100 SONGS LIMIT
# TODO: ASK BEFORE REPLACE
# TODO: FIX NOTES AFTER LYRICS WITHOUT NOTES HAVE THE WRONG LYRICS / Fix Lyrics Generation
parser = argparse.ArgumentParser(description= "LetsSingImporter - Please choose a Mode!")
parser.add_argument('--downloader', help="Mode for downloading Youtube Videos and converting them to Lets Sing Files", action='store_true')
parser.add_argument('--move', help="Mode to move files into the needed Filetree", action='store_true')
args, unknown = parser.parse_known_args()
argsdownloader=args.downloader
argsmove=args.move
if args.downloader == True and args.move == True:
    print("Please choose only one mode")
    sys.exit(1)
if args.downloader == True and args.move == False:
    parser = argparse.ArgumentParser(description='LetsSingImporterSwitch - Download Mode')
    parser.add_argument('--song', required=True, help="Song ID (Queen - Killer Queen => killerqueen)")
    parser.add_argument('--url', required=False, help="Youtube URL")
    parser.add_argument('--txt', default=False, help="TXT File from Ultrastar")
    parser.add_argument('--generate-vxla', action='store_true', help="Generate VXLA File")
    parser.add_argument('--keep-lyrics', action='store_true',
                        help="Keeps the text the lyrics for freestyle notes, but breaks the lyrics on screen under the notes")
    parser.add_argument('--randomize', action='store_true',
                        help="(NOT IMPLEMENTED) Activate to set random Images for backgrounds")
    parser.add_argument('--folder', default="./songs", help="Folder to save files")
  #  parser.add_argument('--atmosphere-folder', required=False, default="atmosphere/contents/",
  #                      help="Path to atmosphere/contents, default is ./atmosphere/contents")
else:
    if args.downloader == False and args.move == True:
        parser = argparse.ArgumentParser(description='LetsSingImporterSwitch - Move Mode')
        parser.add_argument('--folder', default="./songs", help="Folder where files are saved")
        parser.add_argument('--atmosphere-folder', required=False,
                             help="Path to the atmosphere folder", default=False)
        parser.add_argument('--song', required=True, help="Song ID (Queen - Killer Queen => killerqueen)")
        # parser.add_argument('--basefiles', help='name.txt, SongsDlc.tsv')
        parser.add_argument('--titleid', required=True, help="Title ID of the Base Game")
        parser.add_argument('--dlcid', required=True, help="Title ID of the DLC")
        parser.add_argument("--artist", default=None)
        parser.add_argument("--title", default=None)
        parser.add_argument("--genre", default=None)
        parser.add_argument("--year", default=None)
        parser.add_argument("--difficulty", default="Difficulty3")
        parser.add_argument("--lineone", default=None)
        parser.add_argument("--linetwo", default=None)
        parser.add_argument('--generate-vxla', action='store_true', help="Generate VXLA File")
        parser.add_argument('--keep-lyrics', action='store_true', help="Keeps the text the lyrics for freestyle notes, but breaks the lyrics underneath the notes")
    else:
        parser.print_help()
        sys.exit(0)
args, unknown = parser.parse_known_args()
SongFolder = args.song

class MyLogger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

class downloader:
    def __init__(self, song):
        song = f"{args.folder}/{song}/{song}"
        self.song = song
    def RemoveAudio(self):
        os.system(f"ffmpeg -i {self.song}.mp4 -vcodec copy -an {self.song}_noaudio.mp4")
        shutil.move(f"{self.song}_noaudio.mp4", f"{self.song}.mp4")
    def ConvertAudioFile(self): # TODO: Seperate Preview in own function, check if mp3 or ogg ...
        os.system(f"ffmpeg -i {self.song}.mp3 -c:a libvorbis -q:a 4 {self.song}.ogg")
        os.system(f"ffmpeg -t 30 -i {self.song}.ogg -acodec copy {self.song}_preview.ogg")
        os.remove(f"{self.song}.mp3")
    def CreateIcon(self):
        try:
            Icon = (
                ffmpeg
                .input(f"{self.song}_original.png")
                .filter('crop', '512', '512')
                .output(f'{self.song}.png')
                .overwrite_output()
            )
            ffmpeg.run(Icon)
        except:
            print("TRY OTHER CROP")
            Icon = (
                ffmpeg
                .input(f"{self.song}_original.png")
                .filter('crop', '256', '256')
                .output(f'{self.song}.png')
                .overwrite_output()
            )
            ffmpeg.run(Icon)
    def CreateThumbnail(self):
        for entry in [".png", ".jpg", ".webp"]:
            try:
                thumbnail = (
                    ffmpeg
                    .input(f"{self.song}{entry}")
                    .output(f"{self.song}_original.png")
                    .overwrite_output()
                    )
                ffmpeg.run(thumbnail)
                os.remove(f"{self.song}{entry}")
            except:
                continue
    def CreateBackgrounds(self):
        if args.randomize == True: # TODO: FIX RANDOMIZER
            from pymediainfo import MediaInfo
            media_info = MediaInfo.parse(f'{self.song}.mp4')
            duration_in_s = int(media_info.tracks[0].duration / 1000) - 5
            for entry in ["InGameLoading", "Result"]:
                timestamp=random.randint(5, duration_in_s)
                print(timestamp)
                os.system(f'ffmpeg -ss "{timestamp}" -i $(youtube-dl -f mp4 --get-url "{args.url}") -vframes 1 -q:v 2 {self.song}_{entry}.png')
        else:
            for entry in [f"{self.song}_InGameLoading.png", f"{self.song}_Result.png"]:
                try:
                    Background = (
                        ffmpeg
                            .input(f"{self.song}_original.png")
                            .filter('crop', '512', '512')
                            .output(entry)
                            .overwrite_output()
                    )
                    ffmpeg.run(Background)
                except:
                    print("TRY OTHER CROP")
                    Background = (
                        ffmpeg
                            .input(f"{self.song}_original.png")
                            .filter('crop', '256', '256')
                            .output(entry)
                            .overwrite_output()
                    )
                    ffmpeg.run(Background)
class move:
    def __init__(self):
        # Song meta
        self.Song = args.song
        self.SongMeta = {}
        self.AlreadyExists = False
        # Folder
        self.BaseFilesFolder = f"{args.folder}/basefiles"
        self.BaseFilesFolderAtmosphere = f"{args.folder}/basefiles_atmosphere"
        self.SongFolder = f"{args.folder}/{args.song}"
        self.AtmosphereBaseFolder = f"{args.atmosphere_folder}/contents/{args.titleid}/romfs/Data/StreamingAssets"
        self.AtmosphereDLCFolder = f"{args.atmosphere_folder}/contents/{args.dlcid}/romfs"
        self.AtmosphereMediaFolder = f"{args.atmosphere_folder}/contents/{args.dlcid}/romfs/Songs"
        # Files
        self.ContentTXT = ""
        self.ContentTSV = ""
        self.FileTXT = ""
        self.FileTSV = ""
        self.FileXML = ""

    def checkFiles(self):
        missing = []
        for entry in [".mp4", ".ogg", ".png",".txt", ".vxla", "_InGameLoading.png", "_Result.png"]:
            if not os.path.isfile(f"{self.SongFolder}/{self.Song}{entry}"):
                missing.append(f"{self.Song}{entry}")
        if len(missing) != 0:
            print(f'Found missing Files: {", ".join(missing)}')
            sys.exit(1)

    def loadFiles(self):
        self.ContentTXT = open(f"{self.BaseFilesFolder}/name.txt").readlines()
        self.ContentTSV = list(csv.reader(open(f"{self.BaseFilesFolder}/SongsDLC.tsv").readlines(), delimiter="	"))
        shutil.copy(f"{self.BaseFilesFolder}/name.txt", f"{self.BaseFilesFolder}/name.txt_bk")
        shutil.copy(f"{self.BaseFilesFolder}/SongsDLC.tsv", f"{self.BaseFilesFolder}/SongsDLC.tsv_bk")
        self.FileTXT = open(f"{self.BaseFilesFolder}/name.txt", "w")
        self.FileTSV = open(f"{self.BaseFilesFolder}/SongsDLC.tsv", "w")
        self.FileXML = open(f"{self.SongFolder}/{self.Song}_meta.xml", "w")
    def SongAlreadyExists(self):
        for line in self.ContentTSV:
            if self.Song in line[2]:
                self.SongMeta.update({"UID": line[1]})
                self.SongMeta.update({"ID": line[2]})
                return True
        return False

    def validateMeta(self):
        for entry in ["ARTIST", "TITLE", "GENRE", "YEAR"]:
            try:
                self.SongMeta[entry]
            except:
                print(f"Missing Metadata {entry}")
                sys.exit(1)
        if args.difficulty not in ["Difficulty1", "Difficulty2", "Difficulty3", "Difficulty4", "Difficulty5"]:
            print(f'{args.difficulty} is not a valid Difficulty')
            sys.exit(1)
        else:
            self.SongMeta.update({"DIFF": args.difficulty})
        if self.SongMeta["GENRE"] not in ["Rock", "rock", "Pop", "pop"]:
            print(f'{self.SongMeta["GENRE"]} is not a valid Genre')
            sys.exit(1)

    def loadMeta(self):
        self.AlreadyExists = self.SongAlreadyExists()
        if self.AlreadyExists is False:
            print(self.ContentTSV)
            if int(self.ContentTSV[len(self.ContentTSV)-1][1]) - 1 <= 899:
                print("100 Customssongs full")
                sys.exit(1)
            if int(self.ContentTSV[len(self.ContentTSV)-1][1]) - 1 < 900:
                self.SongMeta.update({"UID": int(999)})
            else:
                self.SongMeta.update({"UID": int(self.ContentTSV[len(self.ContentTSV)-1][1]) - 1})
            self.SongMeta.update({"ID": self.Song})
            print(self.SongMeta)
        for line in self.ContentTXT:
            line = line.replace("\n", "").replace(":", " ")
            if not line.startswith("#"):
                continue
            if line.startswith("#ARTIST") and args.artist is None:
                self.SongMeta.update({"ARTIST": line.replace("#ARTIST ", "")})
                continue
            if line.startswith("#TITLE"):
                self.SongMeta.update({"TITLE": line.replace("#TITLE ", "")})
                continue
            if line.startswith("#GENRE") and args.genre is None:
                self.SongMeta.update({"GENRE": line.replace("#GENRE ", "")})
                continue
            if line.startswith("#YEAR") and args.year is None:
                self.SongMeta.update({"YEAR": line.replace("#YEAR ", "")})
                continue
        if args.artist is not None:
            self.SongMeta.update({"ARTIST": args.artist})
        if args.title is not None:
            self.SongMeta.update({"TITLE": args.title})
        if args.genre is not None:
            self.SongMeta.update({"GENRE": args.genre})
        if args.year is not None:
            self.SongMeta.update({"YEAR": args.year})
        if args.lineone == None:
            self.SongMeta.update({"LINEONE": self.SongMeta["TITLE"]})
        else:
            self.SongMeta.update({"LINEONE": args.lineone})
        if args.linetwo == None:
            self.SongMeta.update({"LINETWO": ""})
        else:
            self.SongMeta.update({"LINETWO": args.linetwo})
        self.validateMeta()

    def generateXML(self):
        self.FileXML.write(f"""﻿<?xml version="1.0" encoding="utf-8"?>
<DLCSong xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Genre>{self.SongMeta["GENRE"]}</Genre>
  <Id>{self.SongMeta["ID"]}</Id>
  <Uid>{self.SongMeta["UID"]}</Uid>
  <Artist>{self.SongMeta["ARTIST"]}</Artist>
  <Title>{self.SongMeta["TITLE"]}</Title>
  <Year>{self.SongMeta["YEAR"]}</Year>
  <Ratio>Ratio_16_9</Ratio>
  <Difficulty>{self.SongMeta["DIFF"]}</Difficulty>
  <Feat />
  <Line1>{self.SongMeta["LINEONE"]}</Line1>
  <Line2>{self.SongMeta["LINETWO"]}</Line2>
</DLCSong>
        """)
        self.FileXML.close()
    def generateFiles(self):
        AlreadyExists = False
        for line in self.ContentTSV:
            if self.Song in line[2]:
                AlreadyExists = True
                print("MATCH")
                #print("	".join(['x', self.SongMeta["UID"], self.SongMeta["ID"], self.SongMeta["ARTIST"], self.SongMeta["TITLE"], self.SongMeta["YEAR"], '1', 'x', 'x', 'x', 'x', '1', 'RATIO_4_3', '', '', '', 'x', 'x', '', '', '', 'x', '', '', 'x', '', '', 'x', 'x']))
                self.FileTSV.write('	'.join(['x', str(self.SongMeta["UID"]), self.SongMeta["ID"], self.SongMeta["ARTIST"], self.SongMeta["TITLE"], self.SongMeta["YEAR"], '1', 'x', 'x', 'x', 'x', '1', 'RATIO_4_3', '', '', '', 'x', 'x', '', '', '', 'x', '', '', 'x', '', '', 'x', 'x']) + "\n")
                continue
            else:
                self.FileTSV.write('	'.join(line) + "\n")
        if not AlreadyExists:
            self.FileTSV.write('	'.join(['x', str(self.SongMeta["UID"]), self.SongMeta["ID"], self.SongMeta["ARTIST"], self.SongMeta["TITLE"], self.SongMeta["YEAR"], '1', 'x', 'x', 'x', 'x', '1', 'RATIO_4_3', '', '', '', 'x', 'x', '', '', '', 'x', '', '', 'x', '', '', 'x', 'x']) + "\n")

        self.FileTSV.close()
        AlreadyAdded = False
        for line in self.ContentTXT:
            if self.SongMeta["ID"] in line:
                AlreadyAdded = True
                self.FileTXT.write(self.SongMeta["ID"] + "\r\n")
                continue
            else:
                self.FileTXT.write(line.replace("\n", "") + "\r\n")
        if not AlreadyAdded:
            self.FileTXT.write(self.SongMeta["ID"] + "\r\n")
        self.FileTXT.close()
    def move(self):
        if not os.path.exists(self.AtmosphereMediaFolder):
            os.makedirs(self.AtmosphereMediaFolder)
            for folder in ["audio", "audio_preview", "backgrounds", "covers", "videos", "vxla"]:
                os.makedirs(f"{self.AtmosphereMediaFolder}/{folder}")
                if folder == "backgrounds":
                    for background_folder in ["Results", "InGameLoading"]:
                        os.makedirs(f"{self.AtmosphereMediaFolder}/backgrounds/{background_folder}")
        if not os.path.exists(self.AtmosphereDLCFolder):
            os.makedirs(self.AtmosphereDLCFolder)
        if not os.path.exists(self.AtmosphereBaseFolder):
            os.makedirs(self.AtmosphereBaseFolder)
        shutil.copy(f"{self.SongFolder}/{self.Song}.ogg", f"{self.AtmosphereMediaFolder}/audio/{self.Song}.ogg")
        shutil.copy(f"{self.SongFolder}/{self.Song}.ogg", f"{self.AtmosphereMediaFolder}/audio_preview/{self.Song}_preview.ogg")
        shutil.copy(f"{self.SongFolder}/{self.Song}_InGameLoading.png",
                    f"{self.AtmosphereMediaFolder}/backgrounds/InGameLoading/{self.Song}_InGameLoading.png")
        shutil.copy(f"{self.SongFolder}/{self.Song}_Result.png", f"{self.AtmosphereMediaFolder}/backgrounds/Results/{self.Song}_Result.png")
        shutil.copy(f"{self.SongFolder}/{self.Song}.png", f"{self.AtmosphereMediaFolder}/covers/{self.Song}.png")
        shutil.copy(f"{self.SongFolder}/{self.Song}.vxla", f"{self.AtmosphereMediaFolder}/vxla/{self.Song}.vxla")
        shutil.copy(f"{self.SongFolder}/{self.Song}.mp4", f"{self.AtmosphereMediaFolder}/videos/{self.Song}.mp4")
        shutil.copy(f"{self.BaseFilesFolder}/name.txt", f"{self.AtmosphereDLCFolder}/name.txt")
        shutil.copy(f"{self.BaseFilesFolder}/SongsDLC.tsv", f"{self.AtmosphereBaseFolder}/SongsDLC.tsv")
        shutil.copy(f"{self.SongFolder}/{self.Song}_meta.xml", f"{self.AtmosphereDLCFolder}/{self.Song}_meta.xml")

# Credit => dh4rry
class UltraStar2LetsSing:
    def __init__(self, input):
        self.SongTXT = input
    def parse_file(self):
        data = {"notes": []}
        with io.open(self.SongTXT, "r", encoding="ISO-8859-1", errors='ignore') as f:
            for line in f:
                line = line.replace('\n', '')
                if line.startswith("#"):
                    p = line.split(":", 1)
                    if len(p) == 2:
                        data[p[0][1:]] = p[1]
                else:
                    note_arr = line.split(" ", 4)
                    data["notes"].append(note_arr)
        return data

    def map_data(self, us_data, pitch_corr):
        sing_it = {"text": [], "notes": [], "pages": [], "notes_golden": []}
        bpm = float(us_data["BPM"].replace(',', '.'))
        gap = float(us_data["GAP"].replace(',', '.')) / 1000
        min_note = 1
        last_page = 0.0
        for note in us_data["notes"]:
            if note[0] == ":" or note[0] == "*":
                start = float(note[1]) * 60 / bpm / 4 + gap
                end = start + float(note[2]) * 60 / bpm / 4
                sing_it["text"].append({"t1": start, "t2": end, "value": note[4]})
                nint = int(note[3])
                if nint < min_note:
                    nint = min_note

                sing_it["notes"].append(
                    {"t1": start, "t2": end, "value": nint + pitch_corr})
                if note[0] == "*":
                    sing_it["notes_golden"].append(
                        {"t1": start, "t2": end, "value": nint + pitch_corr})
            elif note[0] == "-":
                start = last_page
                end = float(note[1]) * 60 / bpm / 4 + gap
                last_page = end
                sing_it["pages"].append(
                    {"t1": start, "t2": end, "value": ""})
            elif note[0] == "E":
                if end > last_page:
                    start = last_page
                    sing_it["pages"].append(
                        {"t1": start, "t2": end, "value": ""})
            elif args.keep_lyrics and note[0] == "F":
                start = float(note[1]) * 60 / bpm / 4 + gap
                end = start + float(note[2]) * 60 / bpm / 4
                if note[4] == 0:
                    sing_it["text"].append({"t1": start, "t2": end, "value": ""})
                else:
                    sing_it["text"].append({"t1": start, "t2": end, "value": note[4]})
                nint = int(note[3])
                if nint < min_note:
                    nint = min_note
        return sing_it

    def write_intervals(self, interval_arr, parent):
        for interval in interval_arr:
            ET.SubElement(parent, "Interval",
                          t1="{0:.3f}".format(interval["t1"]), t2="{0:.3f}".format(interval["t2"]),
                          value=str(interval["value"]))

    def write_vxla_file(self, sing_it, filename):
        root = ET.Element("AnnotationFile", version="2.0")

        doc = ET.SubElement(root, "IntervalLayer", datatype="STRING",
                            name="structure", units="", description="")
        ET.SubElement(doc, "Interval", t1="2.000", t2="3.000", value="couplet1")

        doc = ET.SubElement(root, "IntervalLayer", datatype="STRING",
                            name="shortversion", units="", description="")
        ET.SubElement(doc, "Interval", t1="0.000",
                      t2="60.000", value="shortversion")

        doc = ET.SubElement(root, "IntervalLayer", datatype="STRING",
                            name="lyrics", units="", description="")
        self.write_intervals(sing_it["text"], doc)

        doc = ET.SubElement(root, "IntervalLayer", datatype="STRING",
                            name="lyrics_cut", units="", description="")
        self.write_intervals(sing_it["text"], doc)

        doc = ET.SubElement(root, "IntervalLayer", datatype="UINT8",
                            name="notes", units="", description="")
        self.write_intervals(sing_it["notes"], doc)

        doc = ET.SubElement(root, "IntervalLayer", datatype="UINT8",
                            name="notes_golden", units="", description="")
        self.write_intervals(sing_it["notes_golden"], doc)

        doc = ET.SubElement(root, "IntervalLayer", datatype="STRING",
                            name="pages", units="", description="")
        self.write_intervals(sing_it["pages"], doc)
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(
            encoding="ISO-8859-1", indent="   ")
        with open(filename, "wb") as f:
            f.write(xmlstr)

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting...')


if argsdownloader is True and argsmove is False:
    ydl_opts = {
        'format': 'mp4',
        'logger': MyLogger(),
        'outtmpl': f"{args.folder}/{args.song}/{args.song}.%(ext)s",
        'progress_hooks': [my_hook],
        'keepvideo': True,
        'writethumbnail': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    if args.generate_vxla:
        if args.txt is False:
            input=f"{args.folder}/{args.song}/{args.song}.txt"
        else:
            input=args.txt
        if not os.path.isfile(input):
            print("TXT not found")
            sys.exit(1)
        u2ls = UltraStar2LetsSing(input)
        u2ls.write_vxla_file(u2ls.map_data(u2ls.parse_file(), 48), f"{args.folder}/{args.song}/{args.song}.vxla")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(args.url)
        _downloader = downloader(args.song)
        _downloader.CreateThumbnail()
        _downloader.ConvertAudioFile()
        _downloader.CreateIcon()
        _downloader.RemoveAudio()
        _downloader.CreateBackgrounds()

if argsdownloader is False and argsmove is True:
    if args.generate_vxla:
        if not os.path.isfile(f"{args.folder}/{args.song}/{args.song}.txt"):
            print("TXT not found")
            sys.exit(1)
        else:
            input=f"{args.folder}/{args.song}/{args.song}.txt"
        u2ls = UltraStar2LetsSing(input)
        u2ls.write_vxla_file(u2ls.map_data(u2ls.parse_file(), 48), f"{args.folder}/{args.song}/{args.song}.vxla")
    LetsSingMover = move()
    LetsSingMover.checkFiles()
    LetsSingMover.loadFiles()
    LetsSingMover.loadMeta()
    LetsSingMover.generateXML()
    LetsSingMover.generateFiles()
    if not args.atmosphere_folder is False:
        LetsSingMover.move()
