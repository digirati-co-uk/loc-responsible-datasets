# Reformatting

This directory holds the code for creating XML files, which is to be following the download cataloging record files.

## Scripts
### Reformat TXT to MARCXML
- [01_run_reformatter.py](./01_run_reformatter.py)
    - Loads TXT file containing cataloging records
    - Saves as (MARC)XML file to the output directory under the same file name.
    - Runs locally
    - Running:
    `uv run 01_run_reformatter.py --txt-file-path=path/to/txt_file --xml-file-dir=path/to/XML_output_directory`

### Combine XML files
- [02_combine_xml.py](./02_combine_xml.py)
    - Loads in two XML files
    - Converts each file to dictionary 
    - Compares dictionaries to create a [union](https://en.wikipedia.org/wiki/Union_(set_theory)) of the dictionaries 
    - Converted union dictionary back to MARC XML structure
    - Saves as XML file to output path
    - Runs locally
    - Running:
    `uv run 02_combine_xml.py --xml-file-path-1=path/to/first/xml_file --xml-file-path-2=path/to/second/xml_file --combined-xml-output-path=path/to/save/output/xml_file`