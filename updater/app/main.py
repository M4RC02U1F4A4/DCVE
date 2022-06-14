from datetime import date
import time
import urllib.request
import io
import zipfile
import json
import pymongo
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import requests
from datetime import date, datetime


def shacheck(link, id):
    try:
        x = requests.get(f'{link}')
        sha = x.text.strip().split("\n")[4].replace("sha256:", "")
        print(sha)
    except:
        print("Errore requests!!")
        return False
    mydict = meta.find_one({"_id":f"{id}"})
    if mydict:
        if mydict['sha256'] == sha:
            return False
        else:
            meta.update_one({"_id":f"{id}"}, {"$set": {"sha256":f"{sha}"}})
            return True
    else:
        meta.insert_one({"_id":f"{id}", "sha256":f"{sha}"})
        return True


def statsCalc():
    print("Updating stats...")
    numberOfCVE = cveDB.count_documents({})
    print(f"N -> {numberOfCVE}")
    numberOfCVE_CRITICAL = cveDB.count_documents({'baseScore':  {'$gte': 9.0}})
    print(f"CRITICAL -> {numberOfCVE_CRITICAL}")
    numberOfCVE_HIGH = cveDB.count_documents({'baseScore':  {'$gte': 7.0, '$lte': 8.9}})
    print(f"HIGH -> {numberOfCVE_HIGH}")
    numberOfCVE_MEDIUM = cveDB.count_documents({'baseScore':  {'$gte': 4.0, '$lte': 6.9}})
    print(f"MEDIUM -> {numberOfCVE_MEDIUM}")
    numberOfCVE_LOW = cveDB.count_documents({'baseScore': {'$gte': 0.1, '$lte': 3.9}})
    print(f"LOW -> {numberOfCVE_LOW}")
    numberOfCVE_NoScore = cveDB.count_documents({'baseScore':-1})
    mydict = {"_id":"stats", "numberOfCVE":numberOfCVE, "numberOfCVE_CRITICAL":numberOfCVE_CRITICAL, "numberOfCVE_HIGH":numberOfCVE_HIGH, "numberOfCVE_MEDIUM":numberOfCVE_MEDIUM, "numberOfCVE_LOW":numberOfCVE_LOW, "numberOfCVE_NoScore":numberOfCVE_NoScore}
    try:
        stats.insert_one(mydict)
    except:
        stats.update_one({"_id":"stats"}, {"$set": {"numberOfCVE":numberOfCVE, "numberOfCVE_CRITICAL":numberOfCVE_CRITICAL, "numberOfCVE_HIGH":numberOfCVE_HIGH, "numberOfCVE_MEDIUM":numberOfCVE_MEDIUM, "numberOfCVE_LOW":numberOfCVE_LOW, "numberOfCVE_NoScore":numberOfCVE_NoScore}})


def loadCVE(i): 
    id = i['cve']['CVE_data_meta']['ID']
    publishedDate = datetime.strptime(i['publishedDate'], "%Y-%m-%dT%H:%MZ")
    lastModifiedDate = datetime.strptime(i['lastModifiedDate'], "%Y-%m-%dT%H:%MZ")
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
    return({"_id":f"{id}", "baseScore":baseScore, "vectorString":f"{vectorString}", "description":f"{description}", "publishedDate":publishedDate, "lastModifiedDate":lastModifiedDate})


def insertCVE(mydict):
    try:
        cveDB.insert_one(mydict)
    except:
        cveDB.update_one({"_id":f"{mydict['_id']}"}, {"$set": {"baseScore":mydict['baseScore'], "vectorString":f"{mydict['vectorString']}", "description":f"{mydict['description']}", "publishedDate":mydict['publishedDate'], "lastModifiedDate":mydict['lastModifiedDate']}})


