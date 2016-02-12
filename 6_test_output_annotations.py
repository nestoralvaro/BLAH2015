# -*- coding: utf-8 -*-
######################################################
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################
#import codecs
from collections import defaultdict
import datetime

from lxml import etree

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
  Creates the dictionary containing all the texts to be annotated.
  The key is the DIV-SOURCE-ID, while the value for such key will be texts to be annotated
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
    # TODO: OLD
    #id = "{0}_{1}_{2}".format(article_id, sourcedb, div_id)
    # TODO: NEW
    id = "{0}_{1}_{2}".format(sourcedb, article_id, div_id)
    sectionsWithText[id] = text
  return sectionsWithText

def outputAnnotations():
  """
  Creates the text files containing the json objects with the annotations (to be uploaded to PubAnnotation)
  """

  # Obtain the text excerpts
  # TODO: these are some tests
  file_with_texts = "file_for_annotator.XML"
  excerpts = createDictContents(file_with_texts)
  file_with_annotations = "mergedAnnotations.txt"
  #print excerpts
  f= open(file_with_annotations, 'r')
  for line in f.xreadlines():
     parts = line.split("\t")
     id = "{0}_{1}_{2}".format(parts[0], parts[1], parts[2])
     #print id
     #print parts
     text = excerpts[id]
     #print text[2:20]
     begin = int(parts[3])
     end = int(parts[4])
     #print int(parts[3]), int(parts[4])
     print text[int(parts[3]):int(parts[4])], parts[5], "\n"
     #, parts[5], "\n"
     #print excerpts[id]
  #listAnnotations(file_with_annotations, excerpts, dictItems_PHENOM)

############
# Main part
############
if __name__ == '__main__':
  initTime = str(datetime.datetime.now())
  outputAnnotations()
  print "Started at  (" + initTime + ")"
  print "Finished at (" + str(datetime.datetime.now()) + ")"
