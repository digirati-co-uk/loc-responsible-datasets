# 03_Profiling

This directory holds the code for initial exploratory data analysis (general data profiling) and imbalance quantification (stastical profiling) as well as quanitfication of imbalance post mitigation.


### Pre-mitigation Pofiling
Notebooks [01_general_profiling_visualization.ipynb](01_general_profiling_visualization.ipynb) and [02_statistical_profiling_vizualisation.ipynb](02_stastistical_profiling_visualization.ipynb) are run on the initial dataframe created from the scripts within the [02_gathering](../02_gathering/) directory. 

These notebooks serve as visualization tools for profiling and have helped gain a better understanding of the structure and distribution of the original data, as well as help determine which methods to use for mitigation statistical bias (imbalance), specifically with regard to 'legislativeSubjects'.

### Post-mitigation Profiling
Notebook [03_post_resampling_stat_profiling_visualization.ipynb](03_post_resampling_stat_profiling_visualization.ipynb) is run on the original and resampled dataframes created from the scripts within the [04_mitigation_imbalance](04_mitigating_imbalance) directory. 

This notebook also includes brief explanations of the methods applied and how suitable the resulting dataset is for training an ML-based classification model.


## How to run

To run these notebooks on your own data, ensure that the path(s) to your Pandas DataFrame(s) are changed and that the dataframe(s) contain the same attributes and data types ('congress' - int/str, 'billType' - str, 'billNumber' - int, 'legislativeSubjects' - list of str, 'policyArea'- str, 'billText' -str). 

Run as usual with suitable environment. (Environment requirements: Pandas, Numpy, Matplotlib, Seaborn, SciPy.)