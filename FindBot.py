from bottle import route, run, template, request, static_file, redirect
import collections
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
import beaker.middleware
import bottle
#the history counter is used throughout the session to store all the words that 
#have been searched for and how many times. The top 20 will be displayed
userHist = {}
email = ""
loggedIn = False
session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}
app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)
@route('/')
def display_search():
	session = bottle.request.environ.get('beaker.session')
	displayHist = collections.Counter()
	global email
	global loggedIn
	global userHist
	if 'logged_on' in session:
		loggedIn = session['logged_on']
	if loggedIn:
		if 'email' in session:
			email = session['email']
			if email in userHist:
				displayHist = userHist[email]
			else:
				userHist[email] = collections.Counter()
		else:
			return template('already_logged.tpl')
	#the template shows the main search bar and a history table if there is any
	return template('find_bot.tpl', base="", history=displayHist, loggedIn=loggedIn, email=email)

@route('/login')
def home():
	flow = flow_from_clientsecrets("client_secret_248892728445-8nott1p07jt3bvnqhlouj7gjbif5cu66.apps.googleusercontent.com.json", scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', redirect_uri="http://localhost:8080/redirect")
	uri = flow.step1_get_authorize_url()
	redirect(str(uri))

#when the form is submitted the POST method will be called
@route('/', method ='POST')
def do_search():
	#this is the search phrase the user has entered, it is split into
	#a list of separate words and then each word is counted using dictionary
	#counter from collections package
	global userHist
	phrase = request.forms.get('keywords')
	words = phrase.split()
	count = collections.Counter()
	displayHist = collections.Counter()
	for word in words:
		count[word] += 1
		if loggedIn:
			userHist[email][word] += 1
			displayHist = userHist[email]
	#the search.tpl will insert a table into the existing html displaying the 
	#keywords and counting the appearances of each word.
	return template('search.tpl', phrase=phrase, counter=count, history=displayHist, num_words=len(words), loggedIn=loggedIn, email=email)

@route('/images/:filename#.*#')
def send_static(filename):
    return static_file(filename, root='./images/')

@route('/redirect')
def redirect_page():
	CLIENT_ID = '248892728445-8nott1p07jt3bvnqhlouj7gjbif5cu66.apps.googleusercontent.com'
	CLIENT_SECRET = 'szDO0M_8Hww51N3hnsYu1Gk1'
	REDIRECT_URI = 'http://localhost:8080/redirect'
	SCOPE = 'https://www.googleapis.com/auth/drive.file'
	code = request.query.get('code', '')
	flow = OAuth2WebServerFlow(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,scope=SCOPE,redirect_uri=REDIRECT_URI)
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub']
	http = httplib2.Http()
	http = credentials.authorize(http)
	# Get user email
	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = user_document['email']
	session = bottle.request.environ.get('beaker.session')
	session['logged_on'] = True
	session['email'] = user_email
	redirect('/')
@route('/logout')
def logout():
	session = bottle.request.environ.get('beaker.session')

	session['logged_on'] = False
	redirect('/')
run(host='localhost', port=8080, debug=True, app=app)