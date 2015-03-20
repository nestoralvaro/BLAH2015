# -*- coding: utf-8 -*-
######################################################
# We use this approach instead of SRL because
# - The matched patters are the same in case of simple regular expressions
# - We only need to identify the matching sentences, not to annotate these
# - SRL processes some punctuation marks inconsistently (adds extra blank spaces in some cases)
# - The python code runs at the same speed (in most cases even faster) than SRL
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################
import requests, json, re

PATIENTS_FILE = "PATIENT-dic.tsv" # file containing the patients dictionary
PUBANNOTATION_PROJECT_BASE_URL = "http://pubannotation.org/projects/" # Base pubannotation URL
PROJECT_NAME = "BLAH2015_Annotations_drugs" # Pubannotation project
PUBMEDCENTRAL_SOURCE = "PMC" # String used in the case of PubMed Central articles
PUBMED_PUBANNOTATION = "PubMed" # String used by Pubannotation in PubMed articles
FILE_FOR_ANNOTATOR = "file_for_annotator.XML" # Name of the file that will be produced

# Escapes XML angle brackets
def escape(s):
	s = s.replace("&", "&amp;")
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	return s

# Creates a patients dictionary using the external dictionary file
def create_patients_dictionary():
	f= open(PATIENTS_FILE, 'r')
	patients = []
	for line in f.xreadlines():
		tab_pos = line.find('\t')
		patient = line[tab_pos:]
		patient = patient.strip()
		patients.append(patient)
	f.close()
	return patients
		
# Apply a simple regex to check if any of the patient descriptors is matched
def is_patient_descriptor_line(s, people):
	punctuation_mark = "[,.:;'\" \?\(\)\[\]!\n]+" # This is the list of allowed puntuation marks
	p = 0
	match = ""
	while (p < len(people)) and (match == ""):
		search_string = punctuation_mark + people[p] + punctuation_mark
		regexp = re.compile(search_string, re.IGNORECASE) # The search is case insensitive
		if regexp.search(s) is not None:
	  		match = people[p]
		p = p+1
	return match

# Retrieves the JSON contents in the received URL
# Process these contents and stores in ftw the lines containing a patient descriptor
def process_json_information(sourceid, sourcedb, division, url, ftw):
	# get the contents of the div
	url_response = requests.get(url)
	url_data = json.loads(url_response.text)
	# ?
	url_data_text = url_data["text"]
	patient_descriptor_match = is_patient_descriptor_line(url_data_text, patients_dictionary)
	if (patient_descriptor_match is not ""):
		print patient_descriptor_match + " -> " + url
		line_to_annotate = "<node>"
		line_to_annotate += "<id>" + sourceid + "</id>"
		line_to_annotate += "<sourcedb>" + sourcedb + "</sourcedb>"
		line_to_annotate += "<div_id>" + str(division) + "</div_id>"
		line_to_annotate += "<text>" + escape(url_data_text) + "</text>"
		line_to_annotate += "</node>\n"
		line_utf_8 = line_to_annotate.encode('UTF-8')
		ftw.write(line_utf_8)
	return

# Gets the list of articles (and sections within the articles) containing patient descriptors
def get_pubannotation_list_of_articles_in_project(patients_dictionary):
	# Retrieve the list of documents in the project
	project_url = PUBANNOTATION_PROJECT_BASE_URL + PROJECT_NAME + "/docs.json"
	response = requests.get(project_url)
	json_data = json.loads(response.text)
	ftw = open(str(FILE_FOR_ANNOTATOR),'w')
	# Create XML root node
	ftw.write("<document>\n")
#	print project_url
	# iterate over each document
	for i in range(len(json_data)):
		line = json_data[i]
		article_sourcedb = line["sourcedb"]
		article_sourceid = line["sourceid"]
		# Build the URL of each document within the project
		base_annotation_url = PUBANNOTATION_PROJECT_BASE_URL + PROJECT_NAME + "/docs/sourcedb/" + article_sourcedb + "/sourceid/" + article_sourceid
		divs_url_json = ""
		if (article_sourcedb == PUBMED_PUBANNOTATION):
			url_contents_pubmed = base_annotation_url + "/annotations.json"
			process_json_information(article_sourceid, article_sourcedb, 0, url_contents_pubmed, ftw)
		elif (article_sourcedb == PUBMEDCENTRAL_SOURCE):
			divs_url_json = base_annotation_url + "/divs" + ".json"
			divs_response = requests.get(divs_url_json)
			divs_json_data = json.loads(divs_response.text)
			for j in range(len(divs_json_data)):
				url_contents_pmc = base_annotation_url + "/divs/" + str(j) + "/annotations.json"
				process_json_information(article_sourceid, article_sourcedb, j, url_contents_pmc, ftw)
		else:
			print "This is not a valid article"
	# Close XML root node
	ftw.write("</document>")
	ftw.close()
	return
	
################
# Main part
################
if __name__ == '__main__':
	patients_dictionary = create_patients_dictionary()
	get_pubannotation_list_of_articles_in_project(patients_dictionary)
	print "Article processing ended"
