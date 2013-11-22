from django import forms
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from decimal import *
from tweetutil import *
from classifier.models import TestTweets
from tagger import *
from TwitterSearch import *
import time
from time import mktime
from datetime import datetime

def get_slot(intvl, curr_time, start_time):
    i = 0
    while start_time < curr_time:
        i += 1
        curr_time -= intvl
    return i

class KeywordForm(forms.Form):
    keyword = forms.CharField(max_length=100,
                              widget=forms.TextInput(attrs={'placeholder': 'Enter your keyword',
                                                            'class': 'form-control'}))

# main page
def index(request):
    if request.method == 'POST':
        form = KeywordForm(request.POST)
        if form.is_valid():
            # process data
            keyword = form.cleaned_data['keyword']
            return HttpResponseRedirect('/classifier/analysis/'+keyword)
    else:
        form = KeywordForm()

    return render(request, 'classifier/index.html', {
        'form': form,
        })

def analysis_keyword(request, keyword):
    try:
        form = KeywordForm()
        format_tweets = []
        raw_tweets = []
        time_slot = 20
        pos_timeline = [0]*time_slot
        neg_timeline = [0]*time_slot
        time_timeline = []
        tso = TwitterSearchOrder()
        tso.setKeywords([keyword])
        tso.setLanguage('en')
        tso.setCount(100)
        tso.setIncludeEntities(False)
        count = 200
        i = 0
        start_time = datetime.max
        end_time = datetime.min

        ts = TwitterSearch(
            consumer_key = 'argHv5V9fa175ygapOHf1g',
            consumer_secret ='pms9x6kFJ57WIz4SASnJQ6sMioCugsK2dnuMaD9CNo',
            access_token = '167017116-jonEZIB9hyFH0waEsISJooIrat05RaZkDmFdCB41',
            access_token_secret = 'A9cCFgrHuRt2sgBhtyiWhmktFSot1SkdlVckkJ477ZpSi'
            )
        # fetch
        for tweet in ts.searchTweetsIterable(tso):
            text = tweet['text']
            user = tweet['user']['screen_name']
            created_at = tweet['created_at']
            raw_tweets.append([text, user, created_at])
            if i >= count-1:
                break
            else:
                i += 1

        # tagging
        for tweet in raw_tweets:
            tag, pos_value, neg_value = tagger(tweet[0])
            if tag != 0:
                stime = time.strptime(tweet[2], "%a %b %d %H:%M:%S +0000 %Y")
                dt = datetime.fromtimestamp(mktime(stime))
                format_tweets.append([tweet[0], tweet[1], dt, tag, pos_value, neg_value])

        # statistics
        negative = 0
        for tweet in format_tweets:
            if tweet[3] == -1:
                negative += 1

        # generate timeline data
        for tweet in format_tweets:
            if tweet[2] < start_time:
                start_time = tweet[2]
            if tweet[2] > end_time:
                end_time = tweet[2]
        time_intvl = (end_time - start_time) / time_slot

        for tweet in format_tweets:
            slot = get_slot(time_intvl, tweet[2], start_time) - 1
            if tweet[3] == 1:
                pos_timeline[slot] += 1
            else:
                neg_timeline[slot] += -1

        # format final timeline data
        for i in range(time_slot):
            if i % 4 == 0:
                timestr = (start_time+i*time_intvl).strftime('%H:%M:%S')
            else:
                timestr = ''
            time_timeline.append([timestr, pos_timeline[i], neg_timeline[i]])

        template = loader.get_template('classifier/alys_result.html')
        context = RequestContext(request, {
            'format_tweets':format_tweets,
            'len':len(format_tweets),
            'neg': negative,
            'pos': len(format_tweets) - negative,
            'keyword': keyword,
            'timeline': time_timeline,
            'form': form,
            })
        return HttpResponse(template.render(context))
    except TwitterSearchException as e:
        template = loader.get_template('classifier/error.html')
        context = RequestContext(request, {
            'e_str': str(e),
            })
        return HttpResponse(template.render(context))

# tag a single tweet
def tag(request, testtweet_id):
    testtweet = TestTweets.objects.get(id=testtweet_id)
    bigrams = get_bigram_bag(testtweet.tweet)
    tag, pos, neg = tagger(testtweet.tweet)
    tag_string = get_tag_string(tag)
    template = loader.get_template('classifier/tag.html')
    context = RequestContext(request, {
        'bigrams': bigrams,
        'testtweet': testtweet,
        'tag_string': tag_string,
        'tag': tag,
        'pos': str(pos),
        'neg': str(neg),
        })
    return HttpResponse(template.render(context))

# test mode
def test(request):
    tweets = TestTweets.objects.all()[0:1000]
    count = 0
    neutral = 0
    for t in tweets:
        tag, pos, neg = tagger(t.tweet)
        if tag == -1:
            count += 1
        elif tag == 0:
            neutral += 1
    ratio = float(count) / (len(tweets) - neutral)
    template = loader.get_template('classifier/test.html')
    context = RequestContext(request, {
        'ratio': str(ratio)
        })
    return HttpResponse(template.render(context))
