import pandas as pd
from v3io_generator.metric.metric_group import Metric_Group
import hashlib
import datetime
from pytimeparse import parse
import json


class Generator_df:

    def __init__(self, configuration: dict, initial_timestamp=datetime.datetime.now(), user_hierarchy=pd.DataFrame):
        '''

        '''
        metrics = configuration['metrics']
        timestamps = configuration['timestamps']
        errors = configuration['errors']

        self.dimension_hashes = []
        self.initial_values = {}
        self.dimensions = self.define_uh(df_labels=user_hierarchy[list(list(user_hierarchy.columns) - metrics.keys())],
                                         df_metrics=user_hierarchy[metrics.keys()])


        self.metric_groups = {dimension_hash: Metric_Group(metrics=metrics, initial_values=self.initial_values[dimension_hash],
                                                           error_length_ticks=errors.setdefault('length_in_ticks', 0),
                                                           error_rate_ticks=errors.setdefault('rate_in_ticks', 0)) for dimension_hash in
                              self.dimension_hashes}

        self.global_timestamp = self.get_timestamp(initial_timestamp)
        self.timestamp_interval = self.get_interval(timestamps.setdefault('interval', '1s'))
        self.indexes = ['timestamp', [label for label in self.metric_groups.keys()]]

    def get_timestamp(self, user_timestamp):
        if type(user_timestamp) == datetime.datetime:
            return user_timestamp
        else:
            return datetime.datetime.fromtimestamp(user_timestamp)

    def get_interval(self, user_interval):
        if type(user_interval) == int:
            return datetime.timedelta(seconds=user_interval)
        elif type(user_interval) == str:
            seconds = parse(user_interval)
            return datetime.timedelta(seconds=seconds)
        else:
            return user_interval

    def define_uh(self, df_labels: pd.DataFrame, df_metrics: pd.DataFrame):
        labels = []
        for idx, cols in df_labels.iterrows():
            current_label = cols.to_dict().items()
            labels.append((list(current_label), json.loads(df_metrics.iloc[idx].to_json(orient='index'))))
        for label in labels:
            row_labels_hash = hashlib.sha256(str(label[0]).encode()).hexdigest()
            self.dimension_hashes.append(row_labels_hash)
            self.initial_values[row_labels_hash] = label[1]
        return list(map(lambda l: l[0], labels))

    def get_dataframe_hash(self, df: pd.DataFrame):
        return hashlib.sha256(df.to_json().encode()).hexdigest()

    def get_new_timestamp(self):
        self.global_timestamp += self.timestamp_interval
        return self.global_timestamp

    def get_metric_groups_values_as_dict(self):
        res = []
        sample_timestamp = self.get_new_timestamp()
        for dimension in self.dimensions:
            dimension_name = hashlib.sha256(str(dimension).encode()).hexdigest()
            metric_group = self.metric_groups[dimension_name]
            metrics = next(metric_group.generate())
            metrics['timestamp'] = sample_timestamp
            res.append([*dimension, *metrics.items()])
        return res

    def build_dict_from_tuples_array(self, tuples_array: list):
        for row in tuples_array:
            for key, value in row:
                # is it a label?
                if (key, value) in self.dimensions:
                    print('*')
        return tuples_array

    def transform_metric_groups_dict_to_df(self, metric_groups_dict: dict):
        df = pd.DataFrame()

        # Add columns
        for mg in metric_groups_dict:
            mg_dict = dict(mg)
            row = pd.DataFrame(data=mg_dict, index=[0])
            df = df.append(row)
        # Add total is_error
        df['is_error'] = df.filter(regex='.*is_error.*').apply(lambda row: row.min(), axis=1)

        # Add timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        new_indexes = ['timestamp', *list(map(lambda v: v[0], self.dimensions[0]))]
        df = df.set_index(new_indexes)
        return df

    def generate(self, as_df: bool = True):
        while True:
            res = self.get_metric_groups_values_as_dict()
            if as_df:
                res = self.transform_metric_groups_dict_to_df(res)
            else:
                res = self.build_dict_from_tuples_array(res)
            yield res

    def generate_range(self, start_time=datetime.datetime.now(), end_time=datetime.datetime.now()+datetime.timedelta(seconds=1), as_df: bool = True):
        self.global_timestamp = start_time
        gen = self.generate(as_df)
        if end_time >= self.global_timestamp:
            while end_time >= self.global_timestamp:
                yield next(gen)
        else:
            while True:
                yield pd.DataFrame()