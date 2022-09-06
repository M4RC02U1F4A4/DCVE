from flask import Flask, render_template, redirect, request
from flask_caching import Cache
import os
import pymongo
from datetime import date, datetime, timedelta

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}

app = Flask(__name__)

app.config.from_mapping(config)
cache = Cache(app)

@app.route('/')
def home():
    return redirect("/last/published", 301)

@app.route('/reset_cache')
def rc():
    cache.clear()
    return "OK", 200

@app.route('/last/published')
@cache.cached()
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
@cache.cached()
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
@cache.cached()
def todayModified():
    mydict = stats.find_one({"_id":"stats"})
    todayDate = datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    todayModifiedCVE = cveDB.find({"lastModifiedDate":{"$gte":todayDate}}).sort('lastModifiedDate', -1)
    todayModifiedCVE_number = cveDB.count_documents({"lastModifiedDate":{"$gte":todayDate}})
    return render_template(
        'todayModified.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        todayModifiedCVE = list(todayModifiedCVE),
        todayModifiedCVE_number = todayModifiedCVE_number
    )

@app.route('/today/published')
@cache.cached()
def todayPublished():
    mydict = stats.find_one({"_id":"stats"})
    todayDate = datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    todayPublishedCVE = cveDB.find({"publishedDate":{"$gte":todayDate}}).sort('publishedDate', -1)
    todayPublishedCVE_number = cveDB.count_documents({"publishedDate":{"$gte":todayDate}})
    return render_template(
        'todayPublished.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        todayPublishedCVE = list(todayPublishedCVE),
        todayPublishedCVE_number = todayPublishedCVE_number
    )

@app.route('/last/72h')
# @cache.cached()
def last72h():
    mydict = stats.find_one({"_id":"stats"})
    todayDate = datetime.strptime((date.today() - timedelta(3)).strftime("%Y-%m-%d"), "%Y-%m-%d")
    pm72h = cveDB.find({"$and":[{"$or":[ {"publishedDate":{"$gte":todayDate}}, {"lastModifiedDate":{"$gte":todayDate}}]}, {"baseScore":{"$gte":0.0}}]}).sort('lastModifiedDate', -1)
    pm72h_number = cveDB.count_documents({"$and":[{"$or":[ {"publishedDate":{"$gte":todayDate}}, {"lastModifiedDate":{"$gte":todayDate}}]}, {"baseScore":{"$gte":0.0}}]})
    return render_template(
        'pm72h.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        pm72h = list(pm72h),
        pm72h_number = pm72h_number
    )

@app.route('/last/kev')
@cache.cached()
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

@app.route('/today/kev')
@cache.cached()
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

@app.route('/patchtuesday')
@cache.cached()
def patchTuesday():
    mydict = stats.find_one({"_id":"stats"})
    patch = pTuesday.find({})
    patch_number = pTuesday.count_documents({})
    return render_template(
        'patchTuesday.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        patch = list(patch),
        patch_number = patch_number
    )

@app.route('/fasttuesday')
@cache.cached()
def fastTuesday():
    mydict = stats.find_one({"_id":"stats"})
    patch = pTuesday.find({'score':  {'$gte': 7.0}}).sort('score', -1)
    patch_number = pTuesday.count_documents({'score':  {'$gte': 7.0}})
    return render_template(
        'patchTuesday.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        patch = list(patch),
        patch_number = patch_number
    )

@app.route('/check_cve')
def checkCVE():
    mydict = stats.find_one({"_id":"stats"})
    checkcve = cveDB.find({"$and":[{'updated': 1}, {'baseScore':  {'$gte': 0}}]}).sort('lastModifiedDate', -1)
    checkcve_number = cveDB.count_documents({"$and":[{'updated': 1}, {'baseScore':  {'$gte': 0}}]})
    return render_template(
        'checkCVE.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        checkcve = list(checkcve),
        checkcve_number = checkcve_number
    )

@app.route('/check_cve/<cveReaded>/<id>')
def read_checkCVE(cveReaded="", id=0):
    if not cveReaded == "":
        cveDB.update_one({"_id":f"{cveReaded}"}, {"$set": {"updated": 0}})
        return redirect(f"/check_cve#{id}")

@app.route('/check_cve/ALL')
def read_checkCVE_ALL():
    checkcve = cveDB.find({"$and":[{'updated': 1}, {'baseScore':  {'$gte': 0}}]})
    for i in checkcve:
        cveDB.update_one({"_id":f"{i['_id']}"}, {"$set": {"updated": 0}})
    return redirect("/check_cve")

@app.route('/check_cve/undo/<cveReaded>')
def read_checkCVE_undo(cveReaded=""):
    if not cveReaded == "":
        cveDB.update_one({"_id":f"{cveReaded}"}, {"$set": {"updated": 1}})
        return redirect("/last/72h")
        

if __name__ == '__main__':
    client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")
    
    db = client.data
    stats = db['stats']
    cveDB = db['cve']
    kev = db['kev']
    pTuesday = db['pTuesday']

    app.run(debug=False, port=5000, host='0.0.0.0')