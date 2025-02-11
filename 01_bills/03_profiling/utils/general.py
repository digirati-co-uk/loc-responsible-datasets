import numpy as np
import pandas as pd
import collections

from itertools import combinations
from collections import Counter

import matplotlib.pyplot as plt
import seaborn as sns


def get_dataframe_copy(dataframe, attributes):
    if isinstance(attributes, str):
        if isinstance(dataframe.iloc[0][attributes], list):
            dataframe_copy = dataframe.explode(attributes, ignore_index=True)
            return dataframe_copy
        else:
            dataframe_copy = dataframe.copy(deep=True)
            return dataframe_copy

    else:
        for attribute in attributes:
            dataframe_copy = get_dataframe_copy(dataframe, attribute)
            dataframe = dataframe_copy

    return dataframe_copy


def count_bar_plot(dataframe: pd.DataFrame, attribute: str, n: int = None):
    dataframe_copy = get_dataframe_copy(dataframe=dataframe, attributes=attribute)
    count_df = pd.DataFrame(dataframe_copy[attribute].value_counts())
    if n:
        count_df = count_df.iloc[:n]

    # Plot bar plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x="count", y=attribute, data=count_df, palette="viridis", hue=attribute)
    plt.xlabel("Number of Bills")
    plt.ylabel(attribute)
    plt.title(f"Count of Bills per {attribute}")  # Counts of Categorical Values
    plt.show()


def calculate_count_distribution(
    dataframe: pd.DataFrame, attribute: str, n: int = None
):
    dataframe_copy = get_dataframe_copy(dataframe, attribute)

    series = dataframe_copy[attribute]
    summary_stats = series.describe()
    print(f"Summary Stats for {attribute}:\n{summary_stats}\n")

    if n:
        top_n_values = series.value_counts()[:n]
        print(f"Top {n} Most Frequent: {top_n_values}\n")


def frequency_bar_plot(dataframe: pd.DataFrame, attribute: str = "legislativeSubjects"):
    if type(dataframe.iloc[0][attribute]) != list:
        print(f"No frequencies to calculate for {attribute}")
        return

    frequency_attribute = f"frequency_{attribute}"
    dataframe_copy = dataframe.copy(deep=True)
    dataframe_copy[frequency_attribute] = dataframe_copy[attribute].apply(
        lambda x: len(x)
    )

    count_df = pd.DataFrame(dataframe_copy[frequency_attribute].value_counts())

    # Plot bar plot
    plt.figure(figsize=(10, 6))
    sns.barplot(
        y="count",
        x=frequency_attribute,
        data=count_df,
        palette="viridis",
        hue=frequency_attribute,
    )
    plt.ylabel("Number of Bills")
    plt.xlabel(f"Number of {attribute}")
    plt.title(f"Frequency of {attribute}")  # Counts of Categorical Values
    plt.show()


def calculate_frequency_distribution(dataframe: pd.DataFrame, attribute: str):
    dataframe_copy = get_dataframe_copy(dataframe, attribute)

    series = dataframe_copy[attribute]

    frequency_summary_stats = series.value_counts().describe()
    print(f"Summary Stats for Counts for {attribute}:\n{frequency_summary_stats}\n")


def cross_tabulation_heatmap(dataframe: pd.DataFrame, attributes: list, n: int = None):
    dataframe_copy = get_dataframe_copy(dataframe, attributes)

    attr1, attr2 = attributes

    if n:
        top_attr1 = dataframe_copy[attr1].value_counts()[:n].index
        top_attr2 = dataframe_copy[attr2].value_counts()[:n].index
        dataframe_copy = dataframe_copy[
            dataframe_copy[attr1].isin(top_attr1)
            & dataframe_copy[attr2].isin(top_attr2)
        ]

    frequency_matrix = pd.crosstab(dataframe_copy[attr1], dataframe_copy[attr2])
    # Plot heatmap
    plt.figure(figsize=(10, 10))
    sns.heatmap(frequency_matrix, cmap="viridis", annot=True, fmt="d")
    plt.title(f"{attr1} vs. {attr2} Co-occurence Heatmap")
    plt.xlabel(f"{attr2}")
    plt.ylabel(f"{attr1}")
    plt.show()


def frequent_combination_heatmap(
    dataframe: pd.DataFrame, attribute: str = "legislativeSubjects", top_n: int = 30
):
    pairs = []
    for values in dataframe[attribute]:
        if isinstance(values, list) and len(values) > 2:
            pairs.extend(combinations(values, 2))
    pair_counts = Counter(pairs)

    most_common_pairs = pair_counts.most_common(top_n)
    unique_subjects = list(set([s for pair, _ in most_common_pairs for s in pair]))
    co_occurrence_matrix = pd.DataFrame(
        np.zeros((len(unique_subjects), len(unique_subjects))),
        index=unique_subjects,
        columns=unique_subjects,
    )

    for (subj1, subj2), count in most_common_pairs:
        co_occurrence_matrix.loc[subj1, subj2] = count
        co_occurrence_matrix.loc[subj2, subj1] = count

    # Plot heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        co_occurrence_matrix, annot=True, cmap="viridis", fmt=".0f", linewidths=0.5
    )
    plt.title(f"Top {top_n} Frequent Co-Occurrences in {attribute}")
    plt.show()
