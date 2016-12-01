from bottle import route, run, template, request, static_file, redirect, error
import collections
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
import beaker.middleware
import bottle
import anydbm
import pickle
import calculator

#was used to display history per user
userHist = {}
#the database containing a mapping between words and which urls they match to
db = anydbm.open('searchbot_data.db', 'r')
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
	loggedIn = False
	email = ""
	global userHist
	#if the user has logged on, get their search history or create it
	if 'email' in session:
		email = session['email']
		loggedIn = True
		if email in userHist:
			displayHist = userHist[email]
		else:
			userHist[email] = collections.Counter()
	#this template shows the main search bar and a history table if there is any
	return template('find_bot.tpl', base="", history=displayHist, loggedIn=loggedIn, email=email)

@route('/login')
def home():
	flow = flow_from_clientsecrets("client_secret_248892728445-8nott1p07jt3bvnqhlouj7gjbif5cu66.apps.googleusercontent.com.json", scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', redirect_uri="http://localhost:8080/redirect")
	uri = flow.step1_get_authorize_url()
	redirect(str(uri))

@route('/search', method ='GET')
def do_search():
	#this is the search phrase the user has entered, it is split into
	#a list of separate words and then each word is counted using dictionary
	#counter from collections package
	loggedIn = False
	global userHist
	num_displayed = 5
	email = ""
	session = bottle.request.environ.get('beaker.session')
	if 'email' in session:
		email = session['email']
		loggedIn = True

	#get the search phrase and split it up into words, initialise counters	
	phrase = request.query['keywords']
	query = "keywords=" + phrase
	#use the calculator class to determine whether the search phrase can be evaluated or not
	calc = calculator.Calculator(phrase)
	value = calc.evaluate()
	words = phrase.split()
	count = collections.Counter()
	displayHist = collections.Counter()
	num_pages = 0
	urls = []
	#use this to display the correct amount of urls per page
	from_url = int(request.query['from_url']) if 'from_url' in request.query else 0
	for word in words:
		#for the user history - no longer displaying this for labs 3/4 but functionality still in place
		count[word] += 1
		if loggedIn:
			userHist[email][word] += 1
			displayHist = userHist[email]
		#If the word is in the database, add the urls for that word to the list of urls to be displayed
		if word in db:
			urlstring = db[word]
			new_urls = pickle.loads(urlstring)
			for url in new_urls:
				#if the url is not already in the list to be displayed, add it to the list
				if url[0] not in [i[0] for i in urls]:
					urls.append(url)
				#if the url is already in the list that means it is relevant for more than one word in the search phrase.
				#In this case we add the pagerank of the url to the pagerank of the existing url, giving it higher priority
				#as it is now relevant for more than one of the search words
				else:
					links = [i[0] for i in urls]
					titles = [i[1] for i in urls]
					ranks = [i[2] for i in urls]
					index = links.index(url[0])
					ranks[index] += url[2]
					urls = zip(links, titles, ranks)
	#sort using the rank in tuple
	urls.sort(key=lambda x: x[2])
	urls.reverse()
	num_pages = len(urls) / num_displayed
	if (len(urls) % num_displayed != 0):
		num_pages += 1
	#the search_results.tpl will insert a table into the existing html displaying the 
	#URLs for the searched words in order of pagerank.
	return template('search_results.tpl', num_displayed=num_displayed, query=query, from_url=from_url, num_pages=num_pages, word=phrase, urls=urls[from_url:from_url + num_displayed],loggedIn=loggedIn, email=email, val=value)

@route('/images/:filename#.*#')
def send_static(filename):
    return static_file(filename, root='./images/')

#user authentication
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
	session['email'] = user_email
	session.save()
	redirect('/')
@route('/logout')
def logout():
	session = bottle.request.environ.get('beaker.session')
	session.delete()
	redirect('/')
@error(404)
def error404(error):
    return """
        <h2> Sorry the page you are trying to access does not exist!
             Click to <a href="/">return to SearchBot</a>
        </h2>
    """
run(host='localhost', port=8080, debug=True, app=app)