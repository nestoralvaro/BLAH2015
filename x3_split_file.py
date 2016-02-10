# -*- coding: utf-8 -*-
######################################################
# Based on Juan M. Banda's code (https://github.com/jmbanda/BLAH2015/blob/master/NCBOannotate.py)
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################
from lxml import etree
import math

# Escapes XML angle brackets
def escape(s):
	s = s.replace("&", "&amp;")
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	return s

def showNodeInfo(node):
  article_id  = node.findtext('id')
  sourcedb = node.findtext('sourcedb')
  div_id = node.findtext('div_id')
  text = node.findtext('text')
  text = escape(text.encode("UTF-8"))
  nodeInfo = "<node><id>{0}</id><sourcedb>{1}</sourcedb><div_id>{2}</div_id><text>{3}</text></node>\n".format(article_id, sourcedb, div_id, text)
  return nodeInfo

def create_sub_files(file_in, num_parts, parts_folder):
  print "Splitting big file into parts..."
  xml_tree = etree.parse(file_in)
  root = xml_tree.getroot()
  xml_nodes = root.findall('node')
  total_nodes = len(xml_nodes)
  nodes_per_part = int(math.ceil(total_nodes / num_parts))
  node_count = 0
  # Iterate to create "num_parts" files
  for file_num in range(0, int(num_parts)):
    print file_num
    file_name_part = parts_folder + file_in + "_part_" + str(file_num)
    ftw= open(file_name_part,'a')
    # This is the first line in each file:
    ftw.write("<document>\n")
    # Iterate to store "nodes_per_part" nodes in each file
    for node_num in range(0, nodes_per_part):
      # Exit the loop
      if node_count >= total_nodes:
        break
      ftw.write(showNodeInfo(xml_nodes[node_count]))
      ftw.write("\n")
      # ready to retrieve the next node
      node_count += 1

    # This is the last line in each file:
    ftw.write("</document>")
    ftw.close()
  return


############
# Main part
############
if __name__ == '__main__':
  file_to_read = "file_for_annotator.XML"
  num_parts = 60.0
  parts_folder = "file_part/"
  create_sub_files(file_to_read, num_parts, parts_folder)
