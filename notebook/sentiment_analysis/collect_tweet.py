# -*- coding: utf-8 -*-
import string
import math
import time
import random
import urllib.parse
import json
import re

from requests_oauthlib import OAuth1Session

class TwitterClient:
    def __init__(self, consumer_key, consumer_secret, oauth_token = None, oauth_token_secret = None):
        self.client = OAuth1Session(consumer_key, consumer_secret, oauth_token, oauth_token_secret)

    def collect_tweet_by_word(self, word, count=1, page=1, max_id=None):
        result = None
        for i in range(page):
            params = {}
            qparams = []
            qparams.append('q=' + urllib.parse.quote(word))
            qparams.append('lang=ja')
            qparams.append('tweet_mode=extended')
            qparams.append('result_type=mixed')
            qparams.append('count={}'.format(count))
            if max_id is not None:
                qparams.append('max_id={}'.format(max_id))
            while(True):
                try:
                    ret = self.client.get("https://api.twitter.com/1.1/search/tweets.json?" + '&'.join(qparams), params = params)
                    retjson = json.loads(ret.text)
                    retjson['statuses']
                    break
                except:
                    print("refused connection: Sleeping...")
                    time.sleep(60*15)

            max_id = retjson['statuses'][-1]['id']-1
            if result is None and retjson['statuses']:
                result = retjson
            else:
                result['statuses'] += retjson['statuses']
        return result, max_id
    
    def download_tweets_by_word(self, word, outfile, count=1, page=1, max_id=None):
        i = 0
        while(True):
            try:
                data, max_id = self.collect_tweet_by_word(word, count, page, max_id)
                with open(outfile+"_{}.json".format(i), "w") as f:
                    json.dump(data, f)
            except Exception as e:
                print(e)
                print("Unknown Error. please fix the bug!")
                continue
            print("Processed: {}_{}.json".format(outfile, i))
            i = i+1