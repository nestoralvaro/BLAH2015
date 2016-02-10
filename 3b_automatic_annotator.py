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
from nltk import sent_tokenize

REST_URL = "http://data.bioontology.org"
API_KEY = "8b5b7825-538d-40e0-9e9e-5ab9274a9aeb"
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
    try:
        loaded_json = json.loads(opener.open(url).read())
        return loaded_json
    except:
        e = sys.exc_info()[0]
        print "EXCEPTION loading the Json"
        print e
        raise e
        #return []

#If the text is too big, lets split it in parts
def splitIterator(text, size):
    assert size > 0, "size should be > 0"
    begin_position = 0 # place where we start searching for
    end_position = size #the end is the first position until updated (inside while loop)
    while end_position < len(text):
        end_position = begin_position + size # update last position
        match_at = text.rfind(' ', begin_position, end_position)
        #try to look for the next blank after "size", if none is found return "size"
        if match_at > -1:
            end_position = match_at + 1
        yield text[begin_position:end_position]
        begin_position = end_position  # Update next starting position

# This is the real method in charge of performing the requests to NCBO annotator
def get_NCBO_annotation_Request(article_id, sourcedb, div_id, text, timer_min, timer_max, ftw, json_url, offset):
    try:
        annotations = get_json(json_url)
        for result in annotations:
            time.sleep(random.randint(timer_min, timer_max)) #Longer timer to not get blocked by the API
            class_details1 = get_json(result["annotatedClass"]["links"]["self"])
            ontology_full_id =class_details1["@id"]
            ontology_id = ontology_full_id[len(ID_BASE_STRING):]
            prefLabel=class_details1["prefLabel"]
            ontology=class_details1["links"]["ontology"]
            for annotation in result["annotations"]:
                a_from = annotation["from"] + offset
                # It seems the starting offsets are moved 1 position forward
                a_from -= 1
                a_to = annotation["to"] + offset
                a_type = annotation["matchType"]
                # message used in tests
                #print text[a_from:a_to] + "\t" + str(sourcedb) + "\t" + str(article_id) + "\t" + str(div_id) + "\t" + str(a_from) +"\t" + str(a_to) + "\t" + str(ontology_id)  + "\t" + str(prefLabel) + "\n"
                ftw.write(str(sourcedb) + "\t" + str(article_id) + "\t" + str(div_id) + "\t" + str(a_from) +"\t" + str(a_to) + "\t" + str(ontology_id)  + "\t" + str(prefLabel) + "\n")
        # When everything works as expected
        return 0
    except:
        e = sys.exc_info()[0]
        print "EXCEPTION Connection / Formatting issues" #- No annotations to be made by the annotator
        print e
        # Return 1 if something failed
        return 1

# This is a middle layer in charge of issuing the requests to the other method
# This method also handles the possible errors received as response from NCBO annotator
def get_NCBO_annotation(article_id, sourcedb, div_id, text, timer_min, timer_max, ftw, json_url, offset):
    #get_NCBO_annotation_Request(article_id, sourcedb, div_id, text, timer_min, timer_max, ftw, json_url, offset)
    #'''
    result = get_NCBO_annotation_Request(article_id, sourcedb, div_id, text, timer_min, timer_max, ftw, json_url, offset)
    remaining_retries = 10
    #print "Result of the NCBO annotator " + str(result)
    while result == 1 and remaining_retries > 0:
        print "EXCEPTION detected (Retrying)..."
        result = get_NCBO_annotation_Request(article_id, sourcedb, div_id, text, timer_min, timer_max, ftw, json_url, offset)
        # message used in tests
        print "******"
        # message used in tests
        print "::::Result of the NCBO annotator::::"
        print text
        print str(result)
        # Counter to break infinite loops
        remaining_retries -= 1
        #print "remaining_retries " + str(remaining_retries)
        # Add a timeout "just in case" this can fix the problem
        if remaining_retries % 4:
            print "Using the timeout"
            time.sleep(random.randint(8, 12))
    if result == 1:
       print "********* ERROR!!!! NOT ANNOTATED::: article_id: " + article_id + ", sourcedb: " + sourcedb + ", div_id: " + div_id
    return
    #'''

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
        # message used in tests
        print "article_id: " + article_id + ", sourcedb: " + sourcedb + ", div_id: " + div_id
        # message used in tests
        print "LENGTH:: ", len(text)
        max_length = 4000 # 4000 seems to be a good number
        offset = 0
        if len(text) >= max_length: #Avoid passing very long strings
            #parts = sent_tokenize(text) # Maybe too slow
            parts = splitIterator(text, 1500) #1500 is a good hardcoded limit to split if text is too big
            for single_part in parts:
                #print "--------------->", offset #, single_part
                escaped_string = urllib2.quote(single_part.encode('utf-8'))
                get_NCBO_annotation(article_id, sourcedb, div_id, text, 2, 7, ftw, base_ncbo_url + escaped_string, offset)
                offset += len(single_part)
                #offset += 1 # In case of using sent_tokenize (This is slower and can fail in some cases)
        else:
            escaped_string = urllib2.quote(text.encode('utf-8'))
            get_NCBO_annotation(article_id, sourcedb, div_id, text, 1, 2, ftw, base_ncbo_url + escaped_string, offset)
    ftw.close()
    f.close()
    return

# Iterates over the whole file to annotate all the sentences using a dictionary
def annotate_with_dictionary(file_in, file_out, dictionary):
    punctuation_mark = "[,.:;'\" \?\(\)\[\]!\n]+" # This is the list of allowed puntuation marks
    f= codecs.open(file_in, 'r', 'utf-8')
    ftw= open(file_out,'w')
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
    # TODO: These are test files:
    #file_to_read = "file_for_annotator_TEST_2016_.XML"
    #file_to_read = "file_for_annotator_TEST_2016_short.XML"
    #file_to_read = "file_for_annotator_TEST_2016_short_2.XML"
    #file_to_read = "file_for_annotator_TMP.XML"

    # TODO: I read the file name from the command line
    #file_to_read = "file_for_annotator.XML"
    file_to_read = str(sys.argv[1])

    output_folder = "parts_output/"
    # TODO: Use this part to annotate using NCBO
    file_to_write_name = file_to_read[file_to_read.rfind("/") + 1:]
    file_to_write = output_folder + file_to_write_name + ".CHEBI_PATO.out_2016_02_10_test.txt"
    ftw = open(file_to_write,'w').close()
    ontologies = "PATO,CHEBI" # enter NCBO ontologies here, separated by comma
    #ontologies = "CHEBI" # enter NCBO ontologies here, separated by comma
    # First of all come the annotations done by NCBO annotator
    annotate_with_NCBO_annotator(file_to_read, file_to_write, ontologies)

    '''
    # TODO: Use this part to annotate using our dictionaries
    dictionaries = ["PHENOM-dic.tsv", "PATIENT-dic.tsv"] # List of dictionaries to be used
    # Then, we use the dictionaries to annotate the articles
    for dictionary in dictionaries:
      #print "Annotating with dictionary " + str(dictionary)
      dict_file_name = file_to_read + "_dict_" + dictionary + ".txt"
      annotate_with_dictionary(file_to_read, dict_file_name, dictionary)
      #print dict_file_name
    print "Automatic annotation ended"
    '''
