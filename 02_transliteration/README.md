# Transliteration Dataset

## Dataset
[DataCard.md](./DataCard.md) contains information about the datasets described below.

### Dataset 1:
Multiple dataset files.
- Contains transliteration-script pairs across all fields excluding `650, 3XX and 5XX` fields.
- No further filtering and/ or exclusions have been applied
- [s3://loc-responsible-datasets/02_transliteration/generated_data/no_filtering/transliteration_all_unique_Japanese_records_no_filters.csv.gz](s3://loc-responsible-datasets/02_transliteration/generated_data/no_filtering/transliteration_all_unique_Japanese_records_no_filters.csv.gz)
- [s3://loc-responsible-datasets/02_transliteration/generated_data/no_filtering/transliteration_Japanese_records_personal_names_w_800_20250325.csv.gz](s3://loc-responsible-datasets/02_transliteration/generated_data/no_filtering/transliteration_Japanese_records_personal_names_w_800_20250325.csv.gz)

### Dataset 2:
Multiple dataset files.
- Personal names datasets containing only personal name fields (`100, 600, 700, and 800`), with each field only containing the `a` subfield as requested.
    - [s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_all_unique_Japanese_records_personal_names.csv.gz](s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_all_unique_Japanese_records_personal_names.csv.gz)
    
    - [s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_Japanese_records_personal_names_w_800_20250325_personal_names.csv.gz](s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_Japanese_records_personal_names_w_800_20250325_personal_names.csv.gz)
    
- Corporate names datasets containing only corporate name fields (`110, 610, 710, and 810`), with each field only containing the `a` subfield.
    - [s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_all_unique_Japanese_records_corporate_names.csv.gz](s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_all_unique_Japanese_records_corporate_names.csv.gz)
    - [s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_Japanese_records_personal_names_w_800_20250325_corporate_names.csv.gz](s3://loc-responsible-datasets/02_transliteration/generated_data/filtered_on/transliteration_Japanese_records_personal_names_w_800_20250325_corporate_names.csv.gz)
    
- No-names datasets containg all other non-personal and non-corporate name fields in additional to exclusions in Dataset 1.
    - [s3://loc-responsible-datasets/02_transliteration/generated_data/no_filtering/transliteration_all_unique_Japanese_records_no_filters_no_names.csv.gz](s3://loc-responsible-datasets/02_transliteration/generated_data/no_filtering/transliteration_all_unique_Japanese_records_no_filters_no_names.csv.gz)
    

## Code
[uv](https://docs.astral.sh/uv/) has been used for dependency and environment management on this project, with [pyproject.toml](./pyproject.toml) containing the revelant configuration. All scripts and notebooks in subdirectories can be run using this environment.

Code and documentation for the various tasks involved with creating this dataset are found in the following subdirectories:
- [01_reformatting](./01_reformatting)
    - Reformatting of source code from TXT to XML and combining of XML files.
- [02_assembly](./02_assembly/)
    - Compiling of XML files into CSV files according to relevant splits.