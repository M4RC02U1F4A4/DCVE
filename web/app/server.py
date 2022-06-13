from flask import Flask, render_template, redirect
import os
import pymongo
from datetime import date, datetime

app = Flask(__name__)

@app.route('/')
def home():
    return redirect("/last/published", 301)

@app.route('/last/published')
def lastPublished():
    mydict = stats.find_one({"_id":"stats"})
    recent_CRITICAL = cveDB.find(({'baseScore':  {'$gte': 9.0}})).sort('publishedDate', -1).limit(10)
    recent_HIGH = cveDB.find({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}).sort('publishedDate', -1).limit(10)
    recent_MEDIUM = cveDB.find({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}).sort('publishedDate', -1).limit(10)
    recent_LOW = cveDB.find({'baseScore': {'$gte': 0.1, '$lte': 3.9}}).sort('publishedDate', -1).limit(10)
    return render_template(
        'lastPublished.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        recent_CRITICAL = recent_CRITICAL,
        recent_HIGH = recent_HIGH,
        recent_MEDIUM = recent_MEDIUM,
        recent_LOW = recent_LOW,
    )

@app.route('/last/modified')
def lastModified():
    mydict = stats.find_one({"_id":"stats"})
    recent_CRITICAL = cveDB.find(({'baseScore':  {'$gte': 9.0}})).sort('lastModifiedDate', -1).limit(10)
    recent_HIGH = cveDB.find({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}).sort('lastModifiedDate', -1).limit(10)
    recent_MEDIUM = cveDB.find({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}).sort('lastModifiedDate', -1).limit(10)
    recent_LOW = cveDB.find({'baseScore': {'$gte': 0.1, '$lte': 3.9}}).sort('lastModifiedDate', -1).limit(10)
    return render_template(
        'lastModified.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        recent_CRITICAL = recent_CRITICAL,
        recent_HIGH = recent_HIGH,
        recent_MEDIUM = recent_MEDIUM,
        recent_LOW = recent_LOW,
    )

@app.route('/today/modified')
def todayModified():
    mydict = stats.find_one({"_id":"stats"})
    todayDate = datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    todayModifiedCVE = cveDB.find({"lastModifiedDate":{"$gte":todayDate}})
    return render_template(
        'todayModified.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        todayModifiedCVE = list(todayModifiedCVE)
    )

@app.route('/today/published')
def todayPublished():
    mydict = stats.find_one({"_id":"stats"})
    todayDate = datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    todayPublishedCVE = cveDB.find({"publishedDate":{"$gte":todayDate}})
    return render_template(
        'todayPublished.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        todayPublishedCVE = list(todayPublishedCVE)
    )

@app.route('/today/kev')
def todayKevF():
    mydict = stats.find_one({"_id":"stats"})
    todayDate = datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    todayKEV_res = kev.find({"dateAdded":{"$gte":todayDate}})
    return render_template(
        'todayKEV.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        todayKEV_res = list(todayKEV_res)
    )

@app.route('/last/kev')
def lastKevF():
    mydict = stats.find_one({"_id":"stats"})
    lastKEV_res = kev.find().sort('dateAdded', -1).limit(10)
    return render_template(
        'lastKEV.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        lastKEV_res = list(lastKEV_res)
    )

if __name__ == '__main__':
    client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")
    
    db = client.data
    stats = db['stats']
    cveDB = db['cve']
    kev = db['kev']

    app.run(debug=True, port=5000, host='0.0.0.0')