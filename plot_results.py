import pandas as pd
from scipy import stats

from init_experiments.plot import plot_trajectories
from init_experiments import config
from init_experiments.params import param2default, param2requests

from ludwigcluster.client import Client

CAT = '*'  # a, b or *  # TODO
X_LIMS = [[0, 1000], [0, 5000]]  # zoom in on particular vertical region of plot
LABEL_PARAMS = ['init']  # must be a list
VLINE = 2500


# collect data
summary_data = []
client = Client(config.RemoteDirs.root.name, param2default)
for param_p, label in client.gen_param_ps(param2requests, label_params=LABEL_PARAMS):
    # param_df
    dfs = []
    for df_p in param_p.glob('*num*/results_{}.csv'.format(CAT)):
        print('Reading {}'.format(df_p.name))
        df = pd.read_csv(df_p, index_col=0)
        df.index.name = 'epoch'
        dfs.append(df)
    param_df = frame = pd.concat(dfs, axis=1)
    print(param_df)
    # summarize data
    num_reps = param_df.shape[1]
    summary_data.append((param_df.index.values,
                         param_df.mean(axis=1).values,
                         param_df.sem(axis=1).values * stats.t.ppf(1 - 0.05 / 2, num_reps - 1),
                         label,
                         num_reps))
    print('--------------------- END {}\n\n'.format(param_p.name))

# sort data
summary_data = sorted(summary_data, key=lambda data: sum(data[1]), reverse=True)
if not summary_data:
    raise SystemExit('No data found')

# plot
for xlim in X_LIMS:
    fig = plot_trajectories(summary_data,
                            y_label=config.Eval.metric,  # is averaged over cat A and B
                            xlim=xlim,
                            ylim=[0.5, 1.0] if config.Eval.metric in ['ba', 'fs'] else [0.0, 1.0],
                            vline=VLINE)
    fig.show()
