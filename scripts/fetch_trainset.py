import codecs
import sys
import os
import re

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
    n = int(sys.argv[2])
    f = codecs.open(sys.argv[1], 'r', 'utf-8')
    #utput = codecs.open("test.csv", 'w', 'utf-8')
    pos = codecs.open("pos.txt", "a", "utf-8")
    neg = codecs.open("neg.txt", "a", "utf-8")
    i = 0
    for line in f.readlines():
        tweet = line.split(',')[3]
        
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
            neg.write(clean_tweet + os.linesep)
#        else:
#            ret = neg_re.search(clean_tweet)
#            if ret is not None:
#                neg.write(clean_tweet + os.linesep)
        
