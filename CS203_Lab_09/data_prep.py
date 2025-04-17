import mlrun
from sklearn.datasets import load_breast_cancer
import pandas as pd

@mlrun.handler(outputs=["dataset", "label_column"])
def data_loader(context, format="csv"):
    """
    Loads the Breast Cancer dataset, prepares a DataFrame, and logs it as an MLRun Dataset artifact.
    """
    context.logger.info("Loading Breast Cancer dataset using sklearn")
    data = load_breast_cancer()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["target"] = data.target

    context.logger.info(f"Dataset shape: {df.shape}")
    context.logger.info(f'Saving dataset artifact using key "breast_cancer_dataset" to {context.artifact_path}')

    # Log the DataFrame as a Dataset artifact
    context.log_dataset("breast_cancer_dataset", df=df, format=format, index=False)

    context.logger.info("Dataset artifact logged successfully")

    return df, "target"

if __name__ == "__main__":
    with mlrun.get_or_create_ctx("data-prep-local", upload_artifacts=True) as context:
        data_loader(context)