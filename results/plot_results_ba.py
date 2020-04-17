"""
Note:
    balanced accuracy is flat when evaluating slot=b and context-size=3 and sample_b=super,
    because items in slot B do not correlate with items in slot Y (sampling strategy is
    "super"). The context does not have category information because for each Bi word,
     all category contexts are equally represented, thus averaging out category information.
     If instead, context information for each Yi item was averaged together, and Yi item information discarded,
     balanced accuracy should not be flat. This is not done because the research question is about category information
     in A, X, and B, and not in Y.


"""

import pandas as pd
from scipy import stats

from entropic.figs import plot_summary, correct_artifacts
from entropic import config
from entropic.params import param2default, param2requests

from ludwig.results import gen_param_paths


LABEL_PARAMS = []  # must be a list
LEGEND = True
LABELS = []
TOLERANCE = 0.04
SORT_BY_PERFORMANCE = True
REVERSE_ORDER = True

STUDY = '3b1'


if STUDY == '1a1':
    param2requests = {'sample_a': [('item', 'item')],
                      # 'incongruent_a': [(0.0, 0.0), (0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5),
                      #                   (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)],
                      'incongruent_a': [(0.0, 0.0), (0.2, 0.2), (0.4, 0.4), (0.5, 0.5),
                                        (0.6, 0.6), (0.8, 0.8), (1.0, 1.0)],
                      }
    conditions = [('x', 2)]

elif STUDY == '1b1':
    param2requests = {'sample_b': [('item', 'item')],
                      'incongruent_b': [(0.0, 0.0), (0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5),
                                        (0.6, 0.6), (0.7, 0.7), (0.8, 0.8), (0.9, 0.9), (1.0, 1.0)],
                      }
    conditions = [('x', 2)]


elif STUDY == '2a1':
    param2requests = {'sample_a': [('item', 'item')],
                      'incongruent_a': [(1.0, 0.0), (0.0, 1.0), (0.0, 0.0), (1.0, 1.0)],
                      }
    conditions = [('x', 2)]
elif STUDY == '2a2':
    param2requests = {'sample_a': [('item', 'item')],
                      'incongruent_a': [(0.0, 0.5), (1.0, 0.5), (0.5, 0.5)],
                      }
    conditions = [('x', 2)]
elif STUDY == '2b1':
    param2requests = {'sample_b': [('item', 'item')],
                      'incongruent_b': [(1.0, 0.0), (0.0, 1.0), (0.0, 0.0), (1.0, 1.0)],
                      }
    conditions = [('x', 2)]
elif STUDY == '2b2':
    param2requests = {'sample_b': [('item', 'item')],
                      'incongruent_b': [(0.0, 0.5), (1.0, 0.5)],
                      }
    conditions = [('x', 2)]

elif STUDY == '3a1':
    param2requests = {'sample_a': [('item', 'item')],
                      'incongruent_a': [(0.0, 0.0)],
                      'drop_a': [(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)],
                      'lr': [0.4],
                      }
    conditions = [('x', 2)]
elif STUDY == '3b1':
    param2requests = {'sample_b': [('item', 'item')],
                      'incongruent_b': [(0.0, 0.0)],
                      'drop_b': [(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)],
                      'lr': [0.5],  # TODO s this really needed?
                      }
    conditions = [('a', 1), ('x', 1), ('b', 1)]

else:
    conditions = [('a', 1), ('x', 2), ('b', 3)]

for slot, context_size in conditions:

    labels = iter(LABELS)

    print(param2default)
    print()
    print(param2requests)

    # collect data
    summary_data = []
    color_id = 0
    for param_p, label in sorted(gen_param_paths(config.Dirs.root.name,
                                                 param2requests,
                                                 param2default,
                                                 label_n=True,
                                                 label_params=LABEL_PARAMS),
                                 key=lambda i: i[1], reverse=REVERSE_ORDER):
        # load data-frame
        dfs = []
        for df_p in param_p.glob(f'*num*/ba_{slot}_context-size={context_size}.csv'):
            print('Reading {}'.format(df_p.name))
            df = pd.read_csv(df_p, index_col=0)
            df.index.name = 'step'
            # remove dips
            df = df.apply(correct_artifacts, result_type='expand', tolerance=TOLERANCE)
            dfs.append(df)
        param_df = frame = pd.concat(dfs, axis=1)

        # custom labels
        if LABELS:
            label = next(labels)

        # shorten labels
        if str(STUDY).startswith('1a'):
            label = label.replace(f'sample_a={param2requests["sample_a"][0]}\n', '')
        if str(STUDY).startswith('1b'):
            label = label.replace(f'sample_b={param2requests["sample_b"][0]}\n', '')
        else:
            label = label.replace('sample_', '')

        # color
        color = f'C{color_id}'  # make colors consistent with label, not best ba
        color_id += 1
        print('color id', color_id)

        # summarize data
        num_reps = param_df.shape[1]
        summary_data.append((param_df.index.values,
                             param_df.mean(axis=1).values,
                             param_df.sem(axis=1).values * stats.t.ppf(1 - 0.05 / 2, num_reps - 1),
                             label,
                             color,
                             num_reps))

    if not summary_data:
        raise SystemExit('No data found')

    # sort data
    if SORT_BY_PERFORMANCE:
        summary_data = sorted(summary_data, key=lambda data: sum(data[1]), reverse=True)

    # plot
    fig = plot_summary(summary_data,
                       y_label='Categorization [Balanced accuracy]',
                       legend=LEGEND,
                       title=f'study={STUDY}\nslot={slot}\ncontext-size={context_size}\n',
                       )
    fig.show()
