# 01_Bills

## Bills Classification Datacard 

## Dataset Description
Repository:

### Dataset Summary
The Bills Classification dataset is a collection of Congressional Bills with their legislative subjects and policy areas, suitable and intended for use for training and evaluating (large language) classification models. 

### Supported Tasks

### Languages
The dataset is entirely in English.

## Dataset Structure
The dataset is in the form of a dataframe where each bill contains its identifiers (congress, house -billType and bill number - billNumber), most recent version of the bill text, legislative subjects and policy area categories.

### Data Instances
An example of the dataframe is as follows:

| congress | billType | billNumber | legislativeSubjects                                | policyArea                                  | billText                                          |
| :---:    | :---:    | :---:      | :---:                                              | :---:                                       | :---:                                             |
| 101      | hconres  | 1          | [American economic assistance, American milita...] | International Affairs	                      | <pre>Â \nB37 6-6-89 [OC's]\nHCON 1 IH\n101st C... |
| 101      | hconres  | 10         | [Constitutional law, Meditation, Prayer in the...] | Civil Rights and Liberties, Minority Issues | <pre>Â \nB37 Rosey 1/4/89 [Updated]\nHCON 10 I..  |

### Data Fields
| :---:    | :---:    |
| congress            | String or integer indicating the congress that the bill belongs to |
| billType            | String indicating the house that the bill belong to |
| billNumber          | Integer indicating the bill number |
| legislativeSubjects | List of strings showing the legislative subjects assigned to the bill |
| policyArea          | String showing the policy area assigned to the bill |
| billText            | String containing the most recent text of the bill |

### Data Versions
We are providing multiple version of the bills dataset. These include the original version, with some bills being removed from the set according to set criteria, and versions that have had resampling techniques applied to mitigate the statistical bias (imbalance) present in the original data. 

All files are gzipped which range from 0.02GB to 0.84GB in size.

## Dataset Creation

### Curation Rationale
### Source Data
#### Initial Data Collection and Normalization
Finlay



We have made the decision to not perform any text related pre-processing on the bill text itself. This data has been retrieved by filtering the text versions by date and taking the most recent HTML file in its raw format. As such, the text contains HTML tags which may or may not be useful depending on the model the user decides to use. We have therefore left it up to the user of the dataset to determine what, if any, pre-processing they would like to apply to the bill texts.

### Personal and Sensitive Information
The bills used are public law texts.

## Considerations for Using the Data
### Social Impact of Dataset
### Discussion of Biases
### Other Known Limitations

## Additional Information
### Dataset Curators
### Licensing Information
The datasets used in the experiment are public domain, and all data generated has no intellectual property or privacy restrictions.

### Citation Information
### Contributions