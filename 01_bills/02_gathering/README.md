# 02_Gathering
This directory holds the code for creating Pandas datafames which is to be run following the retrieval of information from the Congres.gov APIs using the scripts in [01_retrieval](01_retrieval).

### Script explanations
1. [01_get_compiled_subjects_dataframe.py](01_get_compiled_subjects_dataframe.py) 
Returns a dataframe containing for each bill its identifiers (congress, billNumber and billType), policyArea and legislativeSubjects. This data is gathered using the `subjects.json` file for each bill. If a bill does not have this file then it will not be in the resulting dataframe.

2. [02_get_compiled_subjects_with_text_dataframe.py](02_get_compiled_subjects_with_text_dataframe.py)
Returns a dataframe containing for each bill its identifiers (congress, billNumber and billType), policyArea, legislativeSubjects and billText. 

The subjects data (legislativeSubjects and policyArea) is gathered using the `subjects.json` file for each bill. 

The bill text is gathering using the `text.json` file. Within this file is a list of textVersions which we have filtered by date. We take the most recent textVersion and read in the text from its linked HTML file to populate the billText field of the dataframe for each bill. If any or all of the textVersions fail to have a date then the bill is not included in the dataset. Subsequently, all bills from the 101st and some bills from the 102nd and 103rd Congresses are not included in the dataframe.

If a bill does not have a `subjects.json` and/ or `text.json` then it will also not be in the resulting dataframe.


## How to run

Ensure that the directory containing the relevant information for the bills data retrieved using the scripts from [01_retrieval](01_retrieval) is structured such that each individual bill has a directory with the following path: `{source_bills}/{congress}/{billType}/{billNumber}/`

Activate suitable environment. If using a uv venv, run `uv run <script_name.py>`

Tips:
- For quicker execution of code, it is advised to run [01_get_compiled_subjects_dataframe.py](01_get_compiled_subjects_dataframe.py) or [02_get_compiled_subjects_with_text_dataframe.py](02_get_compiled_subjects_with_text_dataframe.py) on a Congress by Congress basis. To do so, set the `source_directory` argument to point to the directory `{source_bills}/{congress}` for each `congress` instead of the source_bills parent directory, and change `glob pattern` to `"*/*/"`
- To concatinate the dataframes created per congress, run [03_concatinate_dataframes.py](03_concatinate_dataframes.py).


01_get_compiled_subjects_dataframe.py should be run following from the scripts in retrieval step from 01_retrieval