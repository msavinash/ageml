import sys
sys.path.insert(1, './')
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_percentage_error
from agingml import temporal_degradation_test as tdt
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

dataset_url = 'data/avocados_demand_forecasting_dataset.csv'
date_columns = ['date', 'inference_time']
categoric_columns = ['month', 'week', 'day_of_week', 'day', 'year', 'week_in_month']
dtype_categoric = dict([(c,'category') for c in categoric_columns])
# dataset = pd.read_csv(dataset_url , dtype=dtype_categoric, parse_dates=date_columns)
dataset = pd.read_csv(dataset_url)

dataset['timestamp'] = pd.to_datetime(dataset['inference_time'])
non_feature_cols = ['date', 'inference_time', 'demand']

data = dataset[dataset.columns[~dataset.columns.isin(non_feature_cols)]]
data = data.set_index('timestamp')
target = dataset['demand']
target.index = data.index


# Experiment set up
dataset = 'avocados'
n_train = 52
n_test = 12
n_prod = 24
n_simulations = 3000
metric = mean_absolute_percentage_error
freq = 'W'
models = [LGBMRegressor(), ElasticNet(), RandomForestRegressor(), MLPRegressor()]

for model in models:
    print(f'Running process for: {type(model).__name__}')
    errors_df = tdt.evaluation_runner(data, target, model, n_train, n_test, n_prod, n_simulations)
    errors_df.to_parquet(f'results/aging/{dataset}/aging_{dataset}_{type(model).__name__}_{n_simulations}_simulations_{n_prod}_prod.parquet')

    d_errors_df = tdt.aggregate_errors_data(errors_df, metric=metric, freq=freq, only_valid_models=True)
    d_errors_df.to_parquet(f'results/aging/{dataset}/aging_{dataset}_{type(model).__name__}_{n_simulations}_simulations_{n_prod}_prod_{freq}.parquet')