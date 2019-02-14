from random import Random
from v3io_generator.metrics import normal, poisson
import numpy as np

class Metric:
    '''
        - Define metric parameters
        - Define distribution parameters
        - Define alerts
    '''

    def __init__(self, configuration: dict = dict(), initial_value: float = 0):
        # General
        r = Random()
        # self.name = configuration.setdefault('name', f'metric_r{r.randint(0, 1000)}')
        self.available_distributions = {
            'normal': normal.Normal,
            'poisson': poisson.Poisson,
        }
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

    def get_value(self):
        '''
            Produces the metric from a distribution as defined by the user
        :return: One metric sample
        '''
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
            yield res