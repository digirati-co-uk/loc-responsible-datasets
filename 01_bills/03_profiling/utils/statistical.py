import numpy as np
import pandas as pd

from typing import Union
from itertools import combinations

import scipy.stats as stats

import matplotlib.pyplot as plt
import seaborn as sns


def get_dataframe_copy(dataframe: pd.DataFrame, attributes: Union[str, list]):
    """
    Returns a deep copy of an input DataFrame such that the original dataframe is preserved and untouched.
    Modifications are to be applied to returned deep copy.
    """
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


def calculate_cardinality(
    dataframe: pd.DataFrame,
    attributes: list = ["billType", "legislativeSubjects", "policyArea"],
):
    """
    Takes in dataframe and returns cardinality (number of unique values for each column)
    """
    dataframe_copy = get_dataframe_copy(dataframe, attributes)
    cardinality = dataframe_copy.nunique()
    return cardinality


def calculate_class_ratio(dataframe: pd.DataFrame, attribute: str, n: int = 3):
    """
    Takes in dataframe and attribute
    Returns class ratios (proportion of each value), most and least dominant values

    """
    dataframe_copy = dataframe.copy(deep=True)
    if isinstance(dataframe.iloc[0][attribute], list):
        dataframe_copy = dataframe_copy.explode(attribute, ignore_index=True)

    # class ratio (proportion of each value)
    class_ratio = dataframe_copy[attribute].value_counts(normalize=True)

    print(f"Most dominant values in {attribute}:\n{class_ratio[:n]}\n")
    print(f"Least dominant values in {attribute}:\n{class_ratio[-n:]}")
    return class_ratio


def analyze_bias_crosstab(
    dataframe: pd.DataFrame, attributes: list, n: int = None, normalize: bool = True
):
    dataframe_copy = get_dataframe_copy(dataframe, attributes)

    attr1, attr2 = attributes

    if n:
        top_attr1 = dataframe_copy[attr1].value_counts()[:n].index
        top_attr2 = dataframe_copy[attr2].value_counts()[:n].index
        dataframe_copy = dataframe_copy[
            dataframe_copy[attr1].isin(top_attr1)
            & dataframe_copy[attr2].isin(top_attr2)
        ]

    frequency_matrix = pd.crosstab(
        dataframe_copy[attr1], dataframe_copy[attr2], normalize=True
    )
    if normalize:
        frequency_matrix = frequency_matrix.div(frequency_matrix.sum(axis=1), axis=0)

    # Plot heatmap
    plt.figure(figsize=(10, 10))
    sns.heatmap(frequency_matrix, cmap="viridis", annot=True)
    plt.title(f"{attr1} vs. {attr2} Co-occurence Heatmap")
    plt.xlabel(f"{attr2}")
    plt.ylabel(f"{attr1}")
    plt.show()


def calculate_gini_index(dataframe: pd.DataFrame, attribute: str):
    """
    Takes dataframe and attribute and returns the gini index
    0 -> pure distribution (only one category)
    1 -> high impurity (randomly distributed across various classes)
    """
    dataframe_copy = get_dataframe_copy(dataframe, attribute)

    class_ratios = dataframe_copy[attribute].value_counts(normalize=True)

    gini_index = 1 - sum(class_ratios**2)

    return round(gini_index, 4)


def plot_gini_indexes(dataframe: pd.DataFrame, attributes: list):
    """
    Plot bar chart of gini indexes for all attributes given
    """

    gini_indexes = {attr: calculate_gini_index(dataframe, attr) for attr in attributes}

    gini_df = pd.DataFrame(
        list(gini_indexes.items()), columns=["Attribute", "Gini Index"]
    )

    plt.figure(figsize=(8, 6))
    sns.barplot(
        x="Attribute", y="Gini Index", data=gini_df, palette="viridis", hue="Gini Index"
    )
    plt.xlabel("Attribute")
    plt.ylabel("Gini Index")
    plt.title("Gini Index for Categorical Attributes")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def calculate_entropy(dataframe: pd.DataFrame, attribute: str):
    """
    Returns the (shannon - log2) entropy for an attribute
    Higher entropy -> more diverse distribution
    Lower entropy -> more dominated by a single category
    """
    dataframe_copy = get_dataframe_copy(dataframe, attribute)

    value_counts = dataframe_copy[attribute].value_counts(normalize=True)

    entropy = -sum(value_counts * np.log2(value_counts))
    return round(entropy, 4)


