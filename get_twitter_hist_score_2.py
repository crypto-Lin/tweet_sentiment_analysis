import pymongo
from pymongo import MongoClient
import numpy as np
import urllib

DB_NAME = "longhash"
SCORE_NOW = "twitter_score_2"

def initMongo(client, collection):
    db = client[DB_NAME]
    try:
        db.create_collection(collection)
    except:
        pass
    return db[collection]

def get_hist_score_2():
    client = initMongo(MongoClient('mongodb://root:' + urllib.quote('longhash123!@#QAZ') + '@127.0.0.1'), SCORE_NOW)
    hist_score = client.find({},{"_id":0},sort=[("timestamp", pymongo.DESCENDING)]).limit(1680)
    all_scores = []
    for score in hist_score:
        all_scores.append([score['score'], score['timestamp']])
    
    timestamp = []
    score = []
    mag = []
    for i in range(int(len(all_scores)/12)):
        sentiment_scores = [item[0] for item in all_scores[i*12: (i+1)*12]]
        #magnitude_scores = [item[1] for item in all_scores[i*12: (i+1)*12]]
        avg_score = np.mean(sentiment_scores)
        #avg_mag = np.mean(magnitude_scores)
        timestamp.append(all_scores[i*12][2])
        score.append(avg_score)
        #mag.append(avg_mag)
    timestamp = timestamp[::-1]
    score = score[::-1]
    #mag = mag[::-1]
    for i, s in enumerate(score):
        if np.isnan(s) and i>0:
            score[i] = score[i-1]
    #for i, m in enumerate(mag):
    #    if np.isnan(m) and i>0:
    #        mag[i] = mag[i-1]
    #return {"data": {'timestamp':timestamp, 'score':score, 'mag':mag}}
    retrun{'data':{'timestamp':timestamp,'score':score}}
