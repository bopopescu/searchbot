import anydbm
import pickle

# open the database
db = anydbm.open('my.db', 'c')
# 'r' open existing database for reading only (default)
# 'w' open existing database for writing only
# 'c' open database for r/w, creating it if it doesn't exist
# 'n' always create a new empty database, open for reading and writing

# store like in a python dictionary
# but keys and values both must be strings
db['python'] = 'www.python.org'
db['pythonic'] = 'www.python.org'
db['pythonessent'] = 'www.python.org'
db['hello'] = 'www.helloworld.com'
db['world'] = 'www.helloworld.com'

# storing sets of urls as values -> convert to strings using pickling
urlset = set(['www.google.ca', 'www.google.com', 'www.google.ba'])
urlstr = pickle.dumps(urlset)
print urlstr # just to see what pickling looks like
db['Google'] = urlstr
db['Googlelist'] = pickle.dumps(list(urlset))

# close database when done
db.close()

# make second db with page ranks
rankdb = anydbm.open('rank.db', 'c')
rankresults = {'www.python.org':1, 'www.helloworld.com':2, 'www.google.ca':3, 'www.google.ba':9001}
# iterate thru dict and store all the k-v pairs
for website, rank in rankresults.items():
    rankdb[website] = str(rank)
# close when done storing
rankdb.close()

