# LetsSingImporterSwitch
[needs a revision]  
This is a script for Lets Sing 2022, to import custom songs from Ultrastar.

# Usage
To download a song:  
1. python3 UtLs.py --downloader --song gurenge --url https://www.youtube.com/watch?v=JHw8gwQXpWI  
The script will download and convert the video to the needed mediafiles.

2. Now you got a songs folder and in it a folder with the songid (gurenge), there you place your Ultrastar TXT
3. In the "songs"-folder you create the folder "basefiles" and place in it your name.txt and SongsDLC.tsv. (PLEASE BACKUP THE DATA)

To convert a song:  
python3 UtLs.py --move --titleid "0100CC30149B8000" --dlcid "0100CC30149B9002" --song gurenge --title "Gurenge" --genre "Rock" --year 2019 --artist "LiSA" --generate-vxla --atmospher-folder [PATH TO YOUR ATMOSPHERE FOLDER ON THE SD_CARD] 

For a advanced tutorial check: ttps://gbatemp.net/threads/tutorial-add-custom-songs-to-lets-sing-2022-from-ultrastar.607817/
