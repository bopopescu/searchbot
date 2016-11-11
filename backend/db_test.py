import anydbm
import pickle

# open the databases as read only
db = anydbm.open('searchbot_data.db', 'r')
db_lexicon = anydbm.open('searchbot_lexicon.db', 'r')
db_inv_index = anydbm.open('searchbot_inv_index.db', 'r')
db_pagerank = anydbm.open('searchbot_pagerank.db', 'r')
db_doc_index = anydbm.open('searchbot_doc_index.db', 'r')

i = 1
for key in db:
    if i > 1:
        break
    print key, 'maps to ', pickle.loads(db[key])
    i += 1

word = 'canada'
print ''
if word in db:
    print word, 'maps to', pickle.loads(db[word])
else:
    print word, 'not found'

print ''
if word in db_lexicon:
    print word, 'lexicon to', pickle.loads(db_lexicon[word])
else:
    print word, 'not found'

print ''
word = '99'
if word in db_inv_index:
    print word, 'inverted index to', pickle.loads(db_inv_index[word])
else:
    print word, 'not found'

print ''
word = '5'
if word in db_pagerank:
    print word, 'page rank to', pickle.loads(db_pagerank[word])
else:
    print word, 'not found'
    
print ''
word = '5'
if word in db_doc_index:
    print word, 'document index to', pickle.loads(db_doc_index[word])
else:
    print word, 'not found'

db.close()
db_lexicon.close()
db_inv_index.close()
db_pagerank.close()
db_doc_index.close()
