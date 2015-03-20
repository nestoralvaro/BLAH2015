<h1>This project contains the files used by Annotations team during BLAH 2015</h1>

<h2>General Overview</h2>
Our project aimed to create automated annotations for articles retrieved from Europe PMC (http://europepmc.org/). To achieve this goal we divided the project into 4 parts, creating a python script to work on each one of them.

<h2>Scripts description</h2>
Following, there is a brief description of each one of the scripts we produced.

<h3>1_search_epmc_and_store_article_in_pubannotation.py</h3>
This script is in charge of querying Europe PMC website using its API (http://europepmc.org/RestfulWebService) to obtain the information on the articles matching our query.
Our query contained the name of the drugs included in our study.
<code>search_terms = ["Adderall", "Ritalin", "Modafinil", "Adrafinil", "Armodafinil", "Citalopram", "Escitalopram", "Paroxetine", "Fluoxetine", "Fluvoxamine", "Sertraline"]</code>
As the API does not allow concatenation of search terms we had to query each drug separately. Articles IDs can be queried too:
<code>search_terms = ["PMC2548241", "PMC4319657"]</code>
After the query has taken place the code iterates over all results storing the IDs.
The IDs are then used to store the articles in pubannotation website (pubannotation.org)

<h3>2_pubannotation_article_processor.py</h3>
This script runs over all the articles stored in pubannotation by the previous script and outputs the lines that contain a patient descriptor.
The patient descriptors have been manually stored in a dictionary (PATIENT-dic.tsv)
The resulting matches are stored in a file that will be fed to the next script

<h3>3_automatic_annotator.py</h3>
This script invokes NCBO annotator using the selected ontologies. In our case we use "PATO" and "CHEBI" <code>ontologies = "PATO,CHEBI"</code>. The full list of ontologies supported by NCBO annotator can be found in their website (http://bioportal.bioontology.org/ontologies)
This script also allows the use of dictionaries. The dictionaries should contain 2 fields separated by tabs <code>Term_ID TAB_SEPARATOR Description_of_the_term</code>. In our case we use a Phenotype dictionary (generated from Phenominer's S3 file: https://github.com/nhcollier/PhenoMiner/blob/master/data/S3.gz) and the patients dictionary <code>dictionaries = ["PHENOM-dic.tsv", "PATIENT-dic.tsv"]</code> 
The annotations are stored in a new file containing the offsets and the annotations.

The initial version of this script (in which this version is based) was created by jmbanda: https://github.com/jmbanda/BLAH2015

<h3>4_store_json_annotation_in_pubannotation.py</h3>
This script takes the annotations generated in teh previous step and uploads them to pubannotation.
 

