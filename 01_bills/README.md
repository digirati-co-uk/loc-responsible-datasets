
# Bills Classification Dataset

## Dataset

[DataCard.md](./DataCard.md) contains information about both the overall and resampled datasets described below. 


### Dataset 1: 
Single dataset file. 
  - No resampling, contains all of the data available from the source data collected from the API. 
  - [s3://loc-responsible-datasets/01_bills/generated_data/concat_compiled_subjects_with_text.csv.gz](s3://loc-responsible-datasets/01_bills/generated_data/concat_compiled_subjects_with_text.csv.gz)

### Dataset 2: 

Multiple methods of re-sampling data. 

- Random under-sampling followed my random oversampling. 
  - This was judged to be the best re-sampling method, as it allowed for an improved imbalance ratio, maintenance of overall class distribution and adequate sample size. 
  - [s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_rus_ros.csv.gz](s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_rus_ros.csv.gz)
- [s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_knn_undersampling.csv.gz](s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_knn_undersampling.csv.gz)
- [s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_near_miss_undersampling.csv.gz](s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_near_miss_undersampling.csv.gz)
- [s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_random_oversampling.csv.gz](s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_random_oversampling.csv.gz)
- [s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_random_undersampling.csv.gz](s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_basic_random_undersampling.csv.gz)
- [s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_random_undersampling.csv.gz](s3://loc-responsible-datasets/01_bills/generated_data/resampled_data/legislativeSubjects_random_undersampling.csv.gz)


## Code

[uv](https://docs.astral.sh/uv/) has been used for dependency and environment management on this project, with [pyproject.toml](pyproject.toml) containing the relevant configuration. All scripts and notebooks in subdirectories can be run using this environment. 

Code and documentation for the various tasks involved with creating this dataset are found in the following subdirectories: 
- [01_retrieval](./01_retrieval/README.md)
  - Retrieval of source data from the Congress.gov API. 
- [02_gathering](./02_gathering/README.md)
  - Compiling source data into CSV files. 
- [03_profiling](./03_profiling/README.md)
  - General data profiling, statistical profiling and quantification of imbalance. 
- [04_mitigating_imbalance](./04_mitigating_imbalance/README.md)
  - Apply mitigation techniques to create final datasets.  
