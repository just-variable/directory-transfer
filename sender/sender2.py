import json
import os
import socket
from rich.progress import Progress

BUFFER_SIZE = 2*1024*1024

s = socket.socket()
totalFilesSize = {'value': 0}

def fixName(str):
    if(len(str) > 33):
        str = str[:30] + "..."
    return str + " "*(36-len(str))

def readDir(relPath):
    dirDict = {}
    filesList = os.scandir(relPath)

    for itemObj in filesList:
        itemName = itemObj.name
        if (itemName == os.path.basename(__file__)):
            continue
        if (itemObj.is_file()):
            fileDigest = ""
            size = os.stat(relPath + itemName).st_size
            totalFilesSize['value'] += size
            thisFile = [itemName, size, fileDigest, relPath]
            dirDict[thisFile[0]] = thisFile
        else:
            dirDict[itemName] = readDir(relPath + itemName + "/")
    return dirDict

def sendDir(dirDict, progress):

    for itemName in dirDict.keys():
        if (isinstance(dirDict[itemName], list)):
            filee = open(dirDict[itemName][3] + itemName, "rb")

            while True:
                data = filee.read(BUFFER_SIZE*50)
                s.sendall(data)
                progress.update(task1, description=("[red]"+fixName(itemName)), advance=BUFFER_SIZE)
                if not data:
                    break

            s.send(b"<END>")
            while (s.recv(BUFFER_SIZE).decode() != ("fileTransfer:" + itemName)):
                print("[+] Waiting for receiver...")
        else:
            sendDir(dirDict[itemName], progress)

print("[+] Reading files and subdirectories...")
completeFiles = readDir("./")

receiverIP = input("[-] Enter IP of receiver or leave blank for localhost: ")
if (receiverIP == ""):
    receiverIP = "localhost"
s.connect((receiverIP, 5000))
print("[+] Connected.")

completeFilesBytes = json.dumps(completeFiles)
completeFiles = json.loads(completeFilesBytes)

s.send(completeFilesBytes.encode())
s.send(b"<END>")

recv = s.recv(BUFFER_SIZE).decode()
if recv == "dirDictTransfer":
    print("[+] Directory data received by peer. Starting to send...\n")
    with Progress() as progress:
        task1 = progress.add_task("[red]", total=totalFilesSize['value'])
        sendDir(completeFiles, progress)
    
        
print("\n[+] Done, closing connection...")
s.close()
print("[+] Connection closed.")
input("[-] press enter...")