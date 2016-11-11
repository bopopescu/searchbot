import anydbm
import pickle

# open the databases as read only
db = anydbm.open('my.db', 'r')
db2 = anydbm.open('rank.db', 'r')

# see contents of anydbms
print 'These are the open databases:'
print db
print db2

# search for a word in the database
word = 'Google'
if word in db: # existance check
    urlstr = db[word]
    urlset = pickle.loads(urlstr)
    url = urlset.pop() # set elements can only be popped, see set operations
    if url in db2:
        print '\n%s found in url %s rank %d' % (word, url, int(db2[url]))

# search for the list of urls, which is easier to manipulate
word = 'Googlelist'
if word in db:
    print 'first element in', word, 'list is', pickle.loads(db[word])[0], '\n'

# can access other database same way
for web in db2:
    print web, 'has a rank', db2[web]

# close when done
db.close()
db2.close()

