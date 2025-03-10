# 01_Bills

# Bills Classification Datacard 

## Dataset Description

### Dataset Summary
The Bills Classification dataset is a collection of Congressional Bills from the 101st to 118th Congress with their legislative subjects and policy areas, suitable and intended for use in training and evaluating (large language) classification models and other approaches to classifying Bill texts by subject and policy area.  

### Supported Tasks

### Languages
The dataset is entirely in English.

## Dataset Structure
The dataset is in the form of a dataframe where each bill contains its identifiers (congress, house-billType and bill number-billNumber), most recent version of the bill text, legislative subjects and policy area categories.

### Data Instances
An example of the dataframe is as follows:

| congress | billType | billNumber | legislativeSubjects                                | policyArea                                  | billText                                          |
| :---:    | :---:    | :---:      | :---:                                              | :---:                                       | :---:                                             |
| 101      | hconres  | 1          | [American economic assistance, American milita...] | International Affairs	                      | `<pre>Â \nB37 6-6-89 [OC's]\nHCON 1 IH\n101st C...` |
| 101      | hconres  | 10         | [Constitutional law, Meditation, Prayer in the...] | Civil Rights and Liberties, Minority Issues | `<pre>Â \nB37 Rosey 1/4/89 [Updated]\nHCON 10 I..`  |
| 101      | hconres  | 100        | [Genocide, Human rights, International relief,...] | International Affairs | `<pre>Â \nHCON 100 IH\n101st CONGRESS\n1st Sess...` |

Note that the billText values in this example have been truncated. Bill texts contain roughly 7000 words on average.

### Data Fields
| Field               | Description |
|:---:                |:---:                              |
| congress            | String or integer indicating the congress that the bill belongs to |
| billType            | String indicating the house that the bill belong to |
| billNumber          | Integer indicating the bill number |
| legislativeSubjects | List of strings containing the legislative subjects assigned to the bill |
| policyArea          | String containing the policy area assigned to the bill |
| billText            | HTML string containing the most recent text of the bill |

### Data Versions
We are providing multiple version of the bills dataset. These include the original version, with some bills being removed from the set according to set criteria, and versions that have had resampling techniques applied to mitigate the statistical bias (imbalance) present in the original data. 

All files are gzipped and range from 0.02GB to 0.84GB in size.

## Dataset Creation

### Curation Rationale
This dataset as been created on behalf of the Library of Congress.

### Source Data
The source data comprises the Congressional Bills relevant files (subjects, texts, metadata) which are available through the Congress.gov API.

#### Initial Data Collection and Normalization

##### Data Retrieval

Data on individual bills from the 101st to 118th Congresses was gathered from the [Congress.gov API](https://api.congress.gov/). This initial range of source data for the datasets was selected as it could provide a consistent set of subjects along with plaintext for bills suitable for use in classification tasks. 

##### Normalization
We have made the decision to not perform any text related pre-processing on the bill text itself. This data has been retrieved by filtering the text versions by date and taking the most recent HTML file in its raw format. As such, the text contains HTML tags which may or may not be useful depending on the model the user decides to use. We have therefore left it up to the user of the dataset to determine what, if any, pre-processing they would like to apply to the bill texts.

##### Statistical Bias (Imbalance)
As part of our initial exploratory data analysis, general and targeted statistical profiling was performed on the data [(see notebooks here)](03_profiling). It was discovered that the data was highly skewed with regards to legislative subjects, which include Geographic Entities and Organization Names, with the most common occurring term appearing over 30,000 times while the least common only appears once. Due to this discrepancy it is highly likely that any classification models trained on the original data will be biased towards the more frequently occurring terms.

To mitigate this bias caused by statistical imbalance, we have created multiple re-sampled versions of this data and reapplied some statistical profiling to evaluate the subsequent datasets, [see notebook](03_profiling/03_post_resampling_stat_profiling_visualization.ipynb) for visualization and analysis of data splits. To outline, mitigation methods that have been applied are as follows:
1. Random Undersampling
2. k-Nearest-Neighbors Undersampling
3. NearMiss Undersampling
4. Random Oversampling
5. Hybrid: Random Undersampling followed by Random Oversampling.

Please see our [configurations](04_mitigating_imbalance/config.py) used for these techniques. The configurations include arguments specific to each approach which may be similar for some due to the nature of each algorithm.



### Personal and Sensitive Information
The bills used are public law texts, therefore any identifiable information will pertain to public figures.

## Considerations for Using the Data
Not applicable. 

### Social Impact of Dataset
Not applicable. 

### Discussion of Biases
Not applicable. 

### Other Known Limitations
Not applicable. 

## Additional Information
### Dataset Curators
### Licensing Information
The datasets used in the experiment are public domain, and all data generated has no intellectual property or privacy restrictions.

### Citation Information
### Contributions


# How to run

Instructions for running any specific part of the code can be found in the relevant subdirectory.