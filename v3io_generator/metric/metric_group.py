from random import Random
from v3io_generator.metric import Metric

class Metric_Group:

    def __init__(self, metrics: dict, initial_values: dict={}, start_time: int=0, interval: int=0, stocastic_interval: bool=False):
        '''
            Component Manager:
            Receives configuration dictionary and -
                - Creates metrics
                - Runs scenarios
        :param metrics: Configuration dictionary
        '''
        self.metrics = {metric_name: Metric(metric_config,
                                            initial_value=initial_values.setdefault(metric_name, 0)) for metric_name, metric_config in metrics.items()}

        self.r = Random()

    def generate(self):
        # Initialize state

        # Main generator loop
        while True:
            yield {component_name: next(metric.generator()) for component_name, metric in self.metrics.items()}