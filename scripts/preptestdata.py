import codecs
import os
import re
from time import *
import time

def removeNonAscii(s):
    return "".join(i for i in s if ord(i)<128)

emoticon_positive = r"""
    [:;=X8]         # eyes
    [\-]?           # nose
    [\)\]DpP]       # mouth
    |
    [\(\[]          # mouth
    [\-]?           # nose
    [:=8]           # eyes"""

emoticon_negative = r"""
    [:=]            # eyes
    [\']?           # tear
    [\-]?           # nose
    [\(\[]          # mouth
    |
    [\)\]D]         # mouth
    [\-]?           # nose
    [\']?           # tear
    [:=]            # eyes"""

username_string = r"""(?:@[\w_]*\:?)"""

hashedtag_string = r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""

url_string = r"""https?://.*[\s]*"""

html_string = r"""(&\w+;)"""

comma_string = r"""ESCOMMA"""

return_string = r"""ESRETURN"""

textinbrkt_string = r"""(?:\[.*\]|\(.*\))"""

pos_re = re.compile(emoticon_positive, re.VERBOSE | re.UNICODE)
neg_re = re.compile(emoticon_negative, re.VERBOSE | re.UNICODE)


if __name__ == '__main__':
    f = codecs.open('../mined/11-08-13.csv', 'r', 'utf-8')
    pos = codecs.open("pos-test.csv", "a+", "utf-8")
    neg = codecs.open("neg-test.csv", "a+", "utf-8")
    i = 0
    for line in f.readlines():
        items = line.split(',')
        tweet = items[3]
        
        # clean tweet
        clean_tweet = re.sub(url_string, '', tweet)
        clean_tweet = re.sub(hashedtag_string, '', clean_tweet)
        clean_tweet = re.sub(username_string, '', clean_tweet)
        clean_tweet = re.sub(html_string, '', clean_tweet)
        clean_tweet = re.sub(comma_string, ' ,', clean_tweet)
        clean_tweet = re.sub(return_string, ' .', clean_tweet)
        clean_tweet = re.sub(textinbrkt_string, '', clean_tweet)

        # remove non-ascii characters
        clean_tweet = removeNonAscii(clean_tweet)
        
        # remove duplicate whitespace
        clean_tweet = " ".join(clean_tweet.split())

        # check if the tweet contain postive/negative emoticon
        ret = neg_re.search(clean_tweet)
        if ret:
            t = time.strptime(items[5].strip(), "%a %b %d %H:%M:%S +0000 %Y")
            newtime = strftime("%Y-%m-%d %H:%M:%S", t)
            newline = ','.join([items[1], items[2], items[3], newtime])
            neg.write(newline + os.linesep)
        else:
            ret = pos_re.search(clean_tweet)
            if ret:
                t = time.strptime(items[5].strip(), "%a %b %d %H:%M:%S +0000 %Y")
                newtime = strftime("%Y-%m-%d %H:%M:%S", t)
                newline = ','.join([items[1], items[2], items[3], newtime])
                pos.write(newline + os.linesep)



