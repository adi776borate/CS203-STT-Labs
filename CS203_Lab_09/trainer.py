import mlrun
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from mlrun.frameworks.sklearn import apply_mlrun

# Define the main training function
def train_model(
    context: mlrun.run.MLClientCtx,  
    dataset: mlrun.DataItem,        
    label_column: str = "target",   
    n_estimators: int = 100,        
    max_depth: int = 5,             
    random_state: int = 42,         
    model_name: str = "breast_cancer_classifier"       
):
    """
    Trains a RandomForestClassifier model on the input dataset.

    Uses apply_mlrun to automatically log model, metrics, and artifacts.
    """
    context.logger.info("Starting model training")

    # Load DataFrame from the input DataItem
    context.logger.info(f"Loading data from {dataset.url}")
    df = dataset.as_df()
    context.logger.info(f"Data loaded, shape: {df.shape}")

    # Prepare features (X) and target (y)
    X = df.drop(label_column, axis=1)
    y = df[label_column]
    context.logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)
    context.logger.info(f"Train set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

    # Initialize the RandomForestClassifier model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    context.logger.info(f"Initialized RandomForestClassifier with n_estimators={n_estimators}, max_depth={max_depth}")

    # Log the model and metrics using apply_mlrun
    apply_mlrun(model=model, model_name=model_name, x_test=X_test, y_test=y_test)
    model.fit(X_train, y_train)
    context.logger.info("Training completed and model artifacts logged via apply_mlrun.")