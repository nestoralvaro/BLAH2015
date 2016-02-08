# -*- coding: utf-8 -*-
######################################################
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################
import codecs
from collections import defaultdict
import datetime
import urllib2
import json
import sys
import time
import random
import os
import csv
import re
from lxml import etree

PUNCTUATION_MARK = "[,.:;'\" \?\(\)\[\]!\n]+" # This is the list of allowed puntuation marks


def loadDictDenotations(text, dictItems, denotations_counter):
  """
  Annotates the text using the items from the dictionary
  """
  denotations = []
  # Iterate over all the items in the dictionary
  for key, val in dictItems.iteritems():
    # print key, val
    current_string = val
    # Add the punctuation mark delimiters
    search_string = PUNCTUATION_MARK + current_string + PUNCTUATION_MARK
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
      span = {}
      span["begin"] = match_start
      span["end"] = match_end
      denotation = {}
      denotation["span"] = span
      denotation["obj"] = key
      denotations_counter += 1
      denotation["id"] = "T" + str(denotations_counter)
      #print "===>", text[match_start:match_end]
      denotations.append(denotation)
  return denotations

def isOKBoundary(oldAnnotation, newAnnotation, text):
  """
  Checks if two annotations are cross-boundaries.
  If the annotation are *NOT* cross-boundaries (the annotations are OK)
    the result will be *TRUE*
  This method also detects when the annotation includes "CROSS-BORDER"
  """
  result = False
  if ((oldAnnotation['end'] <= newAnnotation['begin']) \
    or (newAnnotation['end'] <= oldAnnotation['begin']) \
    or ((newAnnotation['begin'] >= oldAnnotation['begin']) and (newAnnotation['end'] <= oldAnnotation['end'])) ):
    result = True
  return result

def isStorableDenotation(denotations, denotation, text, info):
  """
  Returns TRUE if the new denotation is NOT cross Boundary,
    i.e. TRUE when the annotations are not sharing spans
  """
  result = True
  newDenotationSpan = denotation['span']
  for d in denotations:
    # If there is any problem I will discard the annotation
    if ((text.find("\\n") != -1) or \
      (text.find("\\b") != -1) or \
      (text.find(" ") != -1) or \
      (text.find("\\t") != -1) or \
      (not isOKBoundary(d['span'], newDenotationSpan, text))):
      result = False
      break
  # TODO: The next lines are printed when there is a cross-boundary annotation
  '''
  if not result:
    print "STORE denotation?", result, info
    print denotations
    print denotation
    print "*****"
  '''
  return result

