# -*- coding: utf-8 -*-
######################################################
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################

from collections import defaultdict
import datetime

def readToDictionary(listFiles):
  """
  Opens a number of files and stores all the annotations in a dictionary
  """
  #dictWithAnnotations = {}
  dictWithAnnotations = defaultdict(list)
  for annotatedFile in listFiles:
    # Add all the annotations in the file (one per line) to the dictionary
    #PubMed	10027339	0
    f= open(annotatedFile, 'r')
    lines = f.readlines()
    for l in lines:
      parts = l.split("\t")
      source_db = parts[0]
      source_id = parts[1]
      source_div = parts[2]
      # Store using the Article-Div identifier
      identifier = "{0}_{1}_{2}".format(source_db, source_id, source_div)
      dictWithAnnotations[identifier].append(l)
    f.close()
  return dictWithAnnotations

def mergeAnnotations(listFiles, targetFile):
  """
  Receives a number of files and merges all the annotations into a new file
  """
  dictWithAnnotations = readToDictionary(listFiles)
  ftw = open(targetFile,'w').close()
  ftw= open(targetFile,'w')
  for key,vals in dictWithAnnotations.items():
     for val in vals:
       # The annotations for the same Article-Div will be listed together
       ftw.write(val)
  ftw.close()
  print len(dictWithAnnotations)

############
# Main part
############
if __name__ == '__main__':
  initTime = str(datetime.datetime.now())
  listFiles = ["file_for_annotator.XML_dict_PHENOM-dic.tsv.txt", "file_for_annotator.XML.CHEBI_PATO.out_2016_02_08_test.txt"]
  
  targetFile = "mergedAnnotations.txt"
  mergeAnnotations(listFiles, targetFile)
  print "Started at  (" + initTime + ")"
  print "Finished at (" + str(datetime.datetime.now()) + ")"
