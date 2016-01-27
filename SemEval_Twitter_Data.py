
# coding: utf-8

# # SEMEVAL 2016
# 
# ## Data Download
# 
# Download all the data for SEMEVAL competition
# 
# Data details at: http://alt.qcri.org/semeval2016/task4/index.php?id=data-and-tools
# 
# Download the file http://alt.qcri.org/semeval2016/task4/data/uploads/semeval2016-task4.traindevdevtest.v1.2.zip
# 
# ```
# wget http://alt.qcri.org/semeval2016/task4/data/uploads/semeval2016-task4.traindevdevtest.v1.2.zip
# cd data
# unzip semeval2016-task4.traindevdevtest.v1.2.zip
# ```
# 
# Extract all the tweet ids from all the files:
# ```
# find ./data/ -name "*.txt" | grep -v README | xargs cut -f1 | sort | uniq > tweet_ids.txt
# ```
# 
# 
# Install `tweepy` using `pip install tweepy`
# 

# In[22]:

import json
import tweepy as tpy
import pprint as pp
import time
import datetime
import traceback
import codecs

# In[2]:

authentication_file = "auth_keys.json"
TWEETS_TEXT_FILE = "TWEET_TEXT.txt"
TWEETS_DATA_FILE = "TWEET_DATA.json"
TWEETS_IDS_FILE = "tweet_ids.txt"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--tweet_ids_file", help="Path to the tweet ids file. Should contain only 1 tweet per line.", default="tweet_ids.txt")
    parser.add_argument("-a", "--auth-file", help="Path to the auth_keys.json file", default="auth_keys.json")
    parser.add_argument("-t", "--text-file", help="Path to the file where to store tweet text only", default="TWEET_TEXT.txt")
    parser.add_argument("-d", "--data-file", help="Path to the file where to store full tweet json data", default="TWEET_DATA.json")
    args = parser.parse_args()
    authentication_file = args.auth_file
    TWEETS_TEXT_FILE = args.text_file
    TWEETS_DATA_FILE = args.data_file
    TWEETS_IDS_FILE = args.tweet_ids_file

    print "Using the following parameters while loading data: "
    print "authentication_file: %s" % authentication_file
    print "TWEETS_TEXT_FILE: %s" % TWEETS_TEXT_FILE
    print "TWEETS_DATA_FILE: %s" % TWEETS_DATA_FILE
    print "TWEETS_IDS_FILE: %s" % TWEETS_IDS_FILE
    print "Now starting processing..."
    

# Load the authentication codes from the file
authentication_codes = json.load(open(authentication_file))

# In[4]:

key_missing = lambda k,d: (k not in d) or d[k] == ""
access_keys = ["access_token", "access_token_secret"]
consumer_keys = ["consumer_key", "consumer_secret"]

assert sum(key_missing(k, authentication_codes) for k in access_keys) == 0,"Please set consumer key and consumer secret in %s" % authentication_file
auth = tpy.OAuthHandler(authentication_codes[consumer_keys[0]], authentication_codes[consumer_keys[1]])
if sum(key_missing(k, authentication_codes) for k in access_keys):
    # Start oauth dance and get the verification URL:
    try:
        redirect_url = auth.get_authorization_url()
    except tpy.TweepError:
        print 'Error! Failed to get request token.'
    print "Go to the following URL: \n", redirect_url
    verifier = raw_input("Enter the verification code: ")
    try:
        auth.get_access_token(verifier)
        authentication_codes[access_keys[0]] = auth.access_token
        authentication_codes[access_keys[1]] = auth.access_token_secret
        print "Got new access token details. Saving to file: %s" % authentication_file
        json.dump(authentication_codes, open(authentication_file, "wb+"), indent=4)
    except tpy.TweepError:
        print 'Error! Failed to get access token.'
else:
    print "Setting already existing authentication codes."
    auth.set_access_token(authentication_codes[access_keys[0]], authentication_codes[access_keys[1]])

print "Initializing tweepy API"
api = tpy.API(auth)



# In[34]:

