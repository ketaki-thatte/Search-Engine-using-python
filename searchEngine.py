"""
Name: Ketaki Thatte
CWID: 10419625
"""

"""
Descrption: Search engine using Inverted Index for documents.
It asks you to enter a search query, and then returns all documents
matching the query, in decreasing order of similarity.
"""

from nltk.tokenize import RegexpTokenizer
from collections import defaultdict
from functools import reduce
import math
from nltk.corpus import stopwords
from prettytable import PrettyTable
import re
import os
import pycurl
from io import BytesIO
from xml.etree import cElementTree as ET

# I have use a corpus of documents. Each document has an id, and these are the keys in the following dict.  The values are the
# corresponding filenames.

# /***** Start Content Reading from all files **************/
def ReadWebContent():
	c = pycurl.Curl()
	# Reading File Content.
	f = open('syllabus-links.txt', "r")

	output=f.readline()
	filecounter=1

	while output:
	    buffer = BytesIO()
	    output=output.strip()
	    c.setopt(c.URL,output)
	    c.setopt(c.WRITEDATA, buffer)
	    c.perform()
	    body = buffer.getvalue()
	    xmlstr = body.decode("iso-8859-1")
	    root = ET.fromstring(xmlstr)
	    # Create Text files from XML Syllabus Files
	    fileName = output.split("/")[-1].split('syl.xml')[0] + '.rtf'
	    fp=open(fileName,"a")
	    for course_name in list(root):
	        # Taking Course Name
	        course = course_name.text
	        fp.write(course)
	        
	    for weeks in list(root):
	        topics=weeks.findall("week")
	        for i in topics:
	            topictext=i.find("topics")
	            # Writing the content of the course 
	            fp.writelines(topictext.text)
	    fp.close()
	    filecounter+=1
	    output=f.readline()
	c.close()

# /***** Done Content Reading from all files **************/

filesList = [f for f in os.listdir('C:/Users/Ketaki/Documents/CS-600/Project') if f.endswith('.rtf')]
corpus_files = {}
courpusCounter = 0
for fCounter in filesList:
 corpus_files[courpusCounter]= fCounter
 courpusCounter+=1


N = len(corpus_files)
# dictionary: a set to contain all terms (i.e., words) in the document corpus.
dictionary = set()
tokenizer = RegexpTokenizer(r'\w+')

# postings: a defaultdict whose keys are terms, and whose  corresponding values are the so-called "postings list" for that
# term, i.e., the list of documents the term appears in.

postings = defaultdict(dict)

# document_frequency: a defaultdict whose keys are terms, with corresponding values equal to the number of documents which contain key
document_frequency = defaultdict(int)

# length: a defaultdict whose keys are document ids, with values equal
# to the Euclidean length of the corresponding document vector.
length = defaultdict(float)

# The list of characters (mostly, punctuation) we want to strip out of
# terms in the document.
characters = " .,!#$%^&*();:\n\t\\\"?!{}[]<>"

def main():
	ReadWebContent()
	initialize_terms_and_postings()
	initialize_document_frequencies()
	initialize_lengths()
	while True:
		do_search()


def initialize_terms_and_postings():
    """Reads in each document in corpus_files, splits it into a list of terms (i.e., tokenizes it), 
    adds new terms to the global dictionary, and adds the document to the posting list for each
    term, with value equal to the frequency of the term in the
    document."""
    global dictionary, postings
    stop_words= set(stopwords.words('english'))

    for id in corpus_files:
        f = open(corpus_files[id],'r')
        document = f.read()
        f.close()
        
        terms = tokenize(document)    
        stopped_tokens = [i for i in terms if not i in stop_words]
       
        unique_terms = set(stopped_tokens)
        dictionary = dictionary.union(unique_terms)
        for term in unique_terms:
           
            postings[term][id] = terms.count(term) # the value is the frequency of the term in the document

        #print(postings)
			                                                                                      
def tokenize(document):
    terms = document.lower().split()
    return [term.strip(characters) for term in terms]

def initialize_document_frequencies():
    global document_frequency
    for term in dictionary:
        document_frequency[term] = len(postings[term])

def initialize_lengths():
    """Computes the length for each document."""
    global length
    for id in corpus_files:
        l = 0
        for term in dictionary:
            l += imp(term,id)**2
        length[id] = math.sqrt(l)

def imp(term,id):
    """Returns the importance of term in document id.  If the term isn't in the document, then return 0."""
    if id in postings[term]:
        return postings[term][id]*inverse_document_frequency(term)
    else:
        return 0.0

def inverse_document_frequency(term):
    """Returns the inverse document frequency of term.  Note that if term isn't in the dictionary then it returns 0, by convention."""
    if term in dictionary:
    	if document_frequency[term] != 0 :
    		return math.log(N/document_frequency[term],2)
    	else:
        	return 0.0
    else:
        return 0.0

def do_search():
    t = PrettyTable(['Similarity Score', 'FileName'])
    query = tokenize((input("Enter Your Query:  ")))
    u_query= set(query)
    
    if u_query == (" "):
        sys.exit()

    result_doc_id = set()
    result_doc_id = intersection(
            [set(postings[term].keys()) for term in u_query])
    if not result_doc_id:
        print ("No documents matched all query terms.")
    else:
        scores = sorted([(id,similarity(u_query,id))
                         for id in result_doc_id],
                        key=lambda x: x[1],
                        reverse=True)
        for (id,score) in scores:
        	t.add_row([str(score), corpus_files[id].strip('.rtf')])
        print(t)

def intersection(sets):
    """Returns the intersection of all sets in the list sets."""
    return reduce(set.union, [s for s in sets])

def similarity(query,id):
    """Returns the cosine similarity between query and document id."""
    similarity = 0.0
    for term in query:
        if term in dictionary:
            similarity += inverse_document_frequency(term)*imp(term,id)
    if length[id] != 0:
    	similarity = similarity / length[id]
    return similarity

if __name__ == "__main__":
    main()
