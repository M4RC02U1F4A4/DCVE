from flask import Flask, render_template
import os
import pymongo

app = Flask(__name__)



@app.route('/')
def home():
    mydict = stats.find_one({"_id":"stats"})
    recent_CRITICAL = cveDB.find(({'baseScore':  {'$gte': 9.0}})).sort('publishedDate', -1).limit(10)
    recent_HIGH = cveDB.find({'baseScore':  {'$gte': 7.0, '$lte': 8.9}}).sort('publishedDate', -1).limit(10)
    recent_MEDIUM = cveDB.find({'baseScore':  {'$gte': 4.0, '$lte': 6.9}}).sort('publishedDate', -1).limit(10)
    recent_LOW = cveDB.find({'baseScore': {'$gte': 0.1, '$lte': 3.9}}).sort('publishedDate', -1).limit(10)
    return render_template(
        'home.html',
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

if __name__ == '__main__':
    client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}")
    db = client.data
    stats = db['stats']
    cveDB = db['cve']
    app.run(debug=True, port=5000, host='0.0.0.0')