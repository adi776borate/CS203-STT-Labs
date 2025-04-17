import mlrun
from cloudpickle import load
import numpy as np
from typing import List

class BreastCancerModel(mlrun.serving.V2ModelServer):
    """
    MLRun Serving Class for the Breast Cancer RandomForest model.
    Inherits from V2ModelServer for standard model serving capabilities.
    """

    def load(self):
        """
        Loads the trained RandomForest model from the specified path using get_model().
        """
        self.context.logger.info(f"Loading model from {self.model_path}...")
        model_file, extra_data = self.get_model('.pkl')
        self.model = load(open(model_file, 'rb'))
        self.context.logger.info("Model loaded successfully.")


    def predict(self, body: dict) -> List:
        """
        Receives prediction requests and returns model predictions.
        Assumes that the 'inputs' key in the body contains a list of feature lists.
        """
        feats = np.asarray(body['inputs'])
        self.context.logger.info(f"Received {feats.shape[0]} samples for prediction.")
        results: np.ndarray = self.model.predict(feats)
        return results.tolist()
