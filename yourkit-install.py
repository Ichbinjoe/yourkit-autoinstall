import os
import re
import shutil

import requests
import sys

download_regexp = re.compile("\/download\/yjp-2016.02-b[0-9]+-linux.tar.bz2")

def get_download_url():
    scrape = requests.get('https://www.yourkit.com/java/profiler/download')

    if scrape.status_code != 200:
        return None

    responseString = str(scrape.content)
    match = download_regexp.search(responseString)
    if match is None:
        return None
    return "https://yourkit.com" + match.string[match.regs[0][0]:match.regs[0][1]]


def downloadToFile(url, file):
    download = requests.get(url)

    if download.status_code != 200:
        return None

    with open(file, 'wb') as f:
        f.write(download.content)

is_64bits = sys.maxsize > 2**32
if not sys.platform == "linux":
    print("You are not running a linux system! This script only supports linux systems")
    exit(-2)

print("Finding latest YourKit distribution")
latest = get_download_url()
if latest is None:
    print("Could not determine latest YourKit distribution!")
    exit(-1)

latestFilename = latest[29:]

latestTrimmedFilename = latestFilename[:11]

print("Latest version: "+latestFilename)

if os.path.isfile(latestFilename):
    print("Latest version already downloaded, skipping download.")
else:
    print("Downloading latest YourKit... (this may take awhile)")
    downloadToFile(latest, latestFilename)
    print("Finished downloading latest YourKit.")

if not os.path.isdir(latestTrimmedFilename):
    print("Un-tarring YourKit to "+latestTrimmedFilename)
    shutil.unpack_archive(latestFilename, ".")
    print("Finished un-tarring")

if is_64bits:
    print("Detected 64bit Linux OS")
    subdirectory = latestTrimmedFilename+"/bin/linux-x86-64/libyjpagent.so"
else:
    print("Detected 32bit Linux OS")
    subdirectory = latestTrimmedFilename+"/bin/linux-x86-32/libyjpagent.so"

subdirectory = os.getcwd() +"/"+ subdirectory
print("YJPAgent path: "+subdirectory)

print("'-agentpath:"+subdirectory+"' must be added to the server startup flags!")

if len(sys.argv) < 2:
    print("No configuration file passed, not automatically injecting.")
else:
    if not os.path.isfile(sys.argv[1]):
        print(sys.argv[1]+" is not a file.")
        exit(-3)
    else:
        splitted = sys.argv[1].split('.') #Try to strip away the file ending
        if len(splitted) > 1:
            newscriptname = ""
            for part in splitted[:len(splitted)-1]:
                newscriptname += part
            newscriptname += "-with-yourkit."
            newscriptname += splitted[len(splitted)-1]
        else:
            newscriptname = sys.argv[1]

        with open(sys.argv[1],"r") as f:
            oldScriptFile = f.read()
        injected = ""
        for line in oldScriptFile.split("\n"):

            if line.strip(" \t").startswith("java"):
                splitIndex = line.find("java") + 4
                line = line[:splitIndex]+" -agentpath:"+subdirectory+line[splitIndex:]
            injected += line+'\n'

        with open(newscriptname,"w") as f:
            f.write(injected)

        print("Injected new configuration file to "+newscriptname)