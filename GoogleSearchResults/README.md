# Google search results collector

Simple shell script to grab results from Google search using seeks

## Requirement : a Seeks http node

Can use an external existing [Seeks](http://www.seeks-project.info/) node like the [official one](http://www.seeks.fr) or a locally installed one.
Read/run ``seeks/INSTALL`` to install, configure and run locally.

## Arguments and example

``./get_results.sh <list_keywords_file> [<N_results>] [<search_lang>] [<url_seeks_node>]``

* ``list_keywords_file``: path to a text file containing a list of search queries listed as lines (example given in ``keywords_example.txt``)
* ``N_results``: maximum number of results desired for each keyword (optional, defaults to 100)
* ``search_lang``: 2 letters code for language of the desired research (examples: en, fr, de, es... optional, defaults to en)
* ``url_seeks_node``: root url (optional, defaults to ``http://localhost:8080``)

For instance for the first 200 results of searches on Google (english) from the sample ``keywords_example.txt`` list with a local Seeks node running on port 8080:
``./get_results.sh keywords_example.txt 200``

And collect your results in the directory keywords_example.

A few python and shell scripts allow you to download the results and extract the raw text within them.
A regular routine to do so would be for instance:
```bash
  bash get_results.sh keywords_example.txt 200
  # bash make_csv_from_json_results_dir.sh keywords_example     # This command is automatically ran at the end of the previous one
  bash get_text_from_csv_results.sh keywords_example            # This command will call the scripts dl_and_extract_text_from_url.sh, ghost_download.py and extractTxtFromHtml_BoilerPipe.py
  bash build_corpus_from_text_results.sh keywords_example
  # Assuming a second corpus keyword_example2 was ran, fusing the two resulting datasets can be performed by:
  bash build_results_fom_two_corpora.sh keywords_example keywords_example2

```

These latest features require to install a few more dependencies for which an example of installation is shown in ``installs-boilerpipe-ghost.sh``.