def plot_entropies(dataframe: pd.DataFrame, attributes: list):
    """
    Returns bar chart to display (Shannon) entropies for all attributes givens
    """
    entropies = {attr: calculate_entropy(dataframe, attr) for attr in attributes}

    entropy_df = pd.DataFrame(list(entropies.items()), columns=["Attribute", "Entropy"])

    # Plot
    plt.figure(figsize=(8, 6))
    sns.barplot(
        x="Attribute", y="Entropy", data=entropy_df, palette="coolwarm", hue="Entropy"
    )
    plt.xlabel("Attribute")
    plt.ylabel("Entropy")
    plt.title("Shannon Entropy for Categorical Attributes")
    plt.xticks(rotation=45)
    plt.show()


def chi_squared_test(dataframe: pd.DataFrame, attributes: list):
    """
    Returns Chi-squared test of independent between attributes
    If chi-squares stat is high and p-value 0: reject null H0 (meaning attributes are strongely dependent)
    Large DoF suggest test is applied to complex dataset with many categories
    """
    dataframe_copy = get_dataframe_copy(dataframe, attributes)

    attr1, attr2 = attributes
    contingency_table = pd.crosstab(dataframe_copy[attr1], dataframe_copy[attr2])

    chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    return {
        "Chi2 Statistic": round(chi2_stat, 4),
        "P-value": round(p_value, 4),
        "Degrees of Freedom": round(dof, 4),
        # "Expected Frequencies": expected,
    }


def find_association(cramers_v):
    bounds = {
        "Very weak/ no": (0, 0.11),
        "Weak": (0.11, 0.31),
        "Moderate": (0.31, 0.51),
        "Strong": (0.51, 1.00),
    }

    if cramers_v == 1.00:
        return "Perfect"
    else:
        for association, (lower, upper) in bounds.items():
            if lower <= cramers_v < upper:
                return association

    return "Not within bounds"


def calculate_cramers_v(
    dataframe: pd.DataFrame, attributes: list, print_statement: bool = True
):
    """
    Returns Cramer's V (size measurement for the chi-squared test of independence):
    0.00 - 0.10 -> Very weak/no association
    0.11 - 0.30 -> Weak association
    0.31 - 0.50 -> Moderate association
    0.51 - 0.99 -> Strong association
    1.00 -> Perfect association
    """
    dataframe_copy = dataframe.copy(deep=True)
    for attribute in attributes:
        if isinstance(dataframe.iloc[0][attribute], list):
            dataframe_copy = dataframe_copy.explode(attribute, ignore_index=True)

    attr1, attr2 = attributes
    contingency_table = pd.crosstab(dataframe_copy[attr1], dataframe_copy[attr2])

    chi2_stat, _, _, _ = stats.chi2_contingency(contingency_table)

    N = contingency_table.sum().sum()
    k = min(contingency_table.shape)

    cramers_v = np.sqrt(chi2_stat / (N * (k - 1))) if k > 1 else 0
    association = find_association(cramers_v)

    if print_statement:
        print(
            f"{attr1} and {attr2}: \nCramer's V: {round(cramers_v, 4)} \nAssociation: {association} association"
        )
        return

    return cramers_v, association


def plot_cramers_v_heatmap(dataframe, attributes):
    """
    Returns heat map to display Cramer's V and relationship strength between all attributes
    """
    cramers_v_matrix = pd.DataFrame(index=attributes, columns=attributes)
    label_matrix = pd.DataFrame(index=attributes, columns=attributes, dtype=str)

    for attr1, attr2 in combinations(attributes, 2):
        cramers_v, association = calculate_cramers_v(
            dataframe, [attr1, attr2], print_statement=False
        )
        cramers_v_matrix.loc[attr1, attr2] = cramers_v
        cramers_v_matrix.loc[attr2, attr1] = cramers_v  # Mirror the matrix

        label_text = f"{cramers_v:.2f}\n({association})"
        label_matrix.loc[attr1, attr2] = label_text
        label_matrix.loc[attr2, attr1] = label_text

    np.fill_diagonal(cramers_v_matrix.values, 1.0)
    np.fill_diagonal(label_matrix.values, "1.00\n(Perfect)")
    cramers_v_matrix = cramers_v_matrix.astype(float)

    # Plot heatmap
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(
        cramers_v_matrix,
        annot=label_matrix.values,
        fmt="",
        cmap="viridis",
        vmin=0,
        vmax=1,
        linewidths=0.5,
    )
    plt.title("Cramér's V Heatmap with Association Labels")
    plt.show()
