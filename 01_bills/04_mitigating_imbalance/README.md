# 04_Mitigating_Imbalance

This directory holds the code for applying mitigation techniques to Pandas dataframes which is to be run following the creation of dataframes using the scripts in [02_gathering](02_gathering).

### Script explanation

1. [apply_resampling.py](apply_resampling.py)

Creates and saves a dataframe after an imbalance mitigation technique has been applied to the original dataset specified. The techniques which can be applied are random undersampling, k-nearest-neighbors undersampling, nearmiss undersampling and random oversampling.


2. [apply_multiple_resampling.py](apply_multiple_resampling.py)

Same as `apply_resampling.py` however it applies two specified mitigation techniques one after another. 


## How to run
Ensure arguments in `config.py` file are correct for each resampling method.

Activate suitable environment. If using a uv venv, run `uv run <script_name.py>` including any relevant arguments if not already edited in the scripts.

