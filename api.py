#!/usr/bin/python

from rauth import OAuth1Service
import requests
import logging
import httplib

# this uses the Rauth package, derived from the Requests package
# Rauth: http://rauth.readthedocs.org/en/latest/
# Requests: http://docs.python-requests.org/en/latest/

debug = True

etrade_info = {
    'consumer_key': 'your key here',
    'consumer_secret': 'your secret here',
    'request_token_url': 'https://etws.etrade.com/oauth/request_token',
    'authorize_token_url': 'https://us.etrade.com/e/t/etws/authorize',
    'access_token_url': 'https://etws.etrade.com/oauth/access_token',
    }

if debug:
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig() 
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    
service = OAuth1Service(
    consumer_key = etrade_info['consumer_key'],
    consumer_secret = etrade_info['consumer_secret'],
    request_token_url = etrade_info['request_token_url'],
    authorize_url = etrade_info['authorize_token_url'],
    access_token_url = etrade_info['access_token_url'])

# stage one: get the request token
request_token, request_token_secret = service.get_request_token(params={'oauth_callback': 'oob'})

# stage two: have the user authorize
# NOTE: We call rauth's get_authorize_url even though we will ignore the results
#       because etrade's url is not standard. We must call this method because
#       doing so sets some state within the service object that it needs later.
junk = service.get_authorize_url(request_token)
# now build the real auth request url. user must visit this url. eventually, he
# will be presented with a code, usually 5 characters, to enter as the verifier.
authorize_url = etrade_info['authorize_token_url'] + '?' + 'key=' + \
    etrade_info['consumer_key'] + '&' + 'token=' + request_token
    
print "*** point your browser at", authorize_url
oauth_verifier = raw_input("*** enter code from browser: ")
    
# stage three: fetch the access token
access_token, access_token_secret = service.get_access_token(request_token, request_token_secret,
                                                             params={'oauth_verifier': oauth_verifier})

# stage four: create the session
session = service.get_session((access_token, access_token_secret))

print "*** session established"

# we now have a working session. use it to fetch data.
accounts_raw = session.get('https://etwssandbox.etrade.com/accounts/sandbox/rest/accountlist.json')
print accounts_raw.text
