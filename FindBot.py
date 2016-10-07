from bottle import route, run, template, request, static_file
import collections
#the history counter is used throughout the session to store all the words that 
#have been searched for and how many times. The top 20 will be displayed
history = collections.Counter()
@route('/')
def display_search():
	#the template shows the main search bar and a history table if there is any
	return template('find_bot.tpl', base="", history=history)
#when the form is submitted the POST method will be called
@route('/', method ='POST')
def do_search():
	#this is the search phrase the user has entered, it is split into
	#a list of separate words and then each word is counted using dictionary
	#counter from collections package
	phrase = request.forms.get('keywords')
	words = phrase.split()
	count = collections.Counter()
	for word in words:
		count[word] += 1
		history[word] += 1
	#the search.tpl will insert a table into the existing html displaying the 
	#keywords and counting the appearances of each word.
	return template('search.tpl', phrase=phrase, counter=count, history=history, num_words=len(words))
@route('/images/:filename#.*#')
def send_static(filename):
    return static_file(filename, root='./images/')
run(host='localhost', port=8080, debug=True)