try:
    tweets_data = json.load(open(TWEETS_DATA_FILE))
    # Save backup of old data:
    print "Saving backup data in %s" % (TWEETS_DATA_FILE+".backup")
    json.dump(tweets_data, open(TWEETS_DATA_FILE+".backup", "wb+"))
except:
    print "Either file %s doesn't exist or error reading file. Will create new file." % TWEETS_DATA_FILE
    tweets_data = {}

total, existing, new_downloaded, not_available = 0, 0, 0, 0
text = ""
with open(TWEETS_IDS_FILE) as tid_fp, codecs.open(TWEETS_TEXT_FILE, "wb+", "utf-8") as ttxt_fp:
    for i, tid in enumerate(tid_fp.readlines()):
        if (i % 50) == 0:
            print "Finished reading %s lines. Next TID: %s" % (i, tid)
        tid = tid[:-1]
        if tid in tweets_data:
            text = tweets_data[tid]["text"].replace("\n", " ").replace("\r", " ")
            existing += 1
            total += 1
        connection_tries = 0 # To fix intermittent connections
        while tid not in tweets_data:
            try:
                print "Trying to download: %s, %s" % (i, tid)
                status = api.get_status(tid)
                print "Download success"
                tweets_data[tid] = status._json
                text = status.text.replace("\n", " ").replace("\r", " ")
                new_downloaded += 1
                total += 1
            except tpy.RateLimitError:
                rate = api.rate_limit_status()
                reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
                now = datetime.datetime.today()
                future = datetime.datetime.fromtimestamp(reset)
                seconds = (future-now).seconds+1
                if seconds < 10000:
                    print "Rate limit exceeded, sleeping for %s seconds until %s\n Will resume downloading: %s" % (seconds, future, tid)
                    print "Finished downloading %s tweets. Total: %s, Existing: %s, Not Available: %s" % (new_downloaded, total, existing, not_available)
                    print "Writing intermediate data with %s tweets to file: %s" % (len(tweets_data), TWEETS_DATA_FILE+".middle")
                    with open(TWEETS_DATA_FILE+".middle", "wb+") as fp_temp:
                        json.dump(tweets_data, fp_temp)
                    print "Finished writing. Now sleeping for %s seconds." % seconds
                    time.sleep(seconds)
                    print "Resume downloading: %s at %s" % (tid, datetime.datetime.today())
            except tpy.TweepError as e:
                print "Encountered error: ", e
                if e.api_code in [34, 179, 144, 63]:
                    print "Tweet id: %s not found. Using placeholder text" % tid
                    text = "Not Available"
                    tweets_data[tid] = {"text": text}
                    not_available += 1
                    total += 1
                elif "Failed to send request: HTTPSConnectionPool" in e.__str__():
                    if connection_tries < 10:
                        connection_tries += 1
                        now = datetime.datetime.today()
                        seconds = 1000
                        future = now + datetime.timedelta(seconds=seconds)
                        print "Network connection issues. Trying to reconnect % time, after %s seconds at %s" % (connection_tries, seconds, future)
                        time.sleep(seconds)
                        print "Awake. Trying to reconnect for the %s time using tid = %s" % (connection_tries, tid)
                    else:
                        print "Tried reconnecting %s times. Aborting. Follow stack trace: \n", (connection_tries, traceback.format_exc())
                        raise
                else:
                    print "Encountered some other error. Follow stack trace:\n", traceback.format_exc()
                    raise
            except:
                print "Encountered some other error. Follow stack trace:\n", traceback.format_exc()
                raise
        print "Writng to %s to text file %s." % (tid, TWEETS_TEXT_FILE)
        print >> ttxt_fp, '%s\t%s' % (tid, text)
        if new_downloaded % 100 == 0 and new_downloaded > 1:
            print "Finished downloading %s tweets. Total: %s, Existing: %s, Not Available: %s" % (new_downloaded, total, existing, not_available)

print "Finished downloading all tweets. New: %s, Total: %s, Existing: %s, Not Available: %s" % (new_downloaded, total, existing, not_available)
print "Writing new data with %s tweets to file: %s" % (len(tweets_data), TWEETS_DATA_FILE)
json.dump(tweets_data, open(TWEETS_DATA_FILE, "wb+"))





