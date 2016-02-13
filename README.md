<h1>This project contains the files used by Annotations team during BLAH 2015</h1>

<h2>General Overview</h2>
Our project aimed to create automated annotations for articles retrieved from Europe PMC (http://europepmc.org/). To achieve this goal we divided the project into several parts, creating a python script for each one.
<br/>
The information on BLAH 2015 can be found on its website: http://2015.linkedannotation.org/

<h2>Scripts description</h2>
Following, there is a brief description of each one of the scripts we produced.

<h3>1_search_epmc_and_store_article_in_pubannotation.py</h3>
This script is in charge of querying Europe PMC website using its API (http://europepmc.org/RestfulWebService) to obtain the information on the articles matching our query.
Our query contained the name of the drugs included in our study.<br/>
<code>search_terms = ["Adderall", "Ritalin", "Modafinil", "Adrafinil", "Armodafinil", "Citalopram", "Escitalopram", "Paroxetine", "Fluoxetine", "Fluvoxamine", "Sertraline"]</code><br/>
As the API does not allow concatenation of search terms we had to query each drug separately. Articles IDs can be queried too:<br/>
<code>search_terms = ["PMC2548241", "PMC4319657"]</code><br/>
After the query has taken place the code iterates over all results storing the IDs.
The IDs are then used to store the articles in pubannotation website (http://pubannotation.org).

<h3>2_pubannotation_article_processor.py</h3>
This script runs over all the articles stored in pubannotation by the previous script and outputs the lines that contain a patient descriptor.
The patient descriptors have been manually stored in a dictionary (PATIENT-dic.tsv)
The resulting matches are stored in a file that will be fed to the next script.

<h3>3_automatic_annotator.py</h3>
This script invokes NCBO annotator using the selected ontologies. In our case we use "PATO" and "CHEBI"<br/>
<code>ontologies = "PATO,CHEBI"</code><br/>
The full list of ontologies supported by NCBO annotator can be found in their website (http://bioportal.bioontology.org/ontologies)
This script also allows the use of dictionaries. The dictionaries should contain 2 fields separated by a tab<br/>
<code>Term_ID TAB_SEPARATOR Description_of_the_term</code><br/>
In our case we use a Phenotype dictionary (generated from Phenominer's S3 file: https://github.com/nhcollier/PhenoMiner/blob/master/data/S3.gz) and the patients dictionary:<br/>
<code>dictionaries = ["PHENOM-dic.tsv", "PATIENT-dic.tsv"]</code><br/>
The annotations are stored in a new file containing the offsets and the annotations (use variable "file_to_write" to specify the name of the output).

The initial version of this script (in which this version is based) was created by jmbanda: https://github.com/jmbanda/BLAH2015

<h4>3b_automatic_annotator.py</h4>
Alternatively, the file to be annotated with NCBO can be passed as an argument when running the python script in the command line. That is specially useful when there is a large file to be annotated as such file could be split into parts using <code>x3_split_file.py</code> (The resulting parts will be placed in the folder <code>file_part/</code>).

The script <code>3b_automatic_annotator.py</code> can annotate all the parts independently (the resulting annotations will be placed in the folder <code>parts_output/</code>). To launch the annotator many times you can use a custom script similar to the one called *parallelize.sh*

Once you have all the annotations in place you only have to put them together into one large file (i.e. $ cat annotation1 annotation2... annotationN > AllAnnotations) and then move on to the next step.

<h3>4_merge_annotations.py</h3>
This script takes the annotations generated in the previous step using NCBO annotator and the dictionary and combines them. The output will be stored in a file called *mergedAnnotations.txt*.

Change the names of the files to be merged in <code>listFiles</code> variable.
 
<h3>5_prepare_json.py</h3>
Once the previous step is done, we can prepare the Json files with the annotations for each article. All the Json files will be stored to *"json_output"* folder although it can be changed in the line <code>file_with_json_objects = "json_output"</code> of this file.

<h3>6_test_output_annotations.py</h3>
This script receives the file with the annotations, and also the files with the texts, and prints out the annotations that are going to be stored.

This script is provided as a way to test which are the annotations that are going to be stored in JSON files (in the previous step: <code>5_prepare_json.py</code>).


<h3>Uploading the annotations</h3>
To upload the annotations to PubAnnotations (http://pubannotation.org) you can create a tar.gz file (including all the files in the folder *"json_output"* created two steps before: <code>5_prepare_json.py</code>) and then upload it to the desired project you own.


In our case we used the batch upload functionality (http://www.pubannotation.org/docs/submit-annotation/) after generating a **tar.gz** file called *annotations.tar.gz* with this command <code>tar -cvzf annotations.tar.gz json_output/</code>.

In case there are too many files to compress you may need to prepare the tar.gz file in 3 steps:
1- Store the list of files to a file first <code>ls json_output/ > list_files.txt</code>
2- Then, go to that directory <code>cd json_output</code>
3- Compress the file using the list of files we prepared <code>tar -cvz -T ../list_files.txt -f NEUROSES.tar.gz</code>


The resulting annotations will be available for download from PubAnnotation website.

