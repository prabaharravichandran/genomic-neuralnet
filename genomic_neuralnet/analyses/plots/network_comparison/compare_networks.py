from __future__ import print_function

import os

import numpy as np
import pandas as pd
import scipy.stats as sps
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.stats.multicomp import pairwise_tukeyhsd 
from shelve import DbfilenameShelf
from contextlib import closing
from collections import defaultdict
from functools import partial
from sklearn.preprocessing import OneHotEncoder
from genomic_neuralnet.analyses.plots \
        import get_nn_model_data, palette, out_dir \
             , get_significance_letters

sns.set_style('dark')
sns.set_palette(palette)

def string_to_label((species, trait)):
    trait_name = trait.replace('_', ' ').title()
    species_name = species.title()
    if trait_name.count(' ') > 1:
        trait_name = trait_name.replace(' ', '\n')
    return '{}\n{}'.format(species_name, trait_name)

def make_best_dataframe(shelf_data):
    data_dict = defaultdict(partial(defaultdict, dict)) 

    num_models = len(shelf_data) 

    for model_name, optimization in shelf_data.iteritems():
        for species_trait, opt_result in optimization.iteritems():
            species, trait, gpu = tuple(species_trait.split('|'))
            max_fit_index = opt_result.df['mean'].idxmax()
            best_fit = opt_result.df.loc[max_fit_index]
            mean_acc = best_fit.loc['mean']
            sd_acc = best_fit.loc['std_dev']
            hidden = best_fit.loc['hidden']
            count = opt_result.folds * opt_result.runs
            raw_results = best_fit.loc['raw_results']
            data_dict[species][trait][model_name] = (mean_acc, sd_acc, count, raw_results, hidden)
    
    # Add species column. Repeat once per trait per model (2*num models).
    accuracy_df = pd.DataFrame({'species': np.repeat(data_dict.keys(), num_models*2)})

    # Add trait column.
    flattened_data = []
    for species, trait_dict in data_dict.iteritems():
        for trait, model_dict in trait_dict.iteritems():
            for model, (mean, sd, count, raw_res, hidden) in model_dict.iteritems():
                flattened_data.append((trait, model, mean, sd, count, raw_res, hidden))
    accuracy_df['trait'], accuracy_df['model'], accuracy_df['mean'], \
        accuracy_df['sd'], accuracy_df['count'], accuracy_df['raw_results'], \
        accuracy_df['hidden'] = zip(*flattened_data)

    return accuracy_df

def make_plot(accuracy_df):

    accuracy_df = accuracy_df.sort_values(by=['species', 'trait'], ascending=[1,0])

    fig, ax = plt.subplots()

    species_and_traits = accuracy_df[['species', 'trait']].drop_duplicates()
    x = np.arange(len(species_and_traits))

    models = sorted(accuracy_df['model'].unique())
    width = 0.22

    species_list = species_and_traits['species']
    trait_list = species_and_traits['trait']

    bar_sets = []
    error_offsets = []
    for idx, model in enumerate(models):
        means = accuracy_df[accuracy_df['model'] == model]['mean'].values
        std_devs = accuracy_df[accuracy_df['model'] == model]['sd'].values
        counts = accuracy_df[accuracy_df['model'] == model]['count'].values
        std_errs = std_devs / np.sqrt(counts) # SE = sigma / sqrt(N)
        # Size of 95% CI is the SE multiplied by a constant from the t distribution 
        # with n-1 degrees of freedom. [0] is the positive interval direction. 
        #confidence_interval_mult = sps.t.interval(alpha=0.95, df=counts - 1)[0]
        #confidence_interval = confidence_interval_mult * std_errs

        offset = width * idx
        color = palette[idx]
        b = ax.bar(x + offset, means, width, color=color)
        e = ax.errorbar(x + offset + width/2, means, yerr=std_errs, ecolor='black', fmt='none')
        bar_sets.append((b, model))
        error_offsets.append(std_errs)

    significance_letter_lookup = get_significance_letters(accuracy_df, ordered_model_names=models)

    def label(idx, rects, model):
        errors = error_offsets[idx]
        for error, rect, species, trait in zip(errors, rects, species_list, trait_list):
            height = rect.get_height()
            significance_letter = significance_letter_lookup[model][species][trait]
            ax.text( rect.get_x() + rect.get_width()/2.
                   , height + error + 0.02
                   , significance_letter 
                   , ha='center'
                   , va='bottom')

    [label(idx, b, m) for idx, (b,m) in enumerate(bar_sets)]

    # Axis labels (layer 1).
    ax.set_ylabel('Accuracy')
    ax.set_xticks(x + width / 2 * len(models))
    ax.set_xticklabels(map(string_to_label, zip(species_list, trait_list)))
    ax.set_xlim((0 - width / 2, len(trait_list)))
    ax.set_ylim((0, 1))

    # Legend
    ax.legend(map(lambda x: x[0], bar_sets), list(models))

    plt.tight_layout()
    fig_path = os.path.join(out_dir, 'network_comparison.png')
    plt.savefig(fig_path, dpi=500)
    plt.show()
    
def main():
    data = get_nn_model_data() 

    accuracy_df = make_best_dataframe(data)

    make_plot(accuracy_df)

if __name__ == '__main__':
    main()
