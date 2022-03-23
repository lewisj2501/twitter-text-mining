from flask import Flask, redirect, url_for, render_template
# import Twitter API, access tokens and datetime for console log
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

# takes search query
query = 'elden ring -is:retweet'
# finds recent tweets based on search query
response = client.search_recent_tweets(query=query, tweet_fields=['created_at','lang'])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    data = twitterData()
    return render_template("search.html", content=data)

def twitterData():
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