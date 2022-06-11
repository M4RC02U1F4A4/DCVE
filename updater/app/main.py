from datetime import date
from email.mime import base
import time
import urllib.request
import io
import zipfile
import json
import pymongo
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import os

def loadCVE(i): 
    id = i['cve']['CVE_data_meta']['ID']
    publishedDate = datetime.datetime.strptime(i['publishedDate'], "%Y-%m-%dT%H:%MZ")
    baseScore = -1
    vectorString = ""
    description = ""

    if "impact" in i:
        if "baseMetricV3" in i['impact']:
            if "cvssV3" in i['impact']['baseMetricV3']:
                baseScore = float(i['impact']['baseMetricV3']['cvssV3']['baseScore'])
                vectorString = i['impact']['baseMetricV3']['cvssV3']['vectorString']

    if "description" in i['cve']:
        description = i['cve']['description']['description_data'][0]['value']

    return({"_id":f"{id}", "baseScore":baseScore, "vectorString":f"{vectorString}", "description":f"{description}", "publishedDate":publishedDate})

def updateAll():
    for year in range(2002, date.today().year + 1):
        print(f"Downloading {year} json...", end='')
        access_url = urllib.request.urlopen(f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.zip")
        z = zipfile.ZipFile(io.BytesIO(access_url.read()))
        data = json.loads(z.read(z.infolist()[0]).decode())
        print("Importing into the DB...", end='')
        for i in data['CVE_Items']:
            mydict = loadCVE(i)
            try:
                cveDB.insert_one(mydict)
            except:
                cveDB.update_one({"_id":f"{mydict['_id']}"}, {"$set": {"baseScore":mydict['baseScore'], "vectorString":f"{mydict['vectorString']}", "description":f"{mydict['description']}", "publishedDate":f"{mydict['publishedDate']}"}})
        print("Done")

def updateModiefied():
    print(f"Downloading modified json...", end='')
    access_url = urllib.request.urlopen(f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.json.zip")
    z = zipfile.ZipFile(io.BytesIO(access_url.read()))
    data = json.loads(z.read(z.infolist()[0]).decode())
    print("Importing into the DB...", end='')
    for i in data['CVE_Items']:
        mydict = loadCVE(i)
        try:
            cveDB.insert_one(mydict)
        except:
            cveDB.update_one({"_id":f"{mydict['_id']}"}, {"$set": {"baseScore":mydict['baseScore'], "vectorString":f"{mydict['vectorString']}", "description":f"{mydict['description']}", "publishedDate":f"{mydict['publishedDate']}"}})
    print("Done")

# Wait for mongoDB
time.sleep(2)

client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")
db = client.data
cveDB = db['cve']
cveDB.create_index('baseScore')
cveDB.create_index('publishedDate')

updateModiefied()

scheduler = BlockingScheduler()
scheduler.add_job(updateAll, 'interval', hours=24)
scheduler.add_job(updateModiefied, 'interval', hours=2)
scheduler.start()