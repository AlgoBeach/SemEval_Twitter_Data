
# coding: utf-8

# In[1]:

import pandas as pd
import json
import fnmatch
import os


# In[2]:

TWEET_DATA_FILE = "TWEET_DATA.json"
LABELS_BASE_DIR = "data/2download"
OUTPUT_DIR = "data/processed"
FILENAMES = []
INPUT_FILES = []
for root, dirnames, filenames in os.walk(LABELS_BASE_DIR):
    for filename in fnmatch.filter(filenames, '*subtask*.txt'):
        FILENAMES.append(filename)
        INPUT_FILES.append(os.path.join(root, filename))

print INPUT_FILES
print FILENAMES


# In[3]:

tweet_data = json.load(open(TWEET_DATA_FILE))
print len(tweet_data)


# In[4]:

df = pd.read_csv(INPUT_FILES[0], sep="\t", header=None)


# In[5]:

cols = df.columns.tolist()
cols[0] = "tid"
df.columns = cols
df.head()


# In[6]:

def add_tweet(x):
    x = "%s" % x
    try:
        return tweet_data.get(x, {"text": "Not Available"})["text"].replace("\n", " ").replace("\r", " ")
    except:
        print x
        raise


# In[7]:

df["text"] = df["tid"].apply(add_tweet)
df.head()


# In[8]:

df.to_csv("%s/%s" % (OUTPUT_DIR, FILENAMES[0]), sep="\t", header=None, index=False)


# In[23]:

def append_tweets(input_file, output_file):
    df = pd.read_csv(input_file, sep="\t", header=None)
    cols = df.columns.tolist()
    cols[0] = "tid"
    df.columns = cols
    df["text"] = df["tid"].apply(add_tweet)
    df.to_csv(output_file, sep="\t", header=None, index=False)
    print "Wrote dataframe with shape: ", df.shape


# In[10]:

append_tweets(INPUT_FILES[0], "%s/%s" % (OUTPUT_DIR, FILENAMES[0]))


# In[24]:

for input_file, output_file in zip(INPUT_FILES, ["%s/%s" % (OUTPUT_DIR, k) for k in FILENAMES]):
    print "Processing %s, saving to %s" % (input_file, output_file)
    append_tweets(input_file, output_file)


# In[25]:

len(INPUT_FILES), len(FILENAMES)


# In[26]:

len(zip(INPUT_FILES, ["%s/%s" % (OUTPUT_DIR, k) for k in FILENAMES]))


# In[27]:

get_ipython().run_cell_magic(u'bash', u'', u'cd data/processed/\nmkdir -p gold/{dev,devtest,train} input/devtest\nmv *.dev.gold.txt gold/dev\nmv *.devtest.gold.txt gold/devtest/\nmv *.train.gold.txt gold/train/\nmv *.devtest.input.txt input/devtest/\nls')


# In[28]:

get_ipython().run_cell_magic(u'bash', u'', u'cd data/processed/\nfind ./ -name "*.txt"')


# In[ ]:



