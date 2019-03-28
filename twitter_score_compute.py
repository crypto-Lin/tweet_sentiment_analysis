# load trained model
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import pickle

import pymongo
from pymongo import MongoClient
import time
import numpy as np
import urllib.parse

# clear tweet
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
import re
from textblob import Word, TextBlob
import enchant

import logging
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

logging.basicConfig(filename='/home/zhangli/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# loading
with open('/home/zhangli/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
tokenizer.oov_token = None

sentiment_model = load_model('/home/zhangli/best_cnn_weights.hdf5')

# get updated tweets
DB_NAME = "longhash"
BASE_COLLECTION = "twitter"
TWITTER_SCORE = "twitter_score_2"

def initMongo(client, collection):
    db = client[DB_NAME]
    try:
        db.create_collection(collection)
    except:
        pass
    return db[collection]

def insertMongo(client, d):
    try:
        client.insert_one(d)
        return None
    except Exception as err:
        #print(err)
        logging.error(err)
    
def save_info(client, info):
    insertMongo(client, info)
        
# 获取单词的词性
def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def my_word_lemmatize(sentence):   
    tokens = word_tokenize(sentence)  # 分词
    tagged_sent = pos_tag(tokens)     # 获取单词词性

    wnl = WordNetLemmatizer()
    lemmas_sent = []
    for tag in tagged_sent:
        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
        lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos)) # 词形还原

    return lemmas_sent

def clear_tweet_text(text, emoji_data):
    filters = ['rt','io','...','..','quot','gt']
    
    pat1 = r'@[A-Za-z0-9_.-]+'
    pat2 = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    combined_pat = r'|'.join((pat1, pat2))    
    text_cleaned = re.sub(combined_pat, ' ', text)
    
    text_cleaned = ' '.join([' '+emoji_data[w]+' ' if w in emoji_data.keys() else w for w in nltk.word_tokenize(text_cleaned)])
    text_cleaned = ''.join([' '+emoji_data[c]+' ' if c in emoji_data.keys() else c for c in text_cleaned ])
   
    letters_only = re.sub("[^a-zA-Z!?\.']", " ", text_cleaned)
    lower_case = letters_only.lower()
    lower_case = lower_case.replace('n\'t',' not')
    
    words = my_word_lemmatize(lower_case) 
    
    words = [i for i in words if (len(i)>1) or (i in ['i'])]
    cleaned_words = [word for word in words if (d.check(word))]

    cleaned_words = [i for i in cleaned_words if i not in filters]
    
    return ' '.join(cleaned_words)
    
def get_top_tweets(skipnums, nums):
    base_client = initMongo(MongoClient('mongodb://root:' + urllib.parse.quote('longhash123!@#QAZ') + '@127.0.0.1'), BASE_COLLECTION)
    twitters = base_client.find({},{"_id":0, "clean_tweet":0, "created_date":0},sort=[("timestamp", pymongo.DESCENDING)]).limit(nums).skip(skipnums)
    data = []
    for twitter in twitters:
 
        data.extend(twitter['orign_tweet'])
    return data


if __name__ == '__main__':
    
    timestamp = int(time.time())
    client = initMongo(MongoClient('mongodb://root:' + urllib.parse.quote('longhash123!@#QAZ') + '@127.0.0.1'), TWITTER_SCORE)
    
    tweets = get_top_tweets(0, 1)
    
    d = enchant.Dict("en_US")
    emoji_client = initMongo(MongoClient('mongodb://root:' + urllib.parse.quote('longhash123!@#QAZ') + '@127.0.0.1'), 'emoji_name')    
    emoji_data = [emoji_client.find_one()][0]   
    del emoji_data['_id']
    
    try:
        clean_tweets = [clear_tweet_text(tweet, emoji_data) for tweet in tweets]
        
    except Exception as e:
        
        logging.error(e)
      
    # compute scores
    test_sequences = tokenizer.texts_to_sequences(clean_tweets)
    test_sequences_padding = pad_sequences(test_sequences, maxlen=140)
    scores = sentiment_model.predict(test_sequences_padding)
    score = np.mean(scores)
    doc = {"timestamp":timestamp, "score":round(float(score),4)}
    
    # below is test part
#     sc = []
#     tweets.append('i realy do n\'t like bitcoin ')
#     tweets.append('i love bitcoin ')
#     tweets.append('i hate cryptocurreny it make me bankrupt')
#     tweets.append('i didn\'t hate bitcoin ')
#     for text in tweets:
#         print(text)
#         ct = clear_tweet_text(text, emoji_data)
#         print(ct)
#         test_sequences = tokenizer.texts_to_sequences([ct])
#         test_sequences_padding = pad_sequences(test_sequences, maxlen=140)
#         scores = sentiment_model.predict(test_sequences_padding)
#         sc.append(scores)
#         print(scores)
#     print(np.mean(sc))
    
    save_info(client, doc)