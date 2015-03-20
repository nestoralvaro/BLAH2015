# -*- coding: utf-8 -*-
######################################################
# @author: nestoralvaro
# Developed for BLAH 2015
######################################################
import urllib2, requests, json

EPMC_PAGE_SIZE = 25 # Page size defined by Europe PMC
ARTICLE_END = "</result>" # Tag denoting the end of each article
PM_ID_TAG = "pmid" # name of the tag containing the ID for PubMed articles
PMC_ID_TAG = "pmcid" # name of the tag containing the PMC ID
SOURCE_TAG = "source" # name of the tag containing the source of the article
PUBMED_SOURCE = "MED" # String used in the case of PubMed articles
PUBMEDCENTRAL_SOURCE = "PMC" # String used in the case of PubMed Central articles
PUBMED_PUBANNOTATION = "PubMed" # String used by Pubannotation in PubMed articles
# Create your pubannotation account to fill the credentials http://pubannotation.org/
PUBANNOTATION_USERNAME = "" # Your pubannotation user name
PUBANNOTATION_PASSWORD = "" # Your pubannotation password
PUBANNOTATION_PROJECT = "BLAH2015_Annotations_drugs" # Your pubannotation project
HTTP_CODE_CREATED_RESOURCE = 201

#Easy XML tag parsing function - this is for badly formed XML input
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return "NULL"

# Invokes find_between function with XML tags
def find_between_tags( s, tag ):
	initial_tag = "<" + tag + ">"
	end_tag = "</" + tag + ">"
	return find_between( s, initial_tag, end_tag )

# Obtains europepmc query url
def europe_pmc_url_generator(search_term):
	# We use Europe PMC restful webservices (http://europepmc.org/RestfulWebService)
	euro_pmc_base_url = "http://www.ebi.ac.uk/europepmc/webservices/rest/search/query="
	# Search parameters:
	#	- Articles that are open access (open_access:y)
	#	- Article including the synonyms of the search terms (synonym=true)
	#	- Get the list of article's IDs (resulttype=idlist)
	url_params = "%20open_access:y&synonym=true&resulttype=idlist"
	full_url = euro_pmc_base_url + search_term + url_params
	return full_url

# Gets the total number of results that Europe PMC contains for the search query
def get_number_of_results(search_term):
	europe_pmc_url_to_query = europe_pmc_url_generator(search_term)
	print europe_pmc_url_to_query
	response = urllib2.urlopen(europe_pmc_url_to_query)
	html = response.read()
	total_articles = int(find_between_tags(html,'hitCount'))
	print "Number of articles matching the search query " + str(total_articles)
	return total_articles

# Downloads the results and stores these in a file
def download_and_store_europe_pmc_results(search_term, articles_file):
	total_articles = get_number_of_results(search_term)	
	epmc_current_page = 1 # EMPC paginates the results. The first page is page number 1
	remaining_articles = total_articles
	europe_pmc_url_to_query = europe_pmc_url_generator(search_term)
	ftw = open(str(articles_file),'a')
	while remaining_articles > 0:
		matched_articles_url = europe_pmc_url_to_query + "&page=" + str(epmc_current_page)
		# print matched_articles_url
		# Download the contents from the page
		response = urllib2.urlopen(matched_articles_url)
		html = response.read()
		# Store the contents in a file
		ftw.write(html)
		remaining_articles = remaining_articles - EPMC_PAGE_SIZE
		epmc_current_page += 1
	ftw.close()	
	return

# Stores one article in pubannotation
def store_article_in_pubannotation(json_article_source, article_id):
	pubannotation_add_article_url = "http://pubannotation.org/projects/" + PUBANNOTATION_PROJECT + "/docs/add.json"
	headers = {'content-type': 'application/json', 'Accept': 'text/plain'}
	json_details = json.dumps({"sourcedb":json_article_source,"sourceid":article_id})
	r = requests.post(pubannotation_add_article_url, json_details, auth=(PUBANNOTATION_USERNAME, PUBANNOTATION_PASSWORD), headers=headers)	
	print json_details + " resulted in: " + str(r.json)
	return r.status_code

# Parses the file containing the matched articles and generates the json string to upload to the articles to pubannotations
def parse_file_and_store_articles_in_pubannotation(articles_file):
	# This string marks the end of a result
	full_text_article_base_url_start = "http://www.ebi.ac.uk/europepmc/webservices/rest/"
	full_text_article_base_url_end = "/fullTextXML"
	ftr= open(articles_file, 'r')
	line_matched_articles = ftr.readline()
	line_matched_articles = str(line_matched_articles)
	match_end = 0
	articles_json_data = []
	while match_end < len(line_matched_articles):
		match_end = line_matched_articles.index(ARTICLE_END) + len(ARTICLE_END)
		# extract id
		s = line_matched_articles[:match_end]
		article_id = find_between_tags(s, PMC_ID_TAG)
		article_pm_id = find_between_tags(s, PM_ID_TAG)
		article_source = find_between_tags(s, SOURCE_TAG)
		line_matched_articles = line_matched_articles[match_end:]
		### Here we download the articles from Europe Pubmed
		pubmed_full_text_article_url = full_text_article_base_url_start + article_id + full_text_article_base_url_end
		# print pubmed_full_text_article_url
		# Only PMC or Pubmed articles are allowed
		if ((article_source == PUBMEDCENTRAL_SOURCE) or (article_source == PUBMED_SOURCE)): # Start
			print "Trying to store article : " + article_id + "(pmid= " + article_pm_id + ")"
			# Let's try first to upload the article as PMC (to upload all sections and not just title and abstract)
			if (store_article_in_pubannotation(PUBMEDCENTRAL_SOURCE, article_id) == HTTP_CODE_CREATED_RESOURCE):
				print "Article stored in pubannotation " + article_pm_id
			elif (article_pm_id != "NULL"):
				store_article_in_pubannotation(PUBMED_PUBANNOTATION, article_pm_id)
		else:
			print "Only Pubmed or PMC articles can be uploaded to PubAnnotations.org This article raised an error: " + 	pubmed_full_text_article_url + "\n"
	return articles_json_data

################
# Main part
################
if __name__ == '__main__':
	search_terms = ["Adderall", "Ritalin", "Modafinil", "Adrafinil", "Armodafinil", "Citalopram", "Escitalopram", "Paroxetine", "Fluoxetine", "Fluvoxamine", "Sertraline"]
	# file where we store the results
	articles_file = "BLAH2015_Annotations_drugs.txt"
	ftw = open(articles_file,'w').close()
	for term in range(len(search_terms)):
		search_term = search_terms[term]
		print "Current search term: " + search_term
		download_and_store_europe_pmc_results(search_term, articles_file)
	parse_file_and_store_articles_in_pubannotation(articles_file)
	print "Process ended"
