from datetime import date
import time
import urllib.request
import io
import zipfile
import json
import pymongo
import datetime
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
    publishedDate = datetime.datetime.strptime(i['publishedDate'], "%Y-%m-%dT%H:%MZ")
    lastModifiedDate = datetime.datetime.strptime(i['lastModifiedDate'], "%Y-%m-%dT%H:%MZ")
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

def createCache():
    print("Creating cache...")
    publishedDateDB.delete_many({})
    recent_CRITICAL = cveDB.find(({'baseScore':  {'$gte': 9.0}})).sort('publishedDate', -1).limit(10)
    publishedDateDB.insert_many(recent_CRITICAL)
    recent_HIGH = cveDB.find({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}).sort('publishedDate', -1).limit(10)
    publishedDateDB.insert_many(recent_HIGH)
    recent_MEDIUM = cveDB.find({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}).sort('publishedDate', -1).limit(10)
    publishedDateDB.insert_many(recent_MEDIUM)
    recent_LOW = cveDB.find({'baseScore': {'$gte': 0.1, '$lte': 3.9}}).sort('publishedDate', -1).limit(10)
    publishedDateDB.insert_many(recent_LOW)

    lastModifiedDateDB.delete_many({})
    recent_CRITICAL = cveDB.find(({'baseScore':  {'$gte': 9.0}})).sort('lastModifiedDate', -1).limit(10)
    lastModifiedDateDB.insert_many(recent_CRITICAL)
    recent_HIGH = cveDB.find({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}).sort('lastModifiedDate', -1).limit(10)
    lastModifiedDateDB.insert_many(recent_HIGH)
    recent_MEDIUM = cveDB.find({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}).sort('lastModifiedDate', -1).limit(10)
    lastModifiedDateDB.insert_many(recent_MEDIUM)
    recent_LOW = cveDB.find({'baseScore': {'$gte': 0.1, '$lte': 3.9}}).sort('lastModifiedDate', -1).limit(10)
    lastModifiedDateDB.insert_many(recent_LOW)

    todayDate = datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")

    todayPublishedDateDB.delete_many({})
    todayPublished_CVE = cveDB.find({"$and":[{"publishedDate":{"$gte":todayDate}},{"baseScore": {'$gte': 0.1}}]})
    todayPublished_CVE = list(todayPublished_CVE)
    if todayPublished_CVE:
        todayPublishedDateDB.insert_many(todayPublished_CVE)

    todayLastModifiedDateDB.delete_many({})
    todayModified_CVE = cveDB.find({"$and":[{"lastModifiedDate":{"$gte":todayDate}},{"baseScore": {'$gte': 0.1}}]})
    todayModified_CVE = list(todayModified_CVE)
    if todayModified_CVE:
        todayLastModifiedDateDB.insert_many(todayModified_CVE)

    lastKev.delete_many({})
    recentKEV = kev.find().sort('dateAdded', -1).limit(10)
    lastKev.insert_many(recentKEV)

    todayKev.delete_many({})
    todayKEV = kev.find({"dateAdded":{"$gte":todayDate}})
    todayKEV = list(todayKEV)
    if todayKEV:
        todayKev.insert_many(todayKEV)
    print("Cache created")
    



def metaCalc():
    print("Updating metadata...")
    statsCalc()
    createCache()
    

# Wait for mongoDB
time.sleep(2)

client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")

db = client.data
cveDB = db['cve']
stats = db['stats']
meta = db['meta']
kev = db['kev']

db2 = client.cache
publishedDateDB = db2['publishedDateDB']
lastModifiedDateDB = db2['lastModifiedDateDB']
todayPublishedDateDB = db2['todayPublishedDateDB']
todayLastModifiedDateDB = db2['todayLastModifiedDateDB']
lastKev = db2['lastKev']
todayKev = db2['todayKev']

cveDB.create_index('baseScore')
cveDB.create_index('publishedDate')
cveDB.create_index('lastModifiedDate')
kev.create_index('dateAdded')
publishedDateDB.create_index('publishedDate')
lastModifiedDateDB.create_index('lastModifiedDate')
todayPublishedDateDB.create_index('publishedDate')
todayLastModifiedDateDB.create_index('lastModifiedDate')
lastKev.create_index('dateAdded')
todayKev.create_index('dateAdded')

# updateModiefied()
# updateAll()
updateKev()
metaCalc()
scheduler = BlockingScheduler()
scheduler.add_job(updateAll, 'interval', hours=1)
scheduler.add_job(updateModiefied, 'interval', hours=1)
scheduler.add_job(metaCalc, 'interval', hours=1)
scheduler.add_job(updateKev, 'interval', hours=1)
scheduler.start()