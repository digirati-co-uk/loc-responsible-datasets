# Assembly

This directory holds the code for creating the Dataframes (CSV files), which is to be run on XML files following [reformatting](../01_reformatting/).

## Script
### Assemble Dataframe
- [01_run_assembly.py](./01_run_assembly.py)
    - Loads in XML file
    - Pulls out transliterated field `880` and pairs them
    - Creates dataframe according to filtering and exclusion scheme 
    - Saves Dataframe to output directory 
    - Run locally
    - Running:
    `uv run 01_run_assembly.py --xml-file-path=path/to/xml_file --output-dir=path/to/save/output_dataframe --filtering-type=type_of_filtering_to_be_applied --excluding-type=type_of_exclusion_to_be_applied`
