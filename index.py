# import Twitter API, access tokens and datetime for console log
from flask import Flask, redirect, url_for, render_template, request
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
    data = twitterData(name)
    return render_template("search.html", content=data, gameName=name.title())
# get twitter data, loop each tweet object, add attribute data to list, return list
def twitterData(game):
    # append user input with base query
    query = game + ' ' +baseQuery
    # finds recent tweets based on search query, default 10 max
    response = client.search_recent_tweets(query=query, tweet_fields=['created_at', 'lang'])
    datalist = []
    for tweet in response.data:
        sublist = []
        sublist.append(tweet.id)
        sublist.append(tweet.text)
        sublist.append(tweet.lang)
        sublist.append(tweet.created_at)
        datalist.append(sublist)

    return datalist
# runs website, runs it in debug mode (don't have to refresh page each time)
if __name__ == "__main__":
    app.run(debug=True)