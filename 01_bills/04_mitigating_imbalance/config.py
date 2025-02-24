ARGUMENTS = {
    "basic_random_undersampling": {
        "sampling_strategy": "auto",
        "replacement": False,
        "min_count": None,
    },
    "basic_knn_undersampling": {
        "sampling_strategy": "auto",
        "n_neighbors": 3,
        "features_to_remove": None,
    },
    "knn_undersampling_with_associated_features": {
        "sampling_strategy": "auto",
        "n_neighbors": 3,
        "features_to_remove": ["congress", "billType", "billNumber", "billText"],
    },
    "basic_near_miss_undersampling": {
        "sampling_strategy": "auto",
        "n_neighbors": 3,
        "features_to_remove": None,
    },
    "near_miss_undersampling_with_associated_features": {
        "sampling_strategy": "auto",
        "n_neighbors": 3,
        "features_to_remove": ["congress", "billType", "billNumber", "billText"],
    },
    "basic_random_oversampling": {
        "sampling_strategy": "auto",
        "max_count": 5,
    },
    "rus_ros": [
        {
            "sampling_strategy": "auto",
            "replacement": False,
            "min_count": 50,
        },
        {
            "sampling_strategy": "auto",
            "max_count": 5,
        },
    ],
    "ros_rus": [
        {
            "sampling_strategy": "auto",
            "max_count": 5,
        },
        {
            "sampling_strategy": "auto",
            "replacement": False,
            "min_count": 50,
        },
    ],
}
