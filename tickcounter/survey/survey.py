import numpy as np
from ..util import plot_each_col
from tickcounter import statistics, plot

import itertools

class Survey(object):
    def __init__(self, data, *,num_col=None, cat_col=None, description=None):
        self.data = data
        self.num_col = num_col
        self.cat_col = cat_col
        self.description = description

    def auto_detect(self, cohen_es=0.2, eta=0.06, phi_es=0.2, p_value=0.05, min_sample=20):
        return statistics._auto_detect(data=self.data, 
                                       num_col=self.num_col, 
                                       cat_col=self.cat_col,
                                       cohen_es=cohen_es,
                                       eta=eta,
                                       phi_es=phi_es,
                                       p_value=p_value,
                                       min_sample=min_sample)
    
    def anova(self, num_col, group_col):
        return statistics._anova(self.data, num_col, group_col)
    
    def compute_eta_squared(self, *args):
        return statistics._compute_eta_squared(self, *args)
    
    def compare_mean(self, num_col, group_col, *, cohen_es=0.2, eta=0.06, p_value=0.05, min_sample=20):
        return statistics._compare_mean(self.data, 
                                        num_col, 
                                        group_col, 
                                        cohen_es=cohen_es, 
                                        eta=eta, 
                                        p_value=p_value,
                                        min_sample=min_sample)

    def compare_group(self, col_1, col_2, p_value=0.05, phi_es=0.2, min_sample=20):
        return statistics._compare_group(data=self.data,
                                         col_1=col_1,
                                         col_2=col_2, 
                                         p_value=p_value,
                                         phi_es=phi_es,
                                         min_sample=min_sample)

    def t_test(self, num_col, group_col, group_1, group_2, **kwargs):
        return statistics._t_test(data=self.data,
                                  num_col=num_col,
                                  group_col=group_col,
                                  group_1=group_1,
                                  group_2=group_2,
                                  **kwargs)
    
    def compute_cohen_es(self, sample_1, sample_2):
        return statistics._compute_cohen_es(sample_1, sample_2)
    
    def compute_phi_es(self, chi2, n):
        return statistics._compute_phi_es(chi2, n)
    
    def chi_squared(self, col_1, expected=None):
        return statistics._chi_squared(self.data, col_1, expected)
    
    def chi_squared_dependence(self, col_1, col_2, groups_1, groups_2):
        return statistics._chi_squared_dependence(self.data, col_1, col_2, groups_1, groups_2)

    def hist_num(self, **kwargs):
        return self._plot(columns=self.num_col, kind='hist', **kwargs)
    
    def count_cat(self, **kwargs):
        return self._plot(columns=self.cat_col, kind='count', **kwargs)
    
    def locate_outlier(self, columns, method='iqr', return_rule=False, zscore_threshold=3):
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
    
    def _plot(self, columns, kind, **kwargs):
        return plot.plot_each_col(data=self.data, col_list=columns, plot_type=kind, **kwargs)

    def _handle_null(self, data, col):
        return data.dropna(subset=col)