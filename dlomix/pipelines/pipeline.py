import numpy as np
from dlomix.constants import retention_time_pipeline_parameters
from dlomix.data.RetentionTimeDataset import RetentionTimeDataset
from dlomix.models.base import RetentionTimePredictor
from dlomix.reports import RetentionTimeReport
from os.path import join

# pipelines can be used to train the model further or from scratch given a dataset
# add string arguments (e.g. prosit to create the model, data source to create the dataset)

# if neither  train nor test are provided --> use toy datasets to (train if necessary or load pre-trained weights), predict on test, and generate report
# if test only --> load pre-trained weights, predict and generate report
# if train and test --> do what you have to do


class RetentionTimePipeline:
    def __init__(self, pre_trained=True):
        super(RetentionTimePipeline, self).__init__()
        self.model = None
        self.test_dataset = None
        self.pre_trained = pre_trained

        self._build_model()

    def _build_model(self):
        self.model = RetentionTimePredictor(
            **retention_time_pipeline_parameters["model_params"]
        )

        if self.pre_trained:
            self.model.load_weights(
                retention_time_pipeline_parameters["trained_model_path"]
            )

    """
    
    Predict retention times given data either as numpy array of sequences or a filepath to a csv file
    
    """

    def predict(self, data=None):
        if not (isinstance(data, str) or isinstance(data, np.ndarray)):
            raise ValueError(
                "Dataset should be provided either as a numpy array or a string pointing to a file."
            )

        self.test_dataset = RetentionTimeDataset(
            data,
            **retention_time_pipeline_parameters["data_params"],
            val_ratio=0,
            test=True
        )
        (
            self.test_dataset.data_mean,
            self.test_dataset.data_std,
        ) = retention_time_pipeline_parameters["trained_model_stats"]

        predictions = self.model.predict(self.test_dataset.test_data)
        predictions = self.test_dataset.denormalize_targets(predictions)
        predictions = predictions.ravel()

        return predictions

    
    def predict_report(self, data, output_path="./") -> None:
        predictions = self.predict(data)
        report = RetentionTimeReport(output_path=output_path, history=None)

        test_targets = self.test_dataset.get_split_targets(split="test")
        report.generate_report(test_targets, predictions)



