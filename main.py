import sys
import os
import requests
import json
from urllib.request import urlopen
import bs4
import re
import platform as Plat
from time import sleep
import mutagen
from mutagen.easyid3 import EasyID3

OpSys = (Plat.system())
Version = 2.0
Debug = False
if OpSys == "Windows":
    os.system("title Xequinox's Soundcloud Downloader [" + str(Version) + "]");
clientid = "tgoEjKtQsCqtiffoqeHxtnND4Lx7zBqV"
LatestVer = requests.get('https://pastebin.com/raw/QDzApaBF').text
DownloadLink = requests.get('https://pastebin.com/raw/BbTKyDni').text


def clearScreen():
    if OpSys != "Windows":
        try:
            os.system("clear")
        except:
            pass
    else:
        try:
            os.system("cls")
        except:
            pass

if float(LatestVer) > Version:
    print("#"*30)
    print("       UPDATE AVAILABLE")
    print("#"*30)
    print("Current Version: " + str(Version))
    print("Latest Version: " + str(LatestVer))
    print("Download Link: "+ str(DownloadLink))
    input("\nPress any key to continue.\n")


def getDlUrl(TrackId):
    downloadUrl = None
    try:
        response = requests.get('https://api.soundcloud.com/i1/tracks/' + TrackId + '/streams?client_id=' + clientid)
        downloadUrl = json.loads(response.text)['http_mp3_128_url']
    except:
        if Debug:
            print("[Error] - GetDlUrl")
            input("Press any key to continue.\n")
        else:
            pass
    return downloadUrl


def saveFile(name,author,url,dest,filename,id3,Try=1):
    Failed = False
    maxTries = 3
    rawName = name
    rawAuthor = author
    rawUrl = url
    rawDest = dest
    rawFilename = filename
    rawID3 = id3
    keep = (' ','.','_','(',')','/','-')
    dest = "".join(c for c in dest if c.isalnum() or c in keep).rstrip()
    keep = (' ','.','_','(',')','-')
    filename = "".join(c for c in filename if c.isalnum() or c in keep).rstrip()
    if filename[0:-4] == "":
        filename = input("Invalid Parsed File Name, Please Choose A New Name.")
        filename = "".join(c for c in filename if c.isalnum() or c in keep).rstrip()
        if filename == "":
            saveFile(rawName,rawAuthor,rawUrl,rawDest,rawFilename,rawID3)
        else:
            filename = filename + ".mp3"
    dest = dest + filename
    if os.path.isfile(dest):
        print("Track: "+name+" Already Exists.")
        return
    try:
        print("Downloading: " + name + " as " + filename[0:-4])
        mp3file = urlopen(url)
        with open(dest,'wb') as output:
          output.write(mp3file.read())
        print("Finished Downloading: "+name)
    except:
        if Try < (maxTries + 1):
            print("Error Downloading: " + name + " || Waiting 10 Seconds And Trying Again." + " [" + str(Try) + "/" + str(maxTries) + "]")
            sleep(10)
            saveFile(rawName,rawAuthor,rawUrl,rawDest,rawFilename,rawID3,Try+1)
        else:
            Failed = True
            print("Failed To Download: " + name + "After " + maxTries + "Tries" + ", Skipping It.")
            pass
    if id3 == True and Failed == False:
        try:
            meta = EasyID3(dest)
        except mutagen.id3.ID3NoHeaderError:
            meta = mutagen.File(dest, easy=True)
            meta.add_tags()
        meta['title'] = rawName
        meta['artist'] = rawAuthor
        meta.save(dest, v1=2)
    return


def PlaylistURL():
    clearScreen()
    x = input("Enter A Playlist Url: ")
    clearScreen()
    useID3 = input("Do You Want To Use ID3 Tags? [Y/N]: ")
    clearScreen()
    if useID3[0].lower() == "y":
        useID3 = True
    elif useID3[0].lower() == "n":
        useID3 = False
    else:
        print("Unknown Option, Options: 'y', 'n', 'yes', 'no'")
        input("Press Any Key To Continue.\n")
        PlaylistURL()
    response = requests.get(x)
    soup = bs4.BeautifulSoup(response.text,"html.parser")
    metas = soup.select("meta")
    PlaylistID = (str(metas[30]).split("\"")[1])[23:len(str(metas[30]).split("\"")[1])]
    response = requests.get("http://api.soundcloud.com/playlists/"+PlaylistID+"?client_id="+clientid)
    PlaylistName = json.loads(response.text)['title']
    Author = (json.loads(response.text)['user']['username'])
    if not os.path.isdir("Downloads/"):
        os.mkdir("Downloads/")
    if not os.path.isdir("Downloads/"+PlaylistName):
        os.mkdir("Downloads/"+PlaylistName)
    for i in range(0,len(json.loads(response.text)['tracks'])):
        title = json.loads(response.text)['tracks'][i]['title']
        saveFile(title,Author,getDlUrl(str(json.loads(response.text)['tracks'][i]['id'])),"Downloads/" + PlaylistName + "/", title + ".mp3",useID3)
    input("Finished All Downloads, Press Any Key To Continue.\n")
    menu()


def TrackURL():
    clearScreen()
    x = input("Enter A Track Url: ")
    clearScreen()
    useID3 = input("Do You Want To Use ID3 Tags? [Y/N]: ")
    clearScreen()
    if useID3[0].lower() == "y":
        useID3 = True
    elif useID3[0].lower() == "n":
        useID3 = False
    else:
        print("Unknown Option, Options: 'y', 'n', 'yes', 'no'")
        input("Press Any Key To Continue.\n")
        PlaylistURL()
    clearScreen()
    print("Loading...")
    try:
        response = requests.get(x)
        text = response.text
        soup = bs4.BeautifulSoup(text,"html.parser")
        metas = soup.select("meta")
        TrackId = str(metas[30]).split("\"")[1][20:len(str(metas[30]).split("\"")[1])]
    except:
        if Debug:
            print("[Error] - TrackURL")
            input("Press any key to return.\n")
            TrackURL()
        else:
            TrackURL()
    links = soup.select('link')
    link = str(links[17])[12:61]
    Author = str(metas[63]).split("\"")[1]
    Title = str(metas[38]).split("\"")[1]
    clearScreen()
    print("TrackId: " + TrackId)
    print("Title: " + Title)
    print("Author: " + Author)
    if not os.path.isdir("Downloads/"):
        os.mkdir("Downloads/")
    saveFile(Title,Author,getDlUrl(TrackId),"Downloads/", Title + ".mp3",useID3)
    input("Finished All Downloads, Press Any Key To Continue.\n")
    menu()


def menu():
    clearScreen()
    print("Xequinox's Soundcloud Downloader")
    print("#"*35)
    print("[1] - Download Playlist From Url")
    print("[2] - Download Track From Url")
    print("#"*35)
    chc = input("#>")
    chc = chc[0]
    if chc == "1":
        PlaylistURL()
    elif chc == "2" :
        TrackURL()
    else:
        menu()
menu()
