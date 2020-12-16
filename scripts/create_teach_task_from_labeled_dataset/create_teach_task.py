"""
Create a labeled teach task from a labeled dataset using custom graphql queries

This is a work around until the ability to add data to teach tasks is supported
in platform

The dataset used in this example is a labeled csv file for a CW use case
"""
import os
import pandas as pd
import json
from typing import Iterable

from indico import IndicoClient, IndicoConfig
from indico.queries import GraphQLRequest, GetDataset, CreateExport, DownloadExport

from graphql_queries import (
    CREATE_TEACH_TASK,
    GET_TEACH_TASK,
    SUBMIT_QUESTIONNAIRE_EXAMPLE,
)


def create_teach_task(client, dataset_id, teach_task_name, classes):
    dataset = client.call(GetDataset(dataset_id))
    source_col_id = dataset.datacolumn_by_name("text").id
    variables = {
        "name": teach_task_name,
        "processors": [],
        "dataType": "TEXT",
        "datasetId": DATASET_ID,
        "numLabelersRequired": 1,
        "sourceColumnId": source_col_id,
        "questions": [
            {
                "type": "ANNOTATION",
                "targets": classes,
                "keywords": [],
                "text": teach_task_name,
            }
        ],
    }
    teach_task = client.call(
        GraphQLRequest(query=CREATE_TEACH_TASK, variables=variables)
    )
    teach_task_id = teach_task["createQuestionnaire"]["id"]
    variables = {"id": teach_task_id}
    teach_task_stats = INDICO_CLIENT.call(
        GraphQLRequest(query=GET_TEACH_TASK, variables=variables)
    )
    labelset_id = teach_task_stats["questionnaires"]["questionnaires"][0]["questions"][
        0
    ]["labelset"]["id"]
    model_group_id = teach_task_stats["questionnaires"]["questionnaires"][0][
        "questions"
    ][0]["modelGroupId"]
    return labelset_id, model_group_id


def label_teach_task(
    client, dataset_id, labelset_id, model_group_id, label_df, label_col
):
    row_index_col = f"row_index_{dataset_id}"
    for _, row in label_df.iterrows():
        row_index = row[row_index_col]
        labels = row[label_col]
        variables = {
            "datasetId": dataset_id,
            "labelsetId": labelset_id,
            "labels": [
                {
                    "rowIndex": row_index,
                    "target": labels,
                }
            ],
            "modelGroupId": model_group_id,
        }

        client.call(
            GraphQLRequest(query=SUBMIT_QUESTIONNAIRE_EXAMPLE, variables=variables)
        )


def get_label_list(labeled_data_df, label_col) -> Iterable[str]:
    label_set = set()
    for i, row in labeled_data_df.iterrows():
        labels = json.loads(row[label_col])
        for label in labels:
            label_set.add(label["label"])
    return list(label_set)


if __name__ == "__main__":

    # NOTE, Configure
    HOST = os.getenv("INDICO_API_HOST", "cush.indico.domains")

    # NOTE, Configure
    API_TOKEN_PATH = "../../indico_api_token.txt"

    # boiler plate code in every script using indico calls
    with open(API_TOKEN_PATH) as f:
        API_TOKEN = f.read()

    my_config = IndicoConfig(host=HOST, api_token=API_TOKEN, verify_ssl=False)
    INDICO_CLIENT = IndicoClient(config=my_config)

    # NOTE: Configure
    DATASET_ID = 79

    # NOTE: Configure
    TEACH_TASK_NAME = "Test GOS Invoice Task v3.1"

    # NOTE: CONFIGURE
    LABEL_COL = "labels"

    # Get labeled dataset
    export = INDICO_CLIENT.call(
        CreateExport(dataset_id=DATASET_ID, file_info=True, wait=True)
    )
    labeled_data_df = INDICO_CLIENT.call(DownloadExport(export.id))

    # NOTE: Configure - Dummy classes allow for the ability to have label tags in review
    dummy_classes = []

    # NOTE: Configure - label names of all labels in the indico produced model
    model_classes = get_label_list(labeled_data_df, LABEL_COL)
    full_classes = dummy_classes + model_classes

    labelset_id, model_group_id = create_teach_task(
        INDICO_CLIENT, DATASET_ID, TEACH_TASK_NAME, full_classes
    )

    label_teach_task(
        INDICO_CLIENT,
        DATASET_ID,
        labelset_id,
        model_group_id,
        labeled_data_df,
        LABEL_COL,
    )
