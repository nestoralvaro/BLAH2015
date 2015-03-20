# -*- coding: utf-8 -*-
######################################################
# Based on Juan M. Banda's code (https://github.com/jmbanda/BLAH2015/blob/master/NCBOannotate.py)
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################
import codecs
import urllib2
import json
import sys
import time
import random
import os
import csv
import re
from lxml import etree
  
REST_URL = "http://data.bioontology.org"
API_KEY = "" #Replace with your own API key from Bioportal
ID_BASE_STRING = "http://purl.obolibrary.org/obo/"

# Unescapes XML angle brackets
def unescape(s):
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	s = s.replace("&amp;", "&")
	return s
	
#Functions to get bioportal results
def get_json(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())

#If the text is too big, lets split it in parts 
def splitIterator(text, size):
    assert size > 0, "size should be > 0"
    for start in xrange(0, len(text), size):
        yield text[start:start + size]

# Gets the annotation for an article from NCBO annotator
def get_NCBO_annotation(article_id, sourcedb, div_id, text, timer_min, timer_max, ftw, json_url):
	annotations = get_json(json_url)
	for result in annotations:
		time.sleep(random.randint(timer_min, timer_max)) #Longer timer to not get blocked by the API
		try:
			class_details1 = get_json(result["annotatedClass"]["links"]["self"])
			ontology_full_id =class_details1["@id"]
			ontology_id = ontology_full_id[len(ID_BASE_STRING):]
			prefLabel=class_details1["prefLabel"]
			ontology=class_details1["links"]["ontology"]
			for annotation in result["annotations"]:
				a_from = annotation["from"]
				# It seems the starting offsets are moved 1 position forward
				a_from -= 1
				a_to = annotation["to"]
				a_type = annotation["matchType"]
				ftw.write(str(sourcedb) + "\t" + str(article_id) + "\t" + str(div_id) + "\t" + str(a_from) +"\t" + str(a_to) + "\t" + str(ontology_id)  + "\t" + str(prefLabel) + "\n")
		except:
			print "Connection / Formatting issues" #- No annotations to be made by the annotator
	return

# Iterates over the whole file to annotate all the sentences with NCBO annotator
def annotate_with_NCBO_annotator(file_in, file_out, ontologies):
	print "Starting NCBO annotation..."
	f= open(file_in, 'r')
	ftw= open(file_out,'a')
	base_ncbo_url = REST_URL + "/annotator?ontologies=" + ontologies + "&longest_only=true&text="
	xml_tree = etree.parse(file_in)
	root = xml_tree.getroot()
	xml_nodes = root.findall('node')
	for node in xml_nodes:
		article_id  = node.findtext('id')
		sourcedb = node.findtext('sourcedb')
		div_id = node.findtext('div_id')
		text = unescape(node.findtext('text'))
		if len(text) >= 4000: #Avoid passing very long strings
			splits=int(len(text)/1500) #1500 is a good hardcoded limit to split if text is too big
			parts=splitIterator(text, 1500)
			for single_part in parts:
				time.sleep(random.randint(1, 2)) #This timer is needed or the NCBO api will time you out
				escaped_string = urllib2.quote(single_part.encode('utf-8'))
				get_NCBO_annotation(article_id, sourcedb, div_id, text, 2, 7, ftw, base_ncbo_url + escaped_string)
		else:
			escaped_string = urllib2.quote(text.encode('utf-8'))
			get_NCBO_annotation(article_id, sourcedb, div_id, text, 1, 2, ftw, base_ncbo_url + escaped_string)
	ftw.close()
	f.close()
	return

# Iterates over the whole file to annotate all the sentences using a dictionary
def annotate_with_dictionary(file_in, file_out, dictionary):
	punctuation_mark = "[,.:;'\" \?\(\)\[\]!\n]+" # This is the list of allowed puntuation marks
	f= codecs.open(file_in, 'r', 'utf-8')
	ftw= open(file_out,'a')
	# New
	xml_tree = etree.parse(file_in)
	root = xml_tree.getroot()
	xml_nodes = root.findall('node')
	for node in xml_nodes:
		article_id  = node.findtext('id')
		sourcedb = node.findtext('sourcedb')
		div_id = node.findtext('div_id')
		text = unescape(node.findtext('text'))
		#Lets parse the text between the abstractText column
		with open(dictionary, 'rb') as tsv_file:
			tsv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in tsv_reader:
				current_string = str(row[1])
				# Add the punctuation mark delimiters
				search_string = punctuation_mark + current_string + punctuation_mark
				# Compile the regexp to match any casing 
				regexp = re.compile(search_string, re.IGNORECASE) # The search is case insensitive
				for m in re.finditer(regexp, text):
					match_start = m.start()
					match_end = m.end()
					# Now that I have the substring, match the main string within it
					sub_regexp = re.compile(current_string, re.IGNORECASE)
					substring = text[match_start:match_end]
					sub_match = re.search(sub_regexp, substring)
					sub_start = sub_match.start()
					sub_end = sub_match.end()
					# recalculate the starting offset
					match_start = match_start + sub_start
					# recalculate the ending offset
					match_end = match_end - (len(substring) - sub_end)
					ftw.write(sourcedb + "\t" + article_id + "\t" + div_id + "\t" +  str(match_start) + "\t" + str(match_end) + "\t" + row[0] + "\t" + str(row[1]) + "\n")
	ftw.close()
	f.close()
	return


############
# Main part
############
if __name__ == '__main__':
	file_to_read = "file_for_annotator.XML"
	file_to_write = str(file_to_read) + ".out.txt"
	ftw = open(file_to_write,'w').close()
	ontologies = "PATO,CHEBI" # enter NCBO ontologies here, separated by comma
	# First of all come the annotations done by NCBO annotator
	annotate_with_NCBO_annotator(file_to_read, file_to_write, ontologies)
	dictionaries = ["PHENOM-dic.tsv", "PATIENT-dic.tsv"] # List of dictionaries to be used
	# Then, we use the dictionaries to annotate the articles
	for dictionary in dictionaries:
		print "Annotating with dictionary " + str(dictionary)
		annotate_with_dictionary(file_to_read, file_to_write, dictionary)
	print "Automatic annotation ended"
