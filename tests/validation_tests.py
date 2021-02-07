import unittest
import torch
import os
# import numpy as np
from flood_forecast.pytorch_training import compute_validation
from flood_forecast.custom.custom_opt import MAPELoss
from flood_forecast.custom.dilate_loss import DilateLoss
from flood_forecast.time_model import PyTorchForecast
# from torch.utils.data import DataLoader


class TestValidationLogic(unittest.TestCase):
    def setUp(self):
        self.test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_init")
        self.model_params = {
            "metrics": ["MSE", "MAPE"],
            "model_params": {
                "number_time_series": 3,
                "forecast_length": 10,
                "seq_len": 20},
            "dataset_params": {
                "forecast_history": 20,
                "class": "default",
                "forecast_length": 10,
                "forecast_test_len": 100,
                "relevant_cols": [
                    "cfs",
                    "temp",
                    "precip"],
                "scaler": "StandardScaler",
                "target_col": ["cfs"],
                "interpolate": False},
            "training_params": {
                "optimizer": "Adam",
                "lr": .1,
                "criterion": "MSE",
                "epochs": 1,
                "batch_size": 2,
                "optim_params": {}},
            "wandb": False,
            "inference_params": {
                "hours_to_forecast": 10}}
        self.baseline_model_params = {
            "metrics": ["MSE", "DilateLoss"],
            "model_params": {
                "forecast_length": 10},
            "dataset_params": {
                "forecast_history": 20,
                "class": "default",
                "forecast_length": 10,
                "forecast_test_len": 100,
                "relevant_cols": [
                    "cfs",
                    "temp",
                    "precip"],
                "scaler": "StandardScaler",
                "target_col": ["cfs"],
                "interpolate": False},
            "training_params": {
                "optimizer": "Adam",
                "lr": .1,
                "criterion": "MSE",
                "epochs": 1,
                "batch_size": 2,
                "optim_params": {}},
            "wandb": False,
            "inference_params": {
                "hours_to_forecast": 10}}
        self.keag_file = os.path.join(self.test_path, "keag_small.csv")
        self.model_m = PyTorchForecast("MultiAttnHeadSimple", self.keag_file, self.keag_file,
                                       self.keag_file, self.model_params)
        self.model_dumb = PyTorchForecast("DummyTorchModel", self.keag_file, self.keag_file, self.keag_file,
                                          self.baseline_model_params)

    def test_compute_validation(self):
        d = torch.utils.data.DataLoader(self.model_m.test_data)
        s, u = compute_validation(d, self.model_m.model, 0, 10, [torch.nn.MSELoss(), MAPELoss()], "cpu",
                                  True, val_or_test="test_loss")
        result_values = list(s.values())
        unscale_result_values = list(u.values())
        # numpy_arr = np.full(shape=1, fill_value=result_values[0], dtype=np.float).reshape(-1, 1)
        # numpy_arr2 = np.full(shape=1, fill_value=result_values[1], dtype=np.float).reshape(-1, 1)
        # unscale_mse = self.model_m.test_data.inverse_scale(numpy_arr)
        # unscale_mape = self.model_m.test_data.inverse_scale(numpy_arr2)
        self.assertEqual(len(result_values), 2)
        # Each of these represents a specific bug that was found earlier.
        self.assertNotAlmostEqual(result_values[0], result_values[1])
        self.assertNotAlmostEqual(result_values[0], result_values[1] * 2)
        self.assertNotAlmostEqual(unscale_result_values[0], unscale_result_values[1])
        self.assertNotAlmostEqual(unscale_result_values[0], unscale_result_values[1] * 2)
        # Todo figure out why these aren't working
        # self.assertAlmostEqual(float(unscale_mse.numpy()[0]), unscale_result_values[0])
        # self.assertAlmostEqual(float(unscale_mape.numpy()[0]), unscale_result_values[1])

    def test_naieve(self):
        d = torch.utils.data.DataLoader(self.model_dumb.test_data)
        s, u = compute_validation(d, self.model_m.model, 0, 10, [DilateLoss(), torch.nn.MSELoss()], "cpu",
                                  True, val_or_test="test_loss")
        s2, u2 = compute_validation(d, self.model_m.model, 0, 10, [torch.nn.MSELoss(), DilateLoss()], "cpu",
                                    True, val_or_test="test_loss")
        s3, u3 = compute_validation(d, self.model_m.model, 0, 10, [DilateLoss()], "cpu",
                                    True, val_or_test="test_loss")
        result_values = list(s.values())
        unscale_result_values = list(u.values())
        result_values2 = list(s2.values())
        unscale_result_values2 = list(u2.values())
        unscale_result_values_solo = list(u3.values())
        scaled_s3 = list(s3.values())
        self.assertEqual(result_values[0], result_values2[1])
        self.assertEqual(unscale_result_values_solo[0], unscale_result_values[0])
        self.assertEqual(unscale_result_values_solo[0], unscale_result_values[0])
        self.assertEqual(scaled_s3[0], result_values[0])
        self.assertEqual(unscale_result_values[1], unscale_result_values2[0])
        self.assertNotAlmostEqual(unscale_result_values[0], unscale_result_values[1] * 2)
        self.assertGreater(result_values[1], result_values[0])
        self.assertLess(unscale_result_values[0], unscale_result_values[1])

if __name__ == '__main__':
    unittest.main()
