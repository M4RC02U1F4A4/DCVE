from flask import Flask, render_template, redirect
import os
import pymongo

app = Flask(__name__)

@app.route('/')
def home():
    return redirect("/top/published", 301)

@app.route('/top/published')
def lastPublished():
    mydict = stats.find_one({"_id":"stats"})
    recent_CRITICAL = publishedDateDB.find(({'baseScore':  {'$gte': 9.0}})).sort('publishedDate', -1).limit(10)
    recent_HIGH = publishedDateDB.find({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}).sort('publishedDate', -1).limit(10)
    recent_MEDIUM = publishedDateDB.find({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}).sort('publishedDate', -1).limit(10)
    recent_LOW = publishedDateDB.find({'baseScore': {'$gte': 0.1, '$lte': 3.9}}).sort('publishedDate', -1).limit(10)
    return render_template(
        'topPublished.html',
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

@app.route('/top/modified')
def lastModified():
    mydict = stats.find_one({"_id":"stats"})
    recent_CRITICAL = lastModifiedDateDB.find(({'baseScore':  {'$gte': 9.0}})).sort('lastModifiedDate', -1).limit(10)
    recent_HIGH = lastModifiedDateDB.find({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}).sort('lastModifiedDate', -1).limit(10)
    recent_MEDIUM = lastModifiedDateDB.find({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}).sort('lastModifiedDate', -1).limit(10)
    recent_LOW = lastModifiedDateDB.find({'baseScore': {'$gte': 0.1, '$lte': 3.9}}).sort('lastModifiedDate', -1).limit(10)
    return render_template(
        'topModified.html',
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
    todayModifiedCVE = todayLastModifiedDateDB.find({}).sort('lastModifiedDate', -1)
    return render_template(
        'todayModified.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        todayModifiedCVE = todayModifiedCVE
    )

@app.route('/today/published')
def todayPublished():
    mydict = stats.find_one({"_id":"stats"})
    todayPublishedCVE = todayLastModifiedDateDB.find({}).sort('publishedDate', -1)
    return render_template(
        'todayPublished.html',
        numberOfCVE = mydict['numberOfCVE'],
        numberOfCVE_CRITICAL = mydict['numberOfCVE_CRITICAL'],
        numberOfCVE_HIGH = mydict['numberOfCVE_HIGH'],
        numberOfCVE_MEDIUM = mydict['numberOfCVE_MEDIUM'],
        numberOfCVE_LOW = mydict['numberOfCVE_LOW'],
        numberOfCVE_NoScore = mydict['numberOfCVE_NoScore'],
        todayPublishedCVE = todayPublishedCVE
    )


if __name__ == '__main__':
    client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")
    db = client.data
    stats = db['stats']
    db2 = client.cache
    publishedDateDB = db2['publishedDateDB']
    lastModifiedDateDB = db2['lastModifiedDateDB']
    todayPublishedDateDB = db2['todayPublishedDateDB']
    todayLastModifiedDateDB = db2['todayLastModifiedDateDB']
    app.run(debug=True, port=5000, host='0.0.0.0')