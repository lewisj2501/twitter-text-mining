# import Twitter API, access tokens and datetime for console log
from flask import Flask, redirect, url_for, render_template, request
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string
import tweepy as twitter
import keys
import time, datetime

# handle authentication to use API
auth = twitter.OAuthHandler(keys.API_KEY, keys.API_KEY_SECRET)
auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)
api = twitter.API(auth)
client = twitter.Client(bearer_token=keys.BEARER_TOKEN)
# takes a hashtag parameter(which tweets are to be retweeted, and a delay in seconds until it executes again)

app = Flask(__name__)

# takes search query, no retweets
baseQuery = '-is:retweet'


# default web page
@app.route("/")
def index():
    return render_template("index.html")


# search web page, passes twitter data to search view
@app.route('/search/', methods=['GET'])
def search():
    name = request.args.get('name')
    genre = request.args.get('media')
    data = twitterData(name, genre)
    return render_template("search.html", content=data, gameName=name.title())


# get twitter data, loop each tweet object, add attribute data to list, return list
def twitterData(title, genre):
    # append user input with base query
    query = title + ' ' + baseQuery
    # finds recent tweets based on search query, default 10 max
    # response = client.search_recent_tweets(query=query,tweet_fields=['created_at', 'lang'],max_results=100)
    response = client.search_recent_tweets(query=query,
                                           tweet_fields=['created_at', 'lang', 'context_annotations', 'entities'],
                                           max_results=100)
    # datalist holds a list containing lists of tweet objects
    datalist = []
    for tweet in response.data:
        tweet_context = tweet.context_annotations
        tweet_context_match = False
        for index in range(len(tweet_context)):
            for key in tweet_context[index]:
                new_dict = tweet_context[index][key]
                if genre in new_dict.values():
                    tweet_context_match = True
                    print("genre match")
                else:
                    print("genre doesn't match")
        # filters for tweets in engilsh
        if tweet.lang == "en" and tweet_context_match == True:
            # each tweet object is added to this list
            sublist = []
            # after tokenising the tweet text, add the words (tokens) to this list
            finalTweet = []
            sentiment_score = 0
            # string that holds the sentiment of a tweet
            tweet_polarity = ""
            # cleansing process of the text
            tweet_text = tweet.text
            # converts tweet text to all lowercase
            tweet_text_lower = tweet_text.lower()
            # removes punctuation
            cleaned_tweet = tweet_text_lower.translate(str.maketrans('', '', string.punctuation))
            # nltk function that tokenises tweet text (breaks into words)
            tokenised_tweet = word_tokenize(cleaned_tweet, "english")
            # removes english stop words (e.g. I, so, a, our, etc. ) and appends to finalTweet list
            for token in tokenised_tweet:
                if token not in stopwords.words('english'):
                    finalTweet.append(token)
            # converts finalTweet list (all the valuble words in the tweet) back to a string
            cleaned_tokenised_tweet = ' '.join(map(str, finalTweet))
            # uses nltk function to get polarity score (is the tweet neg, neu, or pos)
            tweet_polarity_score = SentimentIntensityAnalyzer().polarity_scores(cleaned_tokenised_tweet)
            # get dict neg value
            neg = tweet_polarity_score['neg']
            # get dict pos value
            pos = tweet_polarity_score['pos']
            # if the polarity is more negative than postive, determine tweet as negative, elif its postive,
            # else its neutral
            if neg > pos:
                sentiment_score = round(neg * 100)
                if sentiment_score > 60:
                    tweet_polarity = "Extremely Negative Tweet"
                elif 60 > sentiment_score > 40:
                    tweet_polarity = "Very Negative Tweet"
                elif 40 > sentiment_score > 20:
                    tweet_polarity = "Fairly Negative Tweet"
                else:
                    tweet_polarity = "Mildly Negative Tweet"
            elif pos > neg:
                sentiment_score = round(pos * 100)
                if sentiment_score > 60:
                    tweet_polarity = "Extremely Positive Tweet"
                elif 60 > sentiment_score > 40:
                    tweet_polarity = "Very Positive Tweet"
                elif 40 > sentiment_score > 20:
                    tweet_polarity = "Fairly Positive Tweet"
                else:
                    tweet_polarity = "Mildly Positive Tweet"
            else:
                tweet_polarity = "Neutral Tweet"
                sentiment_score = 0
            # add tweet object properties to list that will be displayed on web page
            sublist.append(tweet.text)
            sublist.append(tweet.lang)
            sublist.append(tweet.created_at)
            sublist.append(tweet_polarity)
            # add list of tweet object to the list of other tweet objects
            datalist.append(sublist)
        else:
            # dont do anything if not english
            print("/n")

    return datalist


# runs website, runs it in debug mode (don't have to refresh page each time)
if __name__ == "__main__":
    app.run(debug=True)
