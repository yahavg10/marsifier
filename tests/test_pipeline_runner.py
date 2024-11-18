import unittest
from unittest.mock import patch, MagicMock

from src.pipeline_runner.pipeline_runner import PipelineRunner


class TestPipelineRunner(unittest.TestCase):

    @patch("src.pipeline_runner.pipeline_runner.importlib.import_module")
    def test_load_steps(self, mock_import_module):
        mock_import_module.return_value.pipeline_steps = [{"name": "step1"}, {"name": "step2"}]
        runner = PipelineRunner("config_module", "steps_module")

        steps = runner.load_steps()

        self.assertEqual(steps, [{"name": "step1"}, {"name": "step2"}])
        mock_import_module.assert_called_with("config_module")

    @patch("src.pipeline_runner.pipeline_runner.importlib.import_module")
    def test_load_step_functions(self, mock_import_module):
        mock_steps_module = MagicMock()
        mock_steps_module.func1 = lambda x: x
        mock_steps_module.func2 = lambda y: y
        mock_import_module.return_value = mock_steps_module
        runner = PipelineRunner("config_module", "steps_module")

        step_functions = runner.load_step_functions()

        self.assertIn("func1", step_functions)
        self.assertIn("func2", step_functions)

    @patch("src.pipeline_runner.pipeline_runner.importlib.import_module")
    @patch("src.pipeline_runner.pipeline_runner.reduce")
    def test_run_pipeline(self, mock_reduce, mock_import_module):
        mock_steps_module = MagicMock()
        mock_steps_module.func1 = lambda x: x
        mock_steps_module.func2 = lambda y: y
        mock_import_module.return_value = mock_steps_module
        runner = PipelineRunner("config_module", "steps_module")
        runner.steps = [{"name": "step1"}]
        runner.step_functions = {"step1": MagicMock(return_value="result")}

        runner.run_pipeline("input_data")

        mock_reduce.assert_called_once()


if __name__ == "__main__":
    unittest.main()
