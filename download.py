from __future__ import unicode_literals
import yt_dlp
import ffmpeg
import argparse
import os
import shutil
import subprocess, json
import random
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--song', required=True)
parser.add_argument('--url', required=True)
parser.add_argument('--randomize', type=bool, default=False)
args = parser.parse_args()
SongFolder = args.song
class MyLogger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

class LetsSingConverter:
    def __init__(self, song):
        song = f"{song}/{song}"
        self.song = song
        thumbnail = (
            ffmpeg
            .input(f"{song}.webp")
            .output(f"{song}_original.png")
            .overwrite_output()
            )
        ffmpeg.run(thumbnail)
        os.remove(f"{song}.webp")
    def RemoveAudio(self):
        os.system(f"ffmpeg -i {self.song}.mp4 -vcodec copy -an {self.song}_noaudio.mp4")
        shutil.move(f"{self.song}_noaudio.mp4", f"{self.song}.mp4")
    def ConvertAudioFile(self):
        os.system(f"ffmpeg -i {self.song}.mp3 -c:a libvorbis -q:a 4 {self.song}.ogg")
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
    def CreateBackgrounds(self):
        if args.randomize == True:
            from pymediainfo import MediaInfo
            media_info = MediaInfo.parse(f'{self.song}.mp4')
            duration_in_s = int(media_info.tracks[0].duration / 1000) - 5
            for entry in ["InGameLoading", "Result"]:
                timestamp=random.randint(5, duration_in_s)
                print(timestamp)
                os.system(f'ffmpeg -ss "{timestamp}" -i $(youtube-dl -f mp4 --get-url "{args.url}") -vframes 1 -q:v 2 {self.song}_{entry}.png')
        else:
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
            shutil.copy(f"{self.song}_original.png", f"{self.song}_InGameLoading.png" )
            shutil.copy(f"{self.song}_original.png", f"{self.song}_Result.png" )


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'format': 'mp4',
    'logger': MyLogger(),
    'outtmpl': f"{args.song}/{args.song}.%(ext)s",
    'progress_hooks': [my_hook],
    'keepvideo': True,
    'writethumbnail': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(args.url)

    Converter = LetsSingConverter(args.song)
    Converter.ConvertAudioFile()
    Converter.CreateIcon()
    Converter.RemoveAudio()
    Converter.CreateBackgrounds()



