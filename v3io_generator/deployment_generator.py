from faker import Faker
from v3io_generator.providers.location_provider import LocationProvider

import itertools
import pandas as pd

class deployment_generator:

    def __init__(self):
        self.f = Faker('en_US')
        self.f.add_provider(LocationProvider)

        self.temp_configuration = list()
        self.temp_location_configuration = dict()

    def get_faker(self):
        return self.f

    def add_location(self, location_level: str, location_bounds: dict):
        self.temp_location_configuration = {
            'level': location_level,
            'nw': location_bounds['nw'],
            'se': location_bounds['se']
        }

    def generate_deployment(self, configuration: list = list()):
        if not configuration:
            deployment_configuration = self.temp_configuration
        else:
            deployment_configuration = configuration

        tmp_generation = self._add_column_to_sample([], deployment_configuration.copy())
        columns = self._extract_columns_from_configuration(deployment_configuration)

        df = pd.DataFrame(data=tmp_generation, columns=columns)

        if not self.temp_location_configuration:
            return df
        else:
            return self._add_location_to_df(df)

    def _add_location_to_df(self, df: pd.DataFrame):
        level = self._get_location_level()
        bounding_box = self._get_location_bounding_box()
        unique_level_values = df[level].unique()
        locations = {current_value: str(self.f.location(bounding_box)) for current_value in unique_level_values}
        df['location'] = df[level].apply(lambda val: locations[val])
        return df

    def _get_location_level(self):
        return self.temp_location_configuration['level']

    def _get_location_bounding_box(self):
        return {'nw': self.temp_location_configuration['nw'], 'se': self.temp_location_configuration['se']}

    def add_level(self, name: str, number: int, level_type):
        self.temp_configuration.append((name, number, level_type))
        # self.temp_configuration.append((self._add_config_name(name), self._add_config_number(number), self._add_config_type(level_type)))

    def _add_config_type(self, level_type: str):
        available_faker_types = {
            'company': self.f.company,
            'person': self.f.person,
            'country': self.f.country,
        }
        return 0

    def _add_config_name(self, name: str):
        return 0

    def _add_config_number(self, num: int):
        return 0

    def _is_data_generation_needed(self, level_tuple: tuple):
        if type(level_tuple[1]) == int:
            return True
        return False

    def _extract_columns_from_configuration(self, configuration: list):
        return list(map(lambda columns: columns[0], configuration))

    def _add_column_to_sample(self, current: list, left: list):
        if len(left) == 1:
            current_level = left.pop(0)
            current_generator = current_level[2]
            num_possibilities_to_generate = current_level[1]
            to_append = [current_generator() for elem in range(num_possibilities_to_generate)]
            generated = [[*current, elem] for elem in to_append]
            return generated
        else:
            current_level = left.pop(0)
            current_generator = current_level[2]
            num_possibilities_to_generate = current_level[1]
            to_append = [current_generator() for elem in range(num_possibilities_to_generate)]
            generated = [self._add_column_to_sample([*current, elem], left.copy()) for elem in to_append]
            return list(itertools.chain.from_iterable(generated))


