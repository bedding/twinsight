import re
import codecs
import sys
from string import punctuation
from collections import defaultdict
import sqlite3

emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpPXx/\:\}\{@\|\\] # mouth      
      |
      [\)\]\(\[dDpPxX/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

def filtering(tweet):
    # remove emoticon
    new_tweet = re.sub(emoticon_string, ' ', tweet)

    # remove RT
    new_tweet.replace('RT', ' ')

    # remove punctuation
    new_tweet = "".join(c for c in new_tweet if c not in punctuation)
    
    return new_tweet.lower()

def remove_stop_words(tokens):
    new_tokens = [t for t in tokens if t not in ['a', 'an', 'the']]
    return new_tokens

def attach_negation(tokens):
    # attach
    i = 0
    while i < len(tokens):
        if tokens[i] == 'no' or tokens[i] == 'not':
            if i == 0:
                tokens[i+1] = tokens[i] + '+' + tokens[i+1]
            elif i == len(tokens) - 1:
                tokens[i-1] = tokens[i-1] + '+' + tokens[i]
            else:
                tokens[i+1] = tokens[i] + '+' + tokens[i+1]
                tokens[i-1] = tokens[i-1] + '+' + tokens[i]
        i += 1
    # delete original
    new_tokens = [t for t in tokens if t not in ['no','not']]

    return new_tokens

if __name__ == '__main__':
    corpus_file = codecs.open(sys.argv[1])
    bigrams_map = defaultdict()

    count = 0
    corpus_size = 0
    tweets = corpus_file.readlines()
    for tweet in tweets:
        # filter
        clean_tweet = filtering(tweet)

        # tokenize
        tokens = clean_tweet.split()

        # remove stop words
        tokens = remove_stop_words(tokens)

        if len(tokens) > 1:
            # attach negation
            tokens = attach_negation(tokens)

            # constrcut bigrams
            i = 0
            while i < len(tokens) - 1:
                bigram = tokens[i] + ' ' + tokens[i+1]
                if bigram not in bigrams_map.keys():
                    bigrams_map[bigram] = 1
                else:
                    bigrams_map[bigram] += 1
                i += 1
            corpus_size += 1
        count += 1
        if count % 1000 == 0:
            print 'now at ' + str(count)
        if corpus_size == 66749:
            break

    print 'save into db'

    conn = sqlite3.connect('features1.db')
    # save features into database
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS positive
                (bigram Text, freq INTEGER)''')
    #c.execute('''CREATE TABLE IF NOT EXISTS config
    #            (corpus_size integer)''')
    #c.execute('INSERT INTO config VALUES (%d)' % corpus_size)
    for key, value in bigrams_map.items():
        c.execute('INSERT INTO positive VALUES (\'%s\', %d)' % (key, value))
    conn.commit()
    conn.close()

        
