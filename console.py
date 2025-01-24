import win32api
import win32con
import win32file
import csv
import os
from datetime import datetime

CSV_PATH = "data/drives.csv"

def SaveToCsv(data:dict,filePath:str):
    if not os.path.exists(filePath.split("/")[0]):
        os.makedirs(filePath.split("/")[0])
    with open(filePath, mode='a',newline='',encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if file.tell() == 0:
            writer.writerow(['Drive','Type','Owner','Serial','Timestamp'])
            
        for drive,info in data.items():
            writer.writerow([drive,info['type'],info['owner'],info['serial'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

def GetOwnerBySerial(serial: str, filePath) -> str:    
    if os.path.exist(filePath):
        with open(file=filePath, mode='r',encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reversed(list(reader)):
                if row['Serial'] == serial:
                    return row['Owner']
    return "None"
def GetConnectedDrives():
    drives = [i for i in win32api.GetLogicalDriveStrings().split("\\\x00") if i]
    rdrives = {}
    
    for drive in drives:
        if win32file.GetDriveType(drive) == win32con.DRIVE_REMOVABLE:
            rdrives[drive] = {
                'type': "DRIVE_REMOVABLE",
                'owner': GetOwnerBySerial(win32api.GetVolumeInformation(drive)[1]),
                'serial': win32api.GetVolumeInformation(drive)[1],
            }

    return rdrives

print(GetConnectedDrives())
SaveToCsv(GetConnectedDrives(),CSV_PATH)