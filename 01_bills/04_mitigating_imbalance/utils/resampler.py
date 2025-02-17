import logging

import pandas as pd

from typing import Union
from imblearn.under_sampling import (
    RandomUnderSampler,
    NeighbourhoodCleaningRule,
    NearMiss,
)
from imblearn.over_sampling import RandomOverSampler

from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


def get_dataframe_copy(dataframe: pd.DataFrame, attributes: Union[str, list]):
    """
    Returns a deep copy of an input DataFrame such that the original dataframe is preserved and untouched.
    Modifications are to be applied to returned deep copy.
    """
    if isinstance(attributes, str):
        dataframe_copy = dataframe.copy(deep=True)

        if isinstance(dataframe.iloc[0][attributes], list):
            dataframe_copy[attributes] = dataframe_copy[attributes].apply(
                lambda x: x if x else ["Empty"]
            )
            dataframe_copy = dataframe_copy.explode(attributes, ignore_index=True)
            return dataframe_copy

        return dataframe_copy

    else:
        for attribute in attributes:
            dataframe_copy = get_dataframe_copy(dataframe, attribute)
            dataframe = dataframe_copy

    return dataframe_copy


class Resampler(object):
    def __init__(self, dataset: pd.DataFrame, random_state: int = 42):
        self.dataset = dataset
        self.random_state = random_state

    # UNDERSAMPLING
    def random_undersampling(
        self,
        attribute_to_balance: str,
        sampling_strategy: str = "auto",
        replacement: bool = False,
        # min_count: int = None,
    ):
        """
        Under-sample the majority class(es) by randomly picking samples with or without replacement

        Sampling strategy:
        'majority': resample only the majority class;
        'not minority': resample all classes but the minority class;
        'not majority': resample all classes but the majority class;
        'all': resample all classes;
        'auto': equivalent to 'not minority'.
        """

        dataframe_copy = get_dataframe_copy(self.dataset, attribute_to_balance)
        # if not min_count:
        #     subject_counts = dataframe_copy[attribute_to_balance].value_counts()
        #     min_count = subject_counts.min()

        X = dataframe_copy.drop(columns=attribute_to_balance)
        y = dataframe_copy[attribute_to_balance]

        rus = RandomUnderSampler(
            sampling_strategy=sampling_strategy,
            random_state=self.random_state,
            replacement=replacement,
        )
        X_resampled, y_resampled = rus.fit_resample(X, y)
        df_resampled = pd.DataFrame(X_resampled)
        df_resampled[attribute_to_balance] = y_resampled

        if isinstance(self.dataset.iloc[0][attribute_to_balance], list):
            features = list(dataframe_copy.columns)
            features.remove(attribute_to_balance)
            df_resampled = (
                df_resampled.groupby(features)[attribute_to_balance]
                .apply(list)
                .reset_index()
            )

        return df_resampled

    def knn_undersampling(
        self,
        attribute_to_balance: str,
        sampling_strategy: str = "auto",
        n_neighbors: int = 3,
    ):
        """
        Under-samples based on NearMiss methods

        Sampling strategy:
        'majority': resample only the majority class;
        'not minority': resample all classes but the minority class;
        'not majority': resample all classes but the majority class;
        'all': resample all classes;
        'auto': equivalent to 'not minority'
        """
        dataframe_copy = get_dataframe_copy(self.dataset, attribute_to_balance)
        label_encoder = LabelEncoder()
        dataframe_copy[f"{attribute_to_balance}"] = label_encoder.fit_transform(
            dataframe_copy[attribute_to_balance]
        )

        features = list(dataframe_copy.columns)
        features.remove(attribute_to_balance)

        encoders = {}
        for feature in features:
            if isinstance(dataframe_copy.iloc[0][feature], str):
                encoders[f"{feature}_encoded"] = LabelEncoder()
                encoder = encoders[f"{feature}_encoded"]
                dataframe_copy[feature] = encoder.fit_transform(dataframe_copy[feature])

        X = dataframe_copy.drop(columns=attribute_to_balance)
        y = dataframe_copy[attribute_to_balance]

        encoders = {}
        for col in list(X.columns):
            if isinstance(X.iloc[0][col], str):
                encoders[f"{col}_encoded"] = LabelEncoder()
                encoder = encoders[f"{col}_encoded"]
                X[col] = encoder.fit_transform(X[col])

        nm = NeighbourhoodCleaningRule(
            n_neighbors=n_neighbors, sampling_strategy=sampling_strategy
        )
        X_resampled, y_resampled = nm.fit_resample(X, y)
        y_resampled_decoded = label_encoder.inverse_transform(y_resampled)

        df_resampled = pd.DataFrame(X_resampled)
        df_resampled[attribute_to_balance] = y_resampled_decoded

        for col_, encoder_ in encoders.items():
            original_col = col_.split("_")[0]
            df_resampled[original_col] = encoder_.inverse_transform(
                df_resampled[original_col]
            )

        if isinstance(self.dataset.iloc[0][attribute_to_balance], list):
            features = list(dataframe_copy.columns)
            features.remove(attribute_to_balance)
            df_resampled = (
                df_resampled.groupby(features)[attribute_to_balance]
                .apply(list)
                .reset_index()
            )

        return df_resampled

    def near_miss_undersampling(
        self,
        attribute_to_balance: str,
        sampling_strategy: str = "auto",
        n_neighbors: int = 3,
    ):
        """
        Under-samples based on NearMiss methods

        Sampling strategy:
        'majority': resample only the majority class;
        'not minority': resample all classes but the minority class;
        'not majority': resample all classes but the majority class;
        'all': resample all classes;
        'auto': equivalent to 'not minority'
        """
        dataframe_copy = get_dataframe_copy(self.dataset, attribute_to_balance)
        label_encoder = LabelEncoder()
        dataframe_copy[f"{attribute_to_balance}"] = label_encoder.fit_transform(
            dataframe_copy[attribute_to_balance]
        )

        features = list(dataframe_copy.columns)
        features.remove(attribute_to_balance)

        encoders = {}
        for feature in features:
            if isinstance(dataframe_copy.iloc[0][feature], str):
                encoders[f"{feature}_encoded"] = LabelEncoder()
                encoder = encoders[f"{feature}_encoded"]
                dataframe_copy[feature] = encoder.fit_transform(dataframe_copy[feature])

        X = dataframe_copy.drop(columns=attribute_to_balance)
        y = dataframe_copy[attribute_to_balance]

        encoders = {}
        for col in list(X.columns):
            if isinstance(X.iloc[0][col], str):
                encoders[f"{col}_encoded"] = LabelEncoder()
                encoder = encoders[f"{col}_encoded"]
                X[col] = encoder.fit_transform(X[col])

        subject_counts = y.value_counts()
        min_class_count = subject_counts.min()
        n_neighbors = (
            min(n_neighbors, min_class_count - 1) if min_class_count > 1 else 1
        )  # Avoid n_neighbors > class samples

        nm = NearMiss(n_neighbors=n_neighbors, sampling_strategy=sampling_strategy)
        X_resampled, y_resampled = nm.fit_resample(X, y)
        y_resampled_decoded = label_encoder.inverse_transform(y_resampled)

        df_resampled = pd.DataFrame(X_resampled)
        df_resampled[attribute_to_balance] = y_resampled_decoded

        for col_, encoder_ in encoders.items():
            original_col = col_.split("_")[0]
            df_resampled[original_col] = encoder_.inverse_transform(
                df_resampled[original_col]
            )

        if isinstance(self.dataset.iloc[0][attribute_to_balance], list):
            features = list(dataframe_copy.columns)
            features.remove(attribute_to_balance)
            df_resampled = (
                df_resampled.groupby(features)[attribute_to_balance]
                .apply(list)
                .reset_index()
            )

        return df_resampled

    def tomek_links(
        self,
    ):
        # only works on numerical data
        pass

    # OVERSAMPLING
    def random_oversampling(
        self,
        attribute_to_balance: str,
        sampling_strategy: str = "auto",
    ):
        """
        Over-sample the minority class(es) by randomly picking samples with or without replacement

        Sampling strategy:
        'minority': resample only the minority class;
        'not minority': resample all classes but the minority class;
        'not majority': resample all classes but the majority class;
        'all': resample all classes;
        'auto': equivalent to 'not majority'.
        """

        dataframe_copy = get_dataframe_copy(self.dataset, attribute_to_balance)

        X = dataframe_copy.drop(columns=attribute_to_balance)
        y = dataframe_copy[attribute_to_balance]

        ros = RandomOverSampler(
            sampling_strategy=sampling_strategy,
            random_state=self.random_state,
        )
        X_resampled, y_sampled = ros.fit_resample(X, y)

        df_resampled = pd.DataFrame(X_resampled)
        df_resampled[attribute_to_balance] = y_sampled

        if isinstance(self.dataset.iloc[0][attribute_to_balance], list):
            features = list(dataframe_copy.columns)
            features.remove(attribute_to_balance)
            df_resampled = (
                df_resampled.groupby(features)[attribute_to_balance]
                .apply(list)
                .reset_index()
            )

        return df_resampled

    def smote(
        self,
    ):
        # only works on continuous data
        pass

    def smote_nc(
        self,
    ):
        # categorical and continous combo,
        # does not work well on data consisting of only continous
        pass
