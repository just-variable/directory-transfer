import socket
import json
import os
from rich.progress import Progress, DownloadColumn, SpinnerColumn, BarColumn, TransferSpeedColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn

BUFFER_SIZE = 2*1024*1024

def fixName(str):
    if(len(str) > 33):
        str = str[:30] + "..." 
    return str + " "*(36-len(str))

def getDir(dirDict):
    for itemName in dirDict.keys():
        if(isinstance(dirDict[itemName], list)):
            try:
                os.makedirs(dirDict[itemName][3])
            except:
                None

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), BarColumn(), TimeRemainingColumn(),  TransferSpeedColumn(), DownloadColumn(True)) as progress:
                task1 = progress.add_task("[cyan]" + fixName(itemName), total=dirDict[itemName][1])
                file = open(dirDict[itemName][3] + itemName, "wb")
                done = False

                while not done:
                    data_buffer = client.recv(BUFFER_SIZE)
                    if(b"<END>" in data_buffer):
                        progress.update(task1, advance=len(data_buffer)-5)
                        client.send(("fileTransfer:" + itemName).encode())
                        data_buffer = data_buffer.replace(b"<END>", b"")
                        file.write(data_buffer)
                        done = True
                    else:
                        progress.update(task1, advance=len(data_buffer))
                        file.write(data_buffer)
                file.close()
        else:
            getDir(dirDict[itemName])
            
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(("0.0.0.0", 5000))
s.listen(5)
print("[+] Listening...")
client, addr = s.accept()
print('[+] Connected to: ', addr)

done = False
dirDictString = ""
while not done:
    data = client.recv(BUFFER_SIZE).decode()
    if("<END>" in data):
        print("[+] Received directory data, receiving files...\n")
        done = True
        dirDictString += data[:-5]
    else:
        dirDictString += data

client.send(b"dirDictTransfer")
dirDict = json.loads(dirDictString)

getDir(dirDict)
        
print("\n[+] Done, closing connection...")
client.close()
input("[-] press enter...")