def createJsonObject(file_with_annotations, excerpts, dictItems_PHENOM):
  """
  Create the Json Object
  This is the produced format:
    {"text": "This is a sample text.....",
    "sourcedb": "PMC",
    "sourceid": "12345",
    "divid": 0,
    "denotations": [
      {"id": "T1", "span": {"begin": 9, "end": 19}, "obj": "CHEBI_23888"},
      {"id": "T2", "span": {"begin": 14, "end": 16}, "obj": "CHEBI_23888"}
      ]
    }
  """
  #print "Creating the Json objects..."
  # Obtain the offsets for the annotations
  f= open(file_with_annotations, 'r')
  file_with_json_objects = "json_output"
  prevSourcedb = ""
  prevSourceid = ""
  prevDivid = ""
  data = {}
  denotation = {}
  denotations = []
  denotations_counter = 1
  json_files = 0


  # TODO: remove these 2 variables
  ready = False
  activateContinue = False
  # END TODO


  for line in f.xreadlines():
    list = line.split("\t")
    sourcedb = list[0]
    sourceid = list[1]
    divid = list[2]

    '''
    # TODO: This is just for one test
    if (sourcedb != "PMC") and (sourceid != "149431"):
      activateContinue = True
    if (sourceid == "149431") and (divid == "4"):
      activateContinue = False
      ready = True
    if activateContinue:
      continue
    # END TODO
    '''


    span_begin = list[3]
    # span_end = str(int(list[4]) + 1) # add one more
    span_end = list[4]
    # obj_name = list[5] + ":" + str(list[6]).rstrip()
    obj_name = list[5]
    # Check if I should create a new json object
    # Here I have to reuse the same Json object
    if ((prevSourcedb == sourcedb) and (prevSourceid == sourceid) and (prevDivid == divid)):
      # Keep loading the same json object
      #print "Same"
      denotations_counter += 1
    # In this case I create a new Json object
    else:
      # Skip the initial element (it is empty)
      if prevSourceid != "":
        # I will generate a new JSON file
        json_files += 1
        #print "******",prevSourceid, prevSourcedb, prevDivid
        # First of all create the corresponding Json object with the **already stored data**
        id = "{0}_{1}_{2}".format(prevSourcedb, prevSourceid, prevDivid)
        print id
        data['text'] = excerpts[id]
        # Load the denotations using the dictionaries (Do once with each dictionary)
        phenom_denotations = loadDictDenotations(excerpts[id], dictItems_PHENOM, denotations_counter)
        denotations = denotations + phenom_denotations
        # Put the denotations in the Json object
        data['denotations'] = denotations
        # In case these 2 fields are needed in the json object, create them
        # data['relations'] = []
        # data['modifications'] = []
        # Create the final Json object
        json_data = json.dumps(data)
        #if (prevSourceid == "117131" and prevSourcedb == "PMC" and  prevDivid == "3"):
        #  print json_data
        # Save it to a file
        file_name = "{0}-{1}-div-{2}.json".format(prevSourcedb, prevSourceid, prevDivid)
        # TODO: comment the next 3 lines when testing
        ftw= open(file_with_json_objects + "/" + file_name,'w')
        ftw.write(json_data)
        ftw.close()

      # Reset the stored values
      prevSourcedb = sourcedb
      prevSourceid = sourceid
      prevDivid = divid
      # Create the object if it doesn't exist yet (new Json object)
      data = {}
      denotations = []
      denotations_counter = 1
      data['sourcedb'] = sourcedb
      data['sourceid'] = sourceid
      data['divid'] = divid
    denotation = {}
    denotation["id"] = "T" + str(denotations_counter)
    #  The span will always be a new one
    span = {}
    span["begin"] = span_begin
    span["end"] = span_end
    denotation["span"] = span
    denotation["obj"] = obj_name
    textForAnnotation = (excerpts["{0}_{1}_{2}".format(prevSourcedb, prevSourceid, prevDivid)])[int(span_begin):int(span_end)]
    #textForAnnotation = excerpts["{0}_{1}_{2}".format(prevSourcedb, prevSourceid, prevDivid)]
    #textForAnnotation = textForAnnotation[int(span_begin):intspan_end]
    #print span_begin, type(span_end)
    # Check if the annotation is correct or wrong (so we discard it)
    if isStorableDenotation(denotations, denotation, textForAnnotation, sourcedb + "_" + sourceid + "_" + divid):
      denotations.append(denotation)
      #print "OK", textForAnnotation, denotation

    # TODO: Remove when producing the final result
    #if json_files == 6:
    #  break
  f.close()
  return

def loadDictItems(file_with_dict):
  """
  Loads the dictionary
  """
  itemsDictionary = defaultdict()
  with open(file_with_dict, 'rb') as tsv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    for row in tsv_reader:
      itemsDictionary[row[0]] = row[1]
  return itemsDictionary

def unescape(s):
  """
  Unescapes XML angle brackets
  """
  s = s.replace("&lt;", "<")
  s = s.replace("&gt;", ">")
  s = s.replace("&amp;", "&")
  return s

def createDictContents(file_with_texts):
  """
  Iterates over the whole file to annotate all the sentences with NCBO annotator
  """
  #print "Creating the dictionary with the text excerpts..."
  sectionsWithText = defaultdict()
  xml_tree = etree.parse(file_with_texts)
  root = xml_tree.getroot()
  xml_nodes = root.findall('node')
  for node in xml_nodes:
    article_id  = node.findtext('id')
    sourcedb = node.findtext('sourcedb')
    div_id = node.findtext('div_id')
    text = unescape(node.findtext('text'))
    id = "{0}_{1}_{2}".format(sourcedb, article_id, div_id)
    sectionsWithText[id] = text
  return sectionsWithText

def createJsonWithOffsets():
  """
  Creates the text files containing the json objects with the annotations (to be uploaded to PubAnnotation)
  """

  # Obtain the text excerpts
  file_with_texts = "file_for_annotator.XML"
  excerpts = createDictContents(file_with_texts)
  #print excerpts
  # print len(excerpts)
  file_with_dict_PHENOM = "PHENOM-dic.tsv"
  dictItems_PHENOM = loadDictItems(file_with_dict_PHENOM)

  # Create the json objects
  #file_with_annotations = "CSISV34/file_for_annotator.XML.NEW__CHEBI.out_2015_06_23.txt"
  file_with_annotations = "mergedAnnotations.txt"
  createJsonObject(file_with_annotations, excerpts, dictItems_PHENOM)

############
# Main part
############
if __name__ == '__main__':
  initTime = str(datetime.datetime.now())
  createJsonWithOffsets()
  print "Started at  (" + initTime + ")"
  print "Finished at (" + str(datetime.datetime.now()) + ")"

  # After the program runs (and produces the JSON files with the annotations), we
  #   create the TAR.GZ file using the following command:
  # tar -cvzf annotations.tar.gz json_output/

  
