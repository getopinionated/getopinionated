try:
    from twitter import *
    from facebook import *
except:
    import sys
    sys.path.append("../libs")
    sys.path.append("../getopinionated")
    from twitter import *
    from facebook import *
import urllib
from django.conf import settings

def posttotwitter(message):
    try:
        # see "Authentication" section below for tokens and keys
        t = Twitter(
                    auth=OAuth(settings.FEED_TWITTER_ACCESS_TOKEN, settings.FEED_TWITTER_ACCESS_SECRET,
                               settings.FEED_TWITTER_CONSUMER_KEY, settings.FEED_TWITTER_CONSUMER_SECRET)
                   )
        # Update your status
        t.statuses.update(status=message)
    except:
	raise
        print "posting to twitter feed failed. Message was: ", message

def posttofacebook(message): #This doesn't work yet, as it is impossible to keep keys for longer than 60 days, you can however connect your twitter-account to facebook
    APP_ID = ""
    APP_SECRET = ""
    
    APP_TOKEN = urllib.urlopen("https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials"%(APP_ID,APP_SECRET)).read()
    APP_TOKEN = APP_TOKEN[13:]
    print APP_TOKEN
    #Step 1: ask permission
    #https://www.facebook.com/dialog/permissions.request?_path=permissions.request&app_id=298186733641393&redirect_uri=https%3A%2F%2Fwww.facebook.com%2Fconnect%2Flogin_success.html%3Fdisplay%3Dpage&response_type=token&fbconnect=1&perms=status_update,publish_stream,manage_pages&from_login=1&m_sess=1&rcount=1
    #Step 2: get short lived access token
    #https://developers.facebook.com/tools/explorer
    appgraph = GraphAPI(APP_TOKEN)
    
    
    
    SHORT_ACCESS_TOKEN = ""
    usergraph = GraphAPI(SHORT_ACCESS_TOKEN)
    print usergraph.request("/oauth/access_token",{"client_id":APP_ID,"client_secret":APP_SECRET,"grant_type":"fb_exchange_token","fb_exchange_token":SHORT_ACCESS_TOKEN}) 
    
    print graph.request("/me/accounts", post_args={"access_token":"ACCESS_TOKEN"})
    profile = graph.get_object("getopinionated")
    graph.put_object("getopinionated", "feed", message=message)
    
    
if __name__ == "__main__":
    import sys
    sys.path.append("../libs")
    
    posttotwitter("hello")
    #posttofacebook("hello")
    
