import pymongo
import time
import os

client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")
db = client.data
stats = db['stats']
cveDB = db['cve']

while True:
    time.sleep(300)
    print("Updating stats...", end='')
    numberOfCVE = str(cveDB.count_documents({}))
    numberOfCVE_CRITICAL = str(cveDB.count_documents({'baseScore':  {'$gte': 9.0}}))
    numberOfCVE_HIGH = str(cveDB.count_documents({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}))
    numberOfCVE_MEDIUM = str(cveDB.count_documents({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}))
    numberOfCVE_LOW = str(cveDB.count_documents({'baseScore': {'$gte': 0.1, '$lte': 3.9}}))
    numberOfCVE_NoScore = str(cveDB.count_documents({'baseScore':-1}))
    mydict = {"_id":"stats", "numberOfCVE":numberOfCVE, "numberOfCVE_CRITICAL":numberOfCVE_CRITICAL, "numberOfCVE_HIGH":numberOfCVE_HIGH, "numberOfCVE_MEDIUM":numberOfCVE_MEDIUM, "numberOfCVE_LOW":numberOfCVE_LOW, "numberOfCVE_NoScore":numberOfCVE_NoScore}
    try:
        stats.insert_one(mydict)
    except:
        cveDB.update_one({"_id":"stats"}, {"$set": {"numberOfCVE":numberOfCVE, "numberOfCVE_CRITICAL":numberOfCVE_CRITICAL, "numberOfCVE_HIGH":numberOfCVE_HIGH, "numberOfCVE_MEDIUM":numberOfCVE_MEDIUM, "numberOfCVE_LOW":numberOfCVE_LOW, "numberOfCVE_NoScore":numberOfCVE_NoScore}})

    print("Done")



