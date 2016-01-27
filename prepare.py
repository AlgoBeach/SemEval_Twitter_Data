import pandas as pd
import json
import sys

def add_tweet(x):
    x = "%s" % x
    try:
        return tweet_data.get(x, {"text": "Not Available"})["text"].replace("\n", " ").replace("\r", " ")
    except:
        print x
        raise


def append_tweets(input_file, output_file):
    df = pd.read_csv(input_file, sep="\t", header=None)
    cols = df.columns.tolist()
    cols[0] = "tid"
    df.columns = cols
    df["text"] = df["tid"].apply(add_tweet)
    df.to_csv(output_file, sep="\t", header=None, index=False)
    print "Wrote dataframe with shape: ", df.shape


TWEET_DATA_FILE = "TWEET_DATA.json"
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to tab seperated input file. First column should be tweet id.")
    parser.add_argument("output_file", help="Path to output file.")
    parser.add_argument("-d", "--data-file", help="Path to the file which stores the tweet json data", default="TWEET_DATA.json")
    args = parser.parse_args()
    if args.input_file is None or args.output_file is None:
        parser.print_help()
        sys.exit(1)
    TWEET_DATA_FILE = args.data_file
    tweet_data = json.load(open(TWEET_DATA_FILE))
    print "Total %s tweets loaded: " % len(tweet_data)
    append_tweets(args.input_file, args.output_file)