def updateAll():
    print("Starting updateAll")
    for year in range(2002, date.today().year + 1):
        if shacheck(f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.meta", str(year)):
            print(f"Downloading {year} json...")
            access_url = urllib.request.urlopen(f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.zip")
            z = zipfile.ZipFile(io.BytesIO(access_url.read()))
            data = json.loads(z.read(z.infolist()[0]).decode())
            print("Importing into the DB...")
            for i in data['CVE_Items']:
                insertCVE(loadCVE(i))
    print("updateAll ended")

def updateModiefied():
    print("Starting updateModified")
    if shacheck('https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.meta', "modified"):
        print(f"Downloading modified json...")
        access_url = urllib.request.urlopen(f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.json.zip")
        z = zipfile.ZipFile(io.BytesIO(access_url.read()))
        data = json.loads(z.read(z.infolist()[0]).decode())
        print("Importing into the DB...")
        for i in data['CVE_Items']:
            insertCVE(loadCVE(i))
    print("updateModified ended")

def updateKev():
    print("Updating KEV")
    r = requests.get('https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json',)
    jsonResponseCisa = r.json()
    for i in jsonResponseCisa['vulnerabilities']:
        score = cveDB.find_one({"_id":f"{i['cveID']}"})
        if score:
            score = score['baseScore']
        else:
            score = -1
        mydict = {"_id":f"{i['cveID']}", "vendorProject":f"{i['vendorProject']}", "product":f"{i['product']}", "dateAdded":datetime.strptime(f"{i['dateAdded']}", "%Y-%m-%d"), "shortDescription":f"{i['shortDescription']}", "requiredAction":f"{i['requiredAction']}", "score":score}
        try:
            kev.insert_one(mydict)
        except:
            kev.update_one({"_id":f"{i['cveID']}"}, {"$set": {"vendorProject":f"{i['vendorProject']}", "product":f"{i['product']}", "dateAdded":datetime.strptime(f"{i['dateAdded']}", "%Y-%m-%d"), "shortDescription":f"{i['shortDescription']}", "requiredAction":f"{i['requiredAction']}", "score":score}})

    print("KEV ended")
    
def patchTuesday():
    month = f"{datetime.now().year}-{datetime.now().strftime('%b')}"
    r = requests.get(f"https://api.msrc.microsoft.com/cvrf/{month}", headers={"Accept":"application/json"})
    jsonResponseMicrosoft = r.json()

    pTuesday.delete_many({})

    for i in jsonResponseMicrosoft['Vulnerability']:
        if len(i['CVSSScoreSets']) > 0:
            mydict = {"_id":f"{i['CVE']}", "score":i['CVSSScoreSets'][0]['BaseScore'], "vector":f"{i['CVSSScoreSets'][0]['Vector']}", "date":datetime.strptime(f"{i['RevisionHistory'][0]['Date']}", "%Y-%m-%dT%H:%M:%S"), "description":f"{i['Title']['Value']}"}
        else:
            mydict = {"_id":f"{i['CVE']}", "score":-1, "date":datetime.strptime(f"{i['RevisionHistory'][0]['Date']}", "%Y-%m-%dT%H:%M:%S"), "description":f"{i['Title']['Value']}"}
        pTuesday.insert_one(mydict)

        
        


# Wait for mongoDB
time.sleep(2)

client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")

db = client.data
cveDB = db['cve']
stats = db['stats']
meta = db['meta']
kev = db['kev']
pTuesday = db['pTuesday']


cveDB.create_index('baseScore')
cveDB.create_index('publishedDate')
cveDB.create_index('lastModifiedDate')
kev.create_index('dateAdded')
pTuesday.create_index('score')

# updateModiefied()
# updateAll()
# updateKev()
# statsCalc()
patchTuesday()

scheduler = BlockingScheduler()
scheduler.add_job(updateAll, 'interval', hours=1)
scheduler.add_job(updateModiefied, 'interval', hours=1)
scheduler.add_job(statsCalc, 'interval', hours=1)
scheduler.add_job(updateKev, 'interval', hours=1)
scheduler.add_job(patchTuesday, 'interval', hours=24)
scheduler.start()