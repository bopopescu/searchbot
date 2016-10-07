To run the back end:
		1. cd into the <backend> directory
		2. check that there is a test case in the file urls.txt
				(change the test case here; our own tests are presented below)
		3. run our modified crawler from the command line using python:
				"python crawler.py"
		4. the output will be printed out to the terminal, and it includes:
				- document title, num words, url, for each line in urls.txt
				- document index (contains document ids and titles)
				- lexicon
				- inverted index
				- resolved (inverted) index



Sample tests used to verify correctness of crawler:

Note1: To run the desired test case, rename the corresponding file to "urls.txt"
Note2: We have changed the depth of the crawl function to depth=0 so that the
      outputs are of a manageable size and can be easier interpreted. Testing
      with larger depths was also done, by simply changing the parameter.

urls.txt - Test proper output format with simple webpage

	Check that the inverted index format is a dictionary { } of numbers mapping
	to a set of numbers and the resolved index format is a dict of strings 
	mapping to a set of strings.

urls2.txt - Test mapping of the same word to multiple urls

	Take the word 'google' for example. It is usually the first result in the
	resolved inverted index. We can see that it maps to all three google pages
	as they are listed in the same set and that shows our inverted linking was
	successful.

urls3.txt - Testing large random web page inputs

	The crawler can handle large inputs of text successfully and output all the
	data structures we have filled. You may need to do a lot of scrolling to 
	get to the top of the output. Also, the wikipedia page is randomized.

