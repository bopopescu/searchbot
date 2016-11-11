
# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re

# LAB 3
# to calculate the page ranks using the reference algorithm
from pagerank import page_rank
# for persistent storage
import anydbm
import pickle

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        
        
        # LAB 1 initialization of inverted index and resolved inv index
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self._inv_index = { }
        self._resolved_inv_index = { }
        self._doc_index = { }
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # LAB 3 initialize list of links
        self._set_of_links = set()


        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title and increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
    # TODO remove me in real version
    def _mock_insert_document(self, url):
        """A function that pretends to insert a url into a document db table
        and then returns that newly inserted document's id."""
        ret_id = self._mock_next_doc_id
        self._mock_next_doc_id += 1
        return ret_id
    
    # TODO remove me in real version
    def _mock_insert_word(self, word):
        """A function that pretends to insert a word into the lexicon db table
        and then returns that newly inserted word's id."""
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        return ret_id
    
    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]
        
        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word, 
        #          store it in the word id cache, and return the id.

        word_id = self._mock_insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.
        
        doc_id = self._mock_insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""
		
        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # TODO insert (from, to) tuple into the list of links
        
        # Lab 3 saving links
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self._set_of_links.add((from_doc_id, to_doc_id))
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print "document title="+ repr(title_text)

        # TODO update document title for document id self._curr_doc_id
        self._doc_index[self._curr_doc_id] = [title_text]
    
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        
        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url
    
    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        print "    num words="+ str(len(self._curr_words))

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))
            
            # LAB 1 - call new function to populate both indexes
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~
            self.update_inv_indexes(word)
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # other extra implementation - store few text lines as info in doc index
        #if self._curr_doc_id in self._doc_index:
        #    if len(self._doc_index[self._curr_doc_id]) < 7:
        #        if elem.string.strip() not in self._ignored_words:
        #            self._doc_index[self._curr_doc_id].append(elem.string)

    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()


    # LAB 1 functions to pupulate and return the inverted/resolved indexes
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_inverted_index(self):
		"""Returns a dict() which maps words ids (key) to a list of document ids.
		The list of document ids is stored as a set() data structure. """
		return self._inv_index

    def get_resolved_inverted_index(self):
		"""Returns a dict() which maps word strings (key) to a list of url strings.
		The list of url strings is stored as a set() data structure. """
		return self._resolved_inv_index


    def update_inv_indexes(self, word):
        """Populates the inverted index and the resolved inverted index."""
        if self.word_id(word) not in self._inv_index:
            self._inv_index[self.word_id(word)] = set()
        self._inv_index[self.word_id(word)].add(self._curr_doc_id)

        if word not in self._resolved_inv_index:
            self._resolved_inv_index[word] = set()
        self._resolved_inv_index[word].add(self._curr_url)

    def get_document_index(self):
        """Returns a dict() which maps document ids to stored info about that web page.
        We can store title, short description (like first three lines), etc."""
        doc_index_list = [ [k,v] for k, v in self._doc_index.items() ]
        doc_index_list.sort()
        return doc_index_list

    def get_lexicon(self):
    	"""Returns a list of all the words encountered during crawl."""
    	#return [wordkeys for wordkeys in self._word_id_cache]
    	return self._word_id_cache
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # end of LAB 1 functions


    # The functions below are additional methods in this class that are
    # not required for Lab 1 but may be useful in the future. They are still
    # under development.

    def get_doc_info(self, doc_id):
        """Returns the title and short description of webpage given a documetn id."""
        if doc_id in self._doc_index:
            title = self._doc_index[doc_id][0]
            info = "".join(self._doc_index[doc_id][1:])
        else:
            title = "Error"
            info = "no such document index found."
        return title, info

    def get_doc_cache(self):
        """Caches word to word_id."""
        return self._doc_id_cache

    def get_word_cache(self):
        """Caches url to doc_id."""
        return self._word_id_cache
    
    def get_list_of_links(self):
        """Return the list of link tuples"""
        return list(self._set_of_links)
    
    def get_document_index_dict(self):
        return self._doc_index


if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)
    # Setting ^^^^^ will determine how far to recurse into each new url hyperlink
    # that the crawler encounters. We use 0 to just get the first web page per url.
    
    # LAB 1
    # Testing of the inverted and resolved indexes
    # just print out their values
    #document_index = bot.get_document_index()
    document_index = bot.get_document_index_dict()
    #print "\nDocument Index\n~~~~~~~~~~~~~~\n", document_index
    lexicon = bot.get_lexicon()
    #print "\nLexicon\n~~~~~~~\n", lexicon
    inverted_index = bot.get_inverted_index()
    #print "\nInverted Index\n~~~~~~~~~~~~~~\n", inverted_index
    resolved_inverted_index = bot.get_resolved_inverted_index()
    #print "\nResolved Index\n~~~~~~~~~~~~~~\n", resolved_inverted_index
    
    
    # LAB 3 code
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pagerank_dict = page_rank(bot.get_list_of_links(), num_iterations=20)
    
    # make an upgraded resolved_inverted_index
    # maps word strings to ordered list of tuples
    # tuples = (url string, page title, page rank score)
    word_to_sorted_list_of_urls = { }
    for word, url_set in resolved_inverted_index.items():
        # combine each url with its page rank into a tuple
        # sort that list of tuples by page rank
        # store new sorted list of url tuples into new data structure
        newlist = []
        for a_url in url_set:
            a_url_id = bot.document_id(a_url)
            a_url_rank = pagerank_dict[a_url_id]
            a_url_title = document_index[a_url_id][0]
            newlist.append((a_url, a_url_title, a_url_rank))
        # sort list by the pagerank (second element in tuple)
        newlist.sort(key=lambda tup: tup[2], reverse=True)
        # insert into new dict
        word_to_sorted_list_of_urls[word] = newlist
    
    # persistently store our own data structure
    our_special_db = anydbm.open('searchbot_data.db', 'c')
    for word, url_list in word_to_sorted_list_of_urls.items():
        our_special_db[str(word)] = pickle.dumps(url_list)
        # word is originally in unicode, need to convert to string
    our_special_db.close()
    
    
    # Persistent Storage of Required Data
    # ie. inverted index, lexicon, document index, PageRank scores
    # store in persistent storage (anydbm)
    
    # document index (maps doc_ids to doc title)
    doc_index_db = anydbm.open('searchbot_doc_index.db', 'c')
    for web_id in document_index:
        doc_index_db[str(web_id)] = pickle.dumps(document_index[web_id])
        # word is originally integer, need to convert to string
    doc_index_db.close()
    
    # lexicon (maps words to word_ids)
    lexicon_db = anydbm.open('searchbot_lexicon.db', 'c')
    for keyword in lexicon:
        lexicon_db[str(keyword)] = pickle.dumps(lexicon[keyword])
        # word is originally in unicode, need to convert to string
    lexicon_db.close()
    
    # inverted index (maps word_ids to set of url_ids)
    inv_index_db = anydbm.open('searchbot_inv_index.db', 'c')
    for word_id in inverted_index:
        inv_index_db[str(word_id)] = pickle.dumps(inverted_index[word_id])
        # word is originally integer, need to convert to string
    inv_index_db.close()
    
    # PageRank scores (maps word_ids to score values)
    pagerank_db = anydbm.open('searchbot_pagerank.db', 'c')
    for web_id in pagerank_dict:
        pagerank_db[str(web_id)] = pickle.dumps(pagerank_dict[web_id])
        # word is originally integer, need to convert to string
    pagerank_db.close()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


