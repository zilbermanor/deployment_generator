from random import Random
from v3io_generator.metric.metrics import normal
from v3io_generator.metric.metrics import poisson
import numpy as np

class Metric:
    '''
        - Define metric parameters
        - Define distribution parameters
        - Define alerts
    '''

    def __init__(self, configuration: dict = dict(), initial_value: float = 0):
        # General
        self.r = Random()
        # self.name = configuration.setdefault('name', f'metric_r{r.randint(0, 1000)}')
        self.available_distributions = {
            'normal': normal.Normal,
            'poisson': poisson.Poisson,
        }

        # Error configurations
        self.is_threshold_below = configuration.setdefault('is_threshold_below', True)
        self.is_in_peak_error = False
        self.is_error = False
        self.steps = 0

        self.error_length = 0
        self.peaks = 0
        self.error_peak_length = 0
        self.error_metric = self.Peak_error()
        self.peak_chance = 0


        self.value_history = initial_value
        self.validations = configuration.setdefault('validation', {'distribution': {}, 'metric': {}})
        self.validation_distribution = self.validations['distribution']
        self.validation_metric = self.validations['metric']
        self.should_validate_distribution_values = self.validation_distribution.setdefault('validate', False)
        self.should_validate_metric_values = self.validation_metric.setdefault('validate', False)

        # Distribution
        self.distribution = self.available_distributions[configuration.setdefault('distribution', 'normal')]
        self.params = configuration.setdefault('distribution_params', {})
        self.past_based_value = configuration.setdefault('past_based_value', False)

        # Validation
        self.distribution_min = self.validation_distribution.setdefault('min', np.NINF)
        self.distribution_max = self.validation_distribution.setdefault('max', np.Inf)

        self.metric_min = self.validation_metric.setdefault('min', np.NINF)
        self.metric_max = self.validation_metric.setdefault('max', np.Inf)

        if self.should_validate_distribution_values:
            self.validate_min_max('distribution')
        if self.should_validate_metric_values:
            self.validate_min_max('metric')

    def Peak_error(self, target_peaks: int = 4, error_peak_ratio: float = 0.5):
        def return_peak():
            #print('PEAK')
            return self.metric_max if self.is_threshold_below else self.metric_min

        while True:
            # Are we in Pre-Error?
            if self.steps <= self.error_length - self.error_peak_length:
                # Will it peak?
                is_peak = True if self.r.uniform(0, 1) <= self.peak_chance else False
                yield return_peak() if is_peak else self.distribution(**self.params)[0]

            # Are we in Peak-Error?
            else:
                self.is_in_peak_error = True
                yield return_peak()

    def start_error(self, error_length: int, target_peaks: int = 4, error_peak_ratio: float = 0.5):
        r = Random()
        r.seed(42)

        # Pick one error scenario
        self.error_length = error_length
        self.is_error = True
        self.error_metric = self.Peak_error()
        self.peaks = int(r.gauss(mu=target_peaks, sigma=0.5 * target_peaks))
        self.error_peak_length = int(
            r.gauss(mu=self.error_length * error_peak_ratio, sigma=self.error_length * 0.1))
        self.peak_chance = self.peaks / (self.error_length - self.error_peak_length)
        return 0

    def stop_error(self):
        # Return generator to Normal
        self.current_metric = self.distribution
        self.is_error = False
        self.is_in_peak_error = False
        self.steps = 0
        self.error_length = 0
        return 0

    def get_value(self):
        '''
            Produces the metric from a distribution as defined by the user
        :return: One metric sample
        '''

        if self.is_error:
            self.steps += 1
            return next(self.error_metric)
        else:
            new_value = self.distribution(**self.params)[0]
            new_value = self.validate_value('distribution',
                                            new_value) if self.should_validate_distribution_values else new_value
            if self.past_based_value:
                self.value_history += new_value
                return self.value_history
            else:
                return new_value

    def validate_value(self, validation_type: str, value):
        '''
            Validates the values are within valid range as defined by min / max
        '''
        min = self.distribution_min if (validation_type == 'distribution') else self.metric_min
        max = self.distribution_max if (validation_type == 'distribution') else self.metric_max
        value = value if value > min else min
        value = value if value < max else max
        return value

    def validate_min_max(self, validation_type: str):
        min = self.distribution_min if validation_type == 'distribution' else self.metric_min
        max = self.distribution_max if validation_type == 'distribution' else self.metric_max
        if min > max:
            raise ValueError(f'In metric {self.name}, max < min, please update configuration')

    def generator(self):
        while True:
            value = self.get_value()
            res = self.validate_value('metric', value) if self.should_validate_metric_values else value
            yield {'value': res, 'is_error': self.is_in_peak_error}