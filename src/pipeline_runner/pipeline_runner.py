import importlib
from typing import List, Callable, Dict, Any
from functools import reduce


class PipelineRunner:
    def __init__(self, config_module: str, steps_module: str):
        self.config_module = config_module
        self.steps_module = steps_module
        self.steps = self.load_steps()
        self.step_functions = self.load_step_functions()

    def load_steps(self) -> List[Dict[str, Any]]:
        config = importlib.import_module(self.config_module)
        return config.pipeline_steps

    def load_step_functions(self) -> Dict[str, Callable]:
        steps_module = importlib.import_module(self.steps_module)
        return {name: func for name, func in vars(steps_module).items() if callable(func)}

    def run_pipeline(self, data: str) -> str:
        def iterator(accumulated_data, step):
            step_name = step['name']
            func = self.step_functions[step_name]
            config = step.get('config', None)
            try:
                print(f"Running {step_name}")
                if config:
                    return func(accumulated_data, config)
                else:
                    return func(accumulated_data)
            except Exception as e:
                print(f"Error in {step_name}: {e}")
                raise

        print(reduce(iterator, self.steps, data))
