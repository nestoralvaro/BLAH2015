# -*- coding: utf-8 -*-
######################################################
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################
import urllib2, requests, json

# Create your pubannotation account to fill the credentials http://pubannotation.org/
PUBANNOTATION_USERNAME = "" # Your pubannotation user name
PUBANNOTATION_PASSWORD = "" # Your pubannotation password
PUBANNOTATION_PROJECT = "BLAH2015_Annotations_drugs" # Your pubannotation project

# Returns the already uploaded annotations
def get_previous_annotations(target):
	response = requests.get(target + "/annotations.json")
	json_data = json.loads(response.text)
	stored_data = {}
	denotations = []
	if "denotations" in json_data:
		denotations = json_data["denotations"]
	if "text" in json_data:
		text = json_data["text"]
	stored_data["denotations"] = denotations
	stored_data["text"] = text
	return stored_data

# needed to decode json data (http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python#13105359)
def byteify(input):
	if isinstance(input, dict):
		return {byteify(key):byteify(value) for key,value in input.iteritems()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input
        	
# Creates the json object containing the annotations
def create_json_annotation(target, sourcedb, sourceid, divid, span_begin, span_end, obj_name):
	data = {}
	data['target'] = target
	data['sourcedb'] = sourcedb
	data['sourceid'] = sourceid
	data['divid'] = divid
	data['project'] = PUBANNOTATION_PROJECT
	# Denotations
	denotations = []
	retrieved_data = get_previous_annotations(target)
	previous_annotations = retrieved_data["denotations"]
	data['text'] = retrieved_data["text"] + "TESSST"
	denotations_counter = 1
	for i in range(len(previous_annotations)):
		# Check if the same annotation is already stored
		if (previous_annotations[i]["obj"] == obj_name) and (str(previous_annotations[i]["span"]["begin"]) == str(span_begin)) and (str(previous_annotations[i]["span"]["end"]) == str(span_end)):
			# Don't store a repeated annotation
			print "***** ANNOTATION ALREADY STORED :-)"
			return ""
		else:
			denotations.append(byteify(previous_annotations[i]))
			denotations_counter += 1
	denotation = {}
	denotation["id"] = "T" + str(denotations_counter)
	#	Span
	span = {}
	span["begin"] = span_begin
	span["end"] = span_end
	denotation["span"] = span
	denotation["obj"] = obj_name
	denotations.append(denotation)
	# End denotations
	data['denotations'] = denotations
	data['relations'] = []
	data['modifications'] = []
	json_data = json.dumps(data)
	return json_data

# Gets the list of articles and stores them in pubannotation
def store_json_annotation_in_pubannotation(file_to_read):
	f= open(file_to_read, 'r')
	headers = {'content-type': 'application/json', 'Accept': 'text/plain'}
	pubannotation_base_article_url = "http://pubannotation.org/projects/" + PUBANNOTATION_PROJECT
	pubannotation_add_article_url = pubannotation_base_article_url + "/annotations.json"
	lines_counter = 1
	for line in f.xreadlines():
		list = line.split("\t")
		sourcedb = list[0]
		sourceid = list[1]
		divid = list[2]
		span_begin = list[3]
		# span_end = str(int(list[4]) + 1) # add one more
		span_end = list[4]
		# obj_name = list[5] + ":" + str(list[6]).rstrip()
		obj_name = list[5]
		target = pubannotation_base_article_url + "/docs/sourcedb/" + sourcedb + "/sourceid/" + sourceid + "/divs/" + str(divid)
		pubannotation_json_url = target + "/annotations.json"
		json_content = create_json_annotation(target, sourcedb, sourceid, divid, span_begin, span_end, obj_name)
		print "processing: " + str(lines_counter) + " -> " + line
		if (len(json_content) > 0):
			r = requests.post(pubannotation_add_article_url, json_content, auth=(PUBANNOTATION_USERNAME, PUBANNOTATION_PASSWORD), headers=headers)
			print "Json upload resulted in: " + str(r.json)
		else:
			print "Nothing to annotate"
		lines_counter += 1
	f.close()
	return


################
# Main part
################
if __name__ == '__main__':
	file_to_read = "file_for_annotator.XML.out.txt"
	store_json_annotation_in_pubannotation(file_to_read)
	print "Annotations upload ended"
