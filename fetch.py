from __future__ import unicode_literals
from xml.sax.handler import property_interning_dict
import youtube_dl, signal, sys, getopt

# Helper text
HELP = """PLAY FETCH CLI
==============

Usage:
    main.py -i https://my-source.com
    main.py -i https://my-source.com -t 500
    main.py -i ./urls.txt -l
Options:
    -i  Input url
    -t  Timeout (in seconds)
    -l  Read from list (in which case, -i becomes the file to read from)
"""

# default timeout period
TIMEOUT = 120

def download_file(url, timeout):
    signal.signal(signal.SIGALRM, throw_timeout)
    signal.alarm(timeout)

    print("Attempting to download: ", url)
    print("With timeout: ", timeout)

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print("DOWNLOADED", url)
    except TimeoutError:
        sys.exit("ERROR: Script timeout - increase the timeout period")
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)

def throw_timeout(s, f):
    raise TimeoutError

# check for mandatory args (url)
argv = sys.argv[1:]
if len(argv) < 2 or argv[1] == "":
    print("ERROR: No input value specified\n")
    print(HELP)
    sys.exit()

opts, args = getopt.getopt(argv, "i:t:l")
fopts = {
    "input": None,
    "timeout": TIMEOUT,
    "list": False
}

for opt, arg in opts:
    if opt == "-i":
        fopts["input"] = arg
    elif opt == "-t":
        fopts["timeout"] = arg
    elif opt == "-l":
        fopts["list"] = not fopts["list"]

if fopts["list"] == False:
    # download single file
    download_file(fopts["input"], fopts["timeout"])
else:
    # read from list
    try:
        file = open(fopts["input"], "r")
        lines = file.readlines()
        for line in lines:
            download_file(line, fopts["timeout"])
    except IOError:
        print("ERROR: Specified file could not be opened")
        sys.exit()