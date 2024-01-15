from flytekit import workflow, task
import pandas as pd


@task
def load_data() -> pd.DataFrame:
    return pd.DataFrame({"column": [1, 2, 3]})


@task
def print_data(data: pd.DataFrame):
    print(data.head())


@workflow
def wf():
    """Put all of the steps together into a single workflow."""
    df = load_data()
    print_data(data=df)
