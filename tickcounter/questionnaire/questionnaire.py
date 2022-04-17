import pandas as pd
from scipy.stats import ttest_ind, chisquare
from ..util import generate_name
import seaborn as sns

import itertools

from tickcounter import plot, statistics

class Questionnaire(object):
    def __init__(self, data, scoring, descrip=None):
        self.data = data.copy() # Original data
        self.descrip = descrip # Used for plotting and analysis, takes a Description object
        self._cached = {
            "transform": None, # Will only contain transformed columns
            "score": None,
            "label": None,
            "data": self.data,
        }
        self.scoring = scoring if isinstance(scoring, list) else [scoring] # Used for calculating score
    
    def transform(self):
        if self._cached['transform'] is not None:
            return self._cached['transform']

        else:
            data = None
            # Will change this to support MultiEncoder in the future.
            for i in self.scoring:
                cur_data = i.transform(self.data[i.columns])
                if data is None:
                    data = cur_data
                else:
                    data = pd.concat([data, cur_data], axis=1)
            self._cached['transform'] = data
            return data

    def score(self):
        if self._cached['score'] is not None:
            return self._cached['score']
        
        else:
            result_df = None
            for i in self.scoring:
                score_ss = i.score(self.data)
                
                if result_df is None:
                    result_df = pd.DataFrame([score_ss]).T
                
                else:
                    result_df = pd.concat([result_df, score_ss], axis=1)
            
            self._cached['score'] = result_df
            self._cached['data'] = pd.concat([self._cached['data'], self._cached['score']], axis=1)
            return result_df

    def label(self):
        if self._cached['label'] is not None:
            return self._cached['label']

        else:
            data = None
            if self._cached['score'] is not None:
                data = self._cached['data']
            
            else:
                self.score()
                data = self._cached['data']

            label_df = None
            for scoring in self.scoring:
                cur_label_df = scoring.label(data, scoring.score_col)
                
                if label_df is None:
                    label_df = cur_label_df 
                
                else:
                    label_df = pd.concat([label_df, cur_label_df], axis=1)
            self._cached['label'] = label_df
            self._cached['data'] = pd.concat([self._cached['data'], label_df], axis=1)
            return label_df

    def _plot(self, columns, kind, transformed, **kwargs):
        df = self.processed
        if transformed:
            df[self.item_col] = self._cached['transform']
        plot.plot_each_col(df, col_list = columns, plot_type=kind, **kwargs)
    
    def auto_detect(self, group_col, num_col=None, cohen_es=0.2, eta=0.06, phi_es=0.2, p_value=0.05, min_sample=20):
        group_col = [group_col] if type(group_col) == str else group_col
        group_col.extend(self.label_col)
        if num_col is not None:
            num_col = [num_col] if type(num_col) == str else num_col
            num_col.extend(self.score_col)
        else:
            num_col = self.score_col
        df = self.processed
        ignore_list = set(itertools.product(self.score_col, self.label_col))
        return statistics._auto_detect(data=df, 
                                       num_col=num_col,
                                       cat_col=group_col, 
                                       cohen_es=cohen_es, 
                                       eta=eta, 
                                       phi_es=phi_es, 
                                       p_value=p_value, 
                                       min_sample=min_sample,
                                       ignore_list=ignore_list)

    def hist_label(self, *, transformed=True, separated=False, **kwargs):
        self._plot(columns = self.label_col, kind='hist', transformed=transformed, **kwargs)

    def hist_item(self, *, transformed=True, separated=False, **kwargs):
        self._plot(columns = self.item_col, kind='hist', transformed=transformed, **kwargs)
    
    def hist_score(self, *, transformed=True, separated=False, **kwargs):
        self._plot(columns = self.score_col, kind='hist', transformed=transformed, **kwargs)

    def boxplot_score(self, *, transformed=True, separated=False, **kwargs):
        self._plot(columns = self.score_col, kind='box', transformed=transformed, **kwargs)
    
    def boxplot_item(self, *, transformed=True, separated=False, **kwargs):
        self._plot(columns = self.item_col, kind='box', transformed=transformed, **kwargs)
    
    def count_label(self, *, transformed=True, separated=False, **kwargs):
        self._plot(columns = self.label_col, kind='count', transformed=transformed, **kwargs)
    
    def locate_outlier(self, columns, method='iqr', return_rule=False, zscore_threshold=3):
        # Note that we work on the original data
        if method == 'iqr':
            outlier, outlier_range =  statistics._locate_outlier_iqr(data=self.data, columns=columns)
        elif method == 'zscore':
            outlier, outlier_range = statistics._locate_outlier_zscore(data=self.data, columns=columns, zscore_threshold=zscore_threshold)
        else:
            raise ValueError("method argument can only be either 'iqr" or 'zscore')

        if return_rule:
            return outlier, outlier_range
        else:
            return outlier
    
    def diff_item(self, col, transformed=True):
        df = self.data
        if col not in df.columns:
            df = self.processed
        
        if transformed:
            df = df.copy()
            df[self.item_col] = self.transform()
        
        else:
            df = self._cached['data']

        return statistics._diff_group(df, group_col=col, num_col=self.item_col)
    
    def corr_item(self, col, transformed=True):
        return self.scored.corr()
    
    def crosstab(self, index, col):
        # Should be a label paired with an info columns
        return pd.crosstab(self.processed[index], self.processed[col])
    
    def t_test_group(self, item, info_col, **kwargs):
        df = self.data
        if info_col not in self._cached['data'].columns:
            df = self.processed
        return statistics._t_test_group(data=df, group_col=info_col, num_col=item, **kwargs)
    
    def t_test(self, num_col, group_col, min_sample=20, **kwargs):
        df = self.processed
        groups_1, ignored_1 = statistics._filter_sparse_group(df, col_1, min_sample)
        groups_2, ignored_2 = statistics._filter_sparse_group(df, col_2, min_sample)
        return statistics._t_test(df, num_col, group_col, groups_1, groups_2, **kwargs)
        
    def chi_squared_dependence(self, col_1, col_2, min_sample=None):
        df = self.processed

        if min_sample is None:
            group_1 = df[col_1].value_counts().index
            group_2 = df[col_2].value_counts().index
        
        else:
            group_1, _ = statistics._filter_sparse_group(df, col_1, min_sample)
            group_2, _ = statistics._filter_sparse_group(df, col_2, min_sample)

        return statistics._chi_squared_dependence(df, col_1, col_2, group_1, group_2)
    
    def scatter_item(self, **kwargs):
        sns.pairplot(data=self.processed, vars=self.item_col, kind='scatter', **kwargs)

    def cluster(self, scoring):
        # Use KMeans clustering to cluster the response to something
        pass

    def drop(self, idx):
        self.data.drop(idx, inplace=True)
        self.reset_cache()

    def reset_cache(self):
        self._cached = {
            "transform": None,
            "score": None,
            "label": None,
            "data": self.data,
        }
    
    @property
    def score_col(self):
        if self._cached['score'] is not None:
            return self._cached['score'].columns
        
        else:
            self.score()
            return self._cached['score'].columns
    
    @property
    def label_col(self):
        if self._cached['label'] is not None:
            return self._cached['label'].columns
        
        else:
            self.label()
            return self._cached['label'].columns
    
    @property
    def item_col(self):
        if self._cached['transform'] is not None:
            return self._cached['transform'].columns
        
        else:
            self.transform()
            return self._cached['transform'].columns
    
    @property
    def transformed(self):
        self.transform()
        return self._cached['transform']
    
    @property
    def scored(self):
        self.score()
        return self._cached['score']
    
    @property
    def labeled(self):
        self.label()
        return self._cached['label']
    
    @property
    def processed(self):
        self.label()
        return self._cached['data']
    
    def __getitem__(self, col):
        try:
            return self._cached['data'][col]

        except KeyError:
            self.label()
            return self._cached['data'][col]