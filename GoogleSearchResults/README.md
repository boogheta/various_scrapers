# Google search results collector

Simple shell script to grab results from Google search using seeks

## Requirement : a Seeks http node

Can use an external existing [Seeks](http://www.seeks-project.info/) node like the [official one](http://www.seeks.fr) or a locally installed one.
Read/run ``seeks/INSTALL`` to install and configure locally.

## Arguments and example

``./get_results.sh <list_keywords_file> [<N_results>] [<url_seeks_node>]``

* ``list_keywords_file``: path to a text file containing a list of search queries listed as lines (example given in ``keywords_example.txt``)
* ``N_results``: maximum number of results desired for each keyword (optional, defaults to 100)
* ``url_seeks_node``: root url (optional, defaults to ``http://localhost:8080``)

For instance for the first 200 results of searches from the sample ``keywords_example.txt`` list with a local Seeks node running on port 8080:
``./get_results.sh keywords_example.txt 200``

