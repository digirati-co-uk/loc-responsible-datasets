# Retrieval 

The source data for this dataset has been gathered from the [Congress.gov API](https://api.congress.gov/) and stored in an s3 bucket for further processing. 


## Scripts

This directory contains scripts used to retrieve the source data for the bills dataset. Scripts are provided that can be run in a local environment and store in a local filesystem, or that can be run in a ray cluster and store to an s3  bucket. In practice, the latter was used to gather the source data as it allowed for parallelisation in a more resilient environment (e.g. task re-running on failure). 

These scripts allow for the retrieval of bill data from the Congress.gov API in two stages. Firstly, for a given set of congresses, the paginated JSON responses from the [bill list by congress](https://api.congress.gov/#/bill/bill_list_by_congress) endpoint are retrieved and stored. These provide a canonical list of all bills available from the API, and are used as the source of data for identifiers of individual bills to be fetched at the next state. Then, for each bill in the paginated responses, the [bill details](https://api.congress.gov/#/bill/bill_details) JSON response is fetched and stored, along with the [bill subjects](https://api.congress.gov/#/bill/bill_subjects), [bill summaries](https://api.congress.gov/#/bill/bill_summaries) and [bill text](https://api.congress.gov/#/bill/bill_text) if present. All `.xml` and `.htm` versions of the text present in the bill text response are fetched and stored. 

### Environment 

The following env variables should be set for the 
```sh
export RAY_ADDRESS="http://127.0.0.1:8264"
export CONGRESS_GOV_API_KEY=<CONGRESS_GOV_API_KEY>
```
n.b. all example commands below also include the `CONGRESS_GOV_API_KEY` provided as an argument or option where appropriate. 

### Data Structure and Location





### Congress bill pages

- [get_congress_bills_source_pages.py](./get_congress_bills_source_pages.py)
  - Fetch and store the paginated responses from the [bill list by congress](https://api.congress.gov/#/bill/bill_list_by_congress) endpoint for a given congress.
  - Creates a status page alongside the stored page response to record bill download status. 
  - Run locally 
  - Requires an Congress.gov API key. 
  - Running: 
    ```sh
    uv run get_congress_bills_source_list.py --api-key=<CONGRESS_GOV_API_KEY> --congress=119
    ```
- [ray_get_congress_bills_source_pages.py](./ray_get_congress_bills_source_pages.py)
  - Fetch and store the paginated responses from the [bill list by congress](https://api.congress.gov/#/bill/bill_list_by_congress) endpoint for a given congress. 
  - Creates a status page alongside the stored page response to record bill download status. 
  - Run in a ray cluster - address set via env variable. 
  - Requires an Congress.gov API key. 
  - Running: 
    ```sh
    uv run ray job submit --working-dir . -- python ray_get_congress_bills_source_pages.py <CONGRESS_GOV_API_KEY> --congress=109
      ```

### Bill data

- [get_page_bills_data.py](./get_page_bills_data.py)
    - Fetch bill data for all bills in the provided page from the [bill list by congress](https://api.congress.gov/#/bill/bill_list_by_congress) endpoint. 
    - Fetches data about the bill from the following endpoints: 
        - [bill details](https://api.congress.gov/#/bill/bill_details)
        - [bill subjects](https://api.congress.gov/#/bill/bill_subjects)
        - [bill summaries](https://api.congress.gov/#/bill/bill_summaries)
        - [bill text](https://api.congress.gov/#/bill/bill_text) 
        - Linked `.htm` and `.xml` versions of the bill text. 
    - Records status of bill download in the status page associated with the provided source page. 
    - Run locally 
    - Requires an Congress.gov API key. 
    - Running: 
      ```sh
      uv run get_page_bills_data.py --api-key=<CONGRESS_GOV_API_KEY> --source-path=../local_data/bills/source_list/110_0.json
      ```
- [ray_get_page_bills_data.py](./ray_get_page_bills_data.py)
  - Fetch bill data for all bills in the provided page from the [bill list by congress](https://api.congress.gov/#/bill/bill_list_by_congress) endpoint. 
  - Fetches data about the bill from the following endpoints: 
      - [bill details](https://api.congress.gov/#/bill/bill_details)
      - [bill subjects](https://api.congress.gov/#/bill/bill_subjects)
      - [bill summaries](https://api.congress.gov/#/bill/bill_summaries)
      - [bill text](https://api.congress.gov/#/bill/bill_text) 
      - Linked `.htm` and `.xml` versions of the bill text. 
  - Records status of bill download in the status page associated with the provided source page. 
  - Run in a ray cluster - address set via env variable. 
  - Requires an Congress.gov API key. 
  - Running: 
    ```sh
    uv run ray job submit --working-dir . -- python ray_get_page_bills_data.py <CONGRESS_GOV_API_KEY> --source-file=s3://loc-responsible-datasets-source-data/01_bills/source_pages/110_500.json
    ```
- [ray_get_congress_bills.py](./ray_get_congress_bills.py)
  - Fetch bill data for all bills in the provided page from the [bill list by congress](https://api.congress.gov/#/bill/bill_list_by_congress) endpoint. 
  - Fetches data about the bill from the following endpoints: 
      - [bill details](https://api.congress.gov/#/bill/bill_details)
      - [bill subjects](https://api.congress.gov/#/bill/bill_subjects)
      - [bill summaries](https://api.congress.gov/#/bill/bill_summaries)
      - [bill text](https://api.congress.gov/#/bill/bill_text) 
      - Linked `.htm` and `.xml` versions of the bill text. 
  - Records status of bill download in the status page associated with the provided source page. 
  - Run in a ray cluster - address set via env variable. 
  - Requires an Congress.gov API key. 
  - Running: 
    ```sh 
    uv run ray job submit --working-dir . -- python ray_get_congress_bills.py <CONGRESS_GOV_API_KEY> --congress=112
    ```
- [ray_get_congress_range_bills.py](./ray_get_congress_range_bills.py)
  - Fetch bill data for all bills in the provided page from the [bill list by congress](https://api.congress.gov/#/bill/bill_list_by_congress) endpoint. 
  - Fetches data about the bill from the following endpoints: 
      - [bill details](https://api.congress.gov/#/bill/bill_details)
      - [bill subjects](https://api.congress.gov/#/bill/bill_subjects)
      - [bill summaries](https://api.congress.gov/#/bill/bill_summaries)
      - [bill text](https://api.congress.gov/#/bill/bill_text) 
      - Linked `.htm` and `.xml` versions of the bill text. 
  - Records status of bill download in the status page associated with the provided source page. 
  - Run in a ray cluster - address set via env variable. 
  - Requires an Congress.gov API key. 
  - Running: 
    ```sh
    uv run ray job submit --working-dir . -- python ray_get_congress_range_bills.py <CONGRESS_GOV_API_KEY> --start=110 --end=118
    ```

### Dataset information 
[create_bill_status_dataframes.py](./create_bill_status_dataframes.py)

[create_page_status_dataframes.py](./create_page_status_dataframes.py)

[status_reporting.ipynb](./status_reporting.ipynb)

### Other

[ray_update_source_pages_subfield_status.py](./ray_update_source_pages_subfield_status.py)
- The first pass at retrieving the source data did not include the `.htm` versions of the text files. This script updates the status files such that the `textVersions` subfield is set to `processed=False`. This allowed for reprocessing of all bills using the same scripts as before, only fetching the additional `.htm` files rather than all data about a bill. 
- To run: 
  ```sh 
  uv run ray job submit --working-dir . -- python ray_update_source_pages_subfield_status.py --congress=102
  ```


