from random import Random
from v3io_generator.metric.metric import Metric


class Metric_Group:

    def __init__(self, metrics: dict, initial_values: dict = {},
                 error_rate_ticks: int = 0,
                 error_length_ticks: int = 0):
        '''
            Component Manager:
            Receives configuration dictionary and -
                - Creates metrics
                - Runs scenarios
        :param metrics: Configuration dictionary
        '''

        # Error handling
        self.error_rate_in_percentage = (1 / error_rate_ticks)
        self.error_length_in_ticks = error_length_ticks
        self.is_error = False
        self.steps = 0
        self.current_error_length = 0
        self.scenario = {}

        # Metrics definition
        self.metrics = {metric_name: Metric(metric_config,
                                            initial_value=initial_values.setdefault(metric_name, 0)) for
                        metric_name, metric_config in metrics.items()}

        self.r = Random()

        self.total_steps = 0

    def notify_metric_of_error(self):
        [component.start_error(self.error_length_in_ticks - self.steps) for metric_name, component in self.metrics.items()
         if self.steps == self.scenario[metric_name]]

    def notify_metrics_of_normalization(self):
        [component.stop_error() for component in self.metrics.values()]

    def generate(self):
        # Initialize state

        # Main generator loop
        while True:
            # Check if we are in an error state (Prev or New)
            self.is_error = True if (
                    (self.is_error is False) and self.r.uniform(0,
                                                                1) <= self.error_rate_in_percentage) else self.is_error

            # If we are in error
            if self.is_error:
                #print(f'Error ({self.steps}/{self.error_length_in_ticks})')

                # If this is the first error step
                if self.steps == 0:
                    # Initialize error
                    self.current_error_length = int(
                        self.r.gauss(mu=self.error_length_in_ticks, sigma=0.1 * self.error_length_in_ticks))
                    self.scenario = {metric_name: int(self.current_error_length * 0.1 * counter) for counter, metric_name in
                                     enumerate(self.metrics.keys())}

                    # Do we need to notify a metric to start an error state?
                    self.notify_metric_of_error()

                    # Advance steps
                    self.steps += 1

                # If we are already in an error state, do we need to stop?
                elif self.steps == self.error_length_in_ticks:
                    # Change internal state
                    self.is_error = False
                    self.steps = 0
                    # Notify metrics
                    self.notify_metrics_of_normalization()

                # Normal in-error step
                else:
                    self.notify_metric_of_error()
                    self.steps += 1

            # If we are not in Error state
            # Generate actual metric
            self.total_steps += 1
            metrics = {component_name: next(metric.generator()) for component_name, metric in self.metrics.items()}
            new_metric = {}
            for metric_name, metric_values in metrics.items():
                for value_name, value in metric_values.items():
                    new_metric[f'{metric_name}_{value_name}' if value_name != 'value' else metric_name] = value
            yield new_metric
