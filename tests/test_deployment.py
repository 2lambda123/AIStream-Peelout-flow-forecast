import os
import json
from flood_forecast.deployment.inference import load_model, convert_to_torch_script, InferenceMode
import unittest
from datetime import datetime


class InferenceTests(unittest.TestCase):
    def setUp(self):
        """
        Modules to test model inference.
        """
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")) as y:
            self.config_test = json.load(y)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "multi_config.json")) as y:
            self.multi_config_test = json.load(y)
        self.new_csv_path = "gs://flow_datasets/Massachusetts_Middlesex_County.csv"
        self.weight_path = "gs://coronaviruspublicdata/experiments/01_July_202009_44PM_model.pth"
        self.multi_path = "gs://flow_datasets/miami_multi.csv"
        self.multi_weight_path = "gs://coronaviruspublicdata/experiments/28_January_202102_14AM_model.pth"
        self.infer_class = InferenceMode(20, 30, self.config_test, self.new_csv_path, self.weight_path, "covid-core")

    def test_load_model(self):
        model = load_model(self.config_test, self.new_csv_path, self.weight_path)
        self.assertIsInstance(model, object)
        convert_to_torch_script(model, "test.pt")

    def test_infer_mode(self):
        # Test inference
        self.infer_class.infer_now(datetime(2020, 6, 1), self.new_csv_path)

    def test_plot_model(self):
        self.infer_class.make_plots(datetime(2020, 5, 1), self.new_csv_path, "flow_datasets", "tes1/t.csv", "prod_plot")

    def test_infer_multi(self):
        infer_multi = InferenceMode(20, 30, self.multi_config_test, self.multi_path, self.multi_weight_path,
                                    "covid-core")
        infer_multi.make_plots(datetime(2020, 12, 10), csv_bucket="flow_datasets",
                               save_name="tes1/t2.csv", wandb_plot_id="prod_plot")

    def test_speed(self):
        pass

if __name__ == "__main__":
    unittest.main()
