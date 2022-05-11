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
    overall_sentiment_array = []
    detailed_sentiment_array = []

    for x, y in data[6].items():
        tuple = x, y
        overall_sentiment_array.append(tuple)

    overallLabels = [row[0] for row in overall_sentiment_array]
    overallValues = [row[1] for row in overall_sentiment_array]

    for x, y in data[7].items():
        tuple = x, y
        detailed_sentiment_array.append(tuple)

    detailedlLabels = [row[0] for row in detailed_sentiment_array]
    detailedValues = [row[1] for row in detailed_sentiment_array]

    return render_template("search.html", content=data[0], name=name.title(), mediaType=data[1], score=data[2],
                           sentiment=data[3], posTweets=data[4], negTweets=data[5],overallLabels=overallLabels,
                           overallValues=overallValues, detailedLabels=detailedlLabels, detailedValues=detailedValues)


# get twitter data, loop each tweet object, add attribute data to list, return list
def twitterData(title, genre):
    # append user input with base query
    query = title + ' ' + baseQuery
    overall_twitter_critic_score = 0
    overall_twitter_critic_sentiment = ""
    pos_twitter_critic_score = []
    neg_twitter_critic_score = []
    neu_twitter_critic_score = []
    # finds recent tweets based on search query, default 10 max
    response = client.search_recent_tweets(query=query,
                                           tweet_fields=['created_at', 'lang', 'context_annotations', 'entities'],
                                           max_results=100)
    # datalist holds a list containing lists of tweet objects
    datalist = []
    neg_tweets = []
    pos_tweets = []
    sentiment_dict = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }

    detailed_sentiment_dict = {
        "Extremely Positive": 0,
        "Very Positive": 0,
        "Fairly Positive": 0,
        "Mildly Positive": 0,
        "Extremely Negative": 0,
        "Very Negative": 0,
        "Fairly Negative": 0,
        "Mildly Negative": 0,
        "Neutral": 0
    }
    for tweet in response.data:
        # filters for tweets in engilsh
        if tweet.lang == "en" and contextMatch(tweet, genre) == True:
            # each tweet object is added to this list
            sublist = []
            posTweets = []
            negTweets = []
            # after tokenising the tweet text, add the words (tokens) to this list
            finalTweet = []
            sentiment_score = 0
            # string that holds the sentiment of a tweet
            tweet_polarity = ""
            # cleansing process of the text
            tweet_text = tweet.text
            cleaned_tokenised_tweet = tweetTokenise(tweet_text,finalTweet,title)
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
                neg_twitter_critic_score.append(sentiment_score)
                x = sentiment_dict.get("Negative") + 1
                sentiment_dict.update({"Negative": x})
                if sentiment_score > 60:
                    tweet_polarity = "Extremely Negative Tweet"
                    neg_tweets.append(tweet.text)
                    x = detailed_sentiment_dict.get("Extremely Negative") + 1
                    detailed_sentiment_dict.update({"Extremely Negative": x})
                elif 60 > sentiment_score > 40:
                    tweet_polarity = "Very Negative Tweet"
                    neg_tweets.append(tweet.text)
                    x = detailed_sentiment_dict.get("Very Negative") + 1
                    detailed_sentiment_dict.update({"Very Negative": x})
                elif 40 > sentiment_score > 20:
                    tweet_polarity = "Fairly Negative Tweet"
                    x = detailed_sentiment_dict.get("Fairly Negative") + 1
                    detailed_sentiment_dict.update({"Fairly Negative": x})
                else:
                    tweet_polarity = "Mildly Negative Tweet"
                    x = detailed_sentiment_dict.get("Mildly Negative") + 1
                    detailed_sentiment_dict.update({"Mildly Negative": x})
            elif pos > neg:
                x = sentiment_dict.get("Positive") + 1
                sentiment_dict.update({"Positive": x})
                sentiment_score = round(pos * 100)
                pos_twitter_critic_score.append(sentiment_score)
                if sentiment_score > 60:
                    tweet_polarity = "Extremely Positive Tweet"
                    pos_tweets.append(tweet_text)
                    x = detailed_sentiment_dict.get("Extremely Positive") + 1
                    detailed_sentiment_dict.update({"Extremely Positive": x})
                elif 60 > sentiment_score > 40:
                    tweet_polarity = "Very Positive Tweet"
                    pos_tweets.append(tweet_text)
                    x = detailed_sentiment_dict.get("Very Positive") + 1
                    detailed_sentiment_dict.update({"Very Positive": x})
                elif 40 > sentiment_score > 20:
                    tweet_polarity = "Fairly Positive Tweet"
                    x = detailed_sentiment_dict.get("Fairly Positive") + 1
                    detailed_sentiment_dict.update({"Fairly Positive": x})
                else:
                    tweet_polarity = "Mildly Positive Tweet"
                    x = detailed_sentiment_dict.get("Mildly Positive") + 1
                    detailed_sentiment_dict.update({"Mildly Positive": x})
            else:
                tweet_polarity = "Neutral Tweet"
                sentiment_score = 0
                x = sentiment_dict.get("Neutral") + 1
                sentiment_dict.update({"Neutral": x})
                x = detailed_sentiment_dict.get("Neutral") + 1
                detailed_sentiment_dict.update({"Neutral": x})
                neu_twitter_critic_score.append(sentiment_score)
            # add tweet object properties to list that will be displayed on web page
            sublist.append(tweet.text)
            sublist.append(tweet.lang)
            sublist.append(tweet.created_at)
            sublist.append(tweet_polarity)
            # add list of tweet object to the list of other tweet objects
            datalist.append(sublist)
            negTweets.append(neg_tweets)
            posTweets.append(pos_tweets)
        else:
            # dont do anything if not english
            print("/n")

    if len(neg_twitter_critic_score) > len(pos_twitter_critic_score):
        avg_score = sum(neg_twitter_critic_score) / len(neg_twitter_critic_score)
        overall_twitter_critic_score = round(avg_score)
        if avg_score > 60:
            overall_twitter_critic_sentiment = "Extremely Negative"
        elif 60 > avg_score > 40:
            overall_twitter_critic_sentiment = "Very Negative"
        elif 40 > avg_score > 20:
            overall_twitter_critic_sentiment = "Fairly Negative"
        else:
            overall_twitter_critic_sentiment = "Mildly Negative"
        print("Negative Feeling")
    elif len(pos_twitter_critic_score) > len(neg_twitter_critic_score):
        avg_score = sum(pos_twitter_critic_score) / len(pos_twitter_critic_score)
        overall_twitter_critic_score = round(avg_score)
        if avg_score > 60:
            overall_twitter_critic_sentiment = "Extremely Positive"
        elif 60 > avg_score > 40:
            overall_twitter_critic_sentiment = "Very Positive"
        elif 40 > avg_score > 20:
            overall_twitter_critic_sentiment = "Fairly Positive"
        else:
            overall_twitter_critic_sentiment = "Mildly Positive"
        print("Positive Feeling")
    else:
        overall_twitter_critic_score = 0
        overall_twitter_critic_sentiment = "Neutral"
        print("Neutral Feeling")

    media_type = ""
    print(genre)
    if int(genre) == 71:
        media_type = "Video Game"
    elif int(genre) == 86:
        media_type = "Film"
    elif int(genre) == 3:
        media_type = "TV Show"
    elif int(genre) == 0:
        media_type = "No results were found. Perhaps the topic you are looking for is in another category."
    else:
        media_type = "No results were found. Perhaps the topic you are looking for is in another category."

    return datalist, media_type, overall_twitter_critic_score, overall_twitter_critic_sentiment, pos_tweets, neg_tweets, sentiment_dict, detailed_sentiment_dict

def contextMatch(tweet, genre):
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

    return tweet_context_match

def tweetTokenise(tweet_text,finalTweet,title):
    # converts tweet text to all lowercase
    tweet_text_lower = tweet_text.lower()
    # removes punctuation
    cleaned_tweet = tweet_text_lower.translate(str.maketrans('', '', string.punctuation))
    # nltk function that tokenises tweet text (breaks into words)
    tokenised_tweet = word_tokenize(cleaned_tweet, "english")
    # removes english stop words (e.g. I, so, a, our, etc. ), removes title and appends to finalTweet list
    # the title is removed to avoid confilct with the analyser (e.g. breaking bad is very negative)
    for token in tokenised_tweet:
        if token not in stopwords.words('english') and token not in title.lower():
            finalTweet.append(token)
    # converts finalTweet list (all the valuble words in the tweet) back to a string
    cleaned_tokenised_tweet = ' '.join(map(str, finalTweet))

    return cleaned_tokenised_tweet

# runs website, runs it in debug mode (don't have to refresh page each time)
if __name__ == "__main__":
    app.run(debug=True)