import numpy as np
from scipy.stats import ttest_ind, chisquare, f_oneway, contingency
from ..util import plot_each_col
from ..findings import TTestFindings, DependenceFindings, ChiSquaredFindings, FindingsList, TestResult

import math
import itertools

class Survey(object):
    def __init__(self, data, *,num_col=None, cat_col=None, description=None):
        self.data = data
        self.num_col = num_col
        self.cat_col = cat_col
        self.description = description

    def auto_detect(self, cohen_es=0.2, eta=0.06, phi_es=0.2, p_value=0.05, min_sample=20):
        findings_list = []
        # Compare mean
        for n_col, c_col in itertools.product(self.num_col, self.cat_col):
            findings = self._compare_mean(n_col, c_col, cohen_es=cohen_es, eta=eta, p_value=p_value, min_sample=min_sample)
            if findings is not None:
                findings_list.append(findings)

        # Compare dependency of two cat_col
        for col_1, col_2 in itertools.combinations(self.cat_col, r=2):
            findings = self._compare_group(col_1, col_2, p_value=p_value, phi_es=phi_es, min_sample=min_sample)
            if findings is not None:
                findings_list.append(findings)
        
        return FindingsList(findings_list)

    
    def _compare_mean(self, num_col, group_col, *, cohen_es=0.2, eta=0.06, p_value=0.05, min_sample=20):
        groups, ignored = self._filter_sparse_group(group_col, min_sample)
        if not ignored.empty:
            print(f"Ignoring groups {list(ignored)} when comparing {num_col} and {group_col}")

        if len(groups) == 1:
            print(f"Skipping comparing {num_col} and {group_col}, only one group available")
        
        elif len(groups) == 2:
            group_1 = groups[0]
            group_2 = groups[1]
            test_result, effect_size = self._t_test(num_col, group_col, group_1, group_2)
            if test_result.pvalue <= p_value and effect_size >= cohen_es:
                return TTestFindings(data=self.data,
                                     group_col=group_col,
                                     num_col=num_col,
                                     group_1=group_1,
                                     group_2=group_2,
                                     test_result=test_result)

        else:
            test_result, effect_size = self._anova(num_col, group_col, groups)
            if test_result.pvalue <= p_value and effect_size >= eta:
                return AnovaFindings(data=self.data,
                                     group_col=group_col,
                                     groups=groups,
                                     num_col=num_col,
                                     test_result=test_result
                                     )
        
        return None
     
    def _filter_sparse_group(self, group_col, min_sample):
        group_count = self.data[group_col].value_counts()
        ignored = group_count[(group_count < min_sample)]
        result = group_count.drop(ignored.index)
        return result.index, ignored.index

    def _compare_group(self, col_1, col_2, p_value=0.05, phi_es=0.2, min_sample=20):
        groups_1, ignored_1 = self._filter_sparse_group(col_1, min_sample)
        groups_2, ignored_2 = self._filter_sparse_group(col_2, min_sample)
        if len(groups_1) <= 1 or len(groups_2) <= 1:
            pass
        
        else:
            test_result, effect_size = self._chi_squared_dependence(col_1, col_2, groups_1, groups_2)
            if test_result.pvalue <= p_value and effect_size >= phi_es:
                return DependenceFindings(data=self.data,
                                        col_1=col_1,
                                        col_2=col_2,
                                        groups_1=groups_1,
                                        groups_2=groups_2,
                                        test_result=test_result
                                        )
        return None
    
    def _anova(self, num_col, group_col):
        group_samples = []
        for i in group_count.index:
            group_samples.append(self.data[self.data[cat_col] == i][num_col])
        test_result = f_oneway(*group_samples)
        effect_size = self._compute_eta_squared(*group_samples)
        return test_result, effect_size
    
    def _compute_eta_squared(self, *args):
        all_data = np.array(list(itertools.chain(args)))
        group_mean = [sample.mean() for i in args]
        group_mean = np.array(group_mean)
        return group_mean.var() / all_data.var()

    def _t_test(self, num_col, group_col, group_1, group_2, **kwargs):
        first_sample = self.data[self.data[group_col] == group_1][num_col]
        second_sample = self.data[self.data[group_col] == group_2][num_col]
        test_result = ttest_ind(a = first_sample,
                                b = second_sample,
                                **kwargs)
        effect_size = self._compute_cohen_es(first_sample, second_sample)
        return test_result, effect_size
    
    def _compute_cohen_es(self, sample_1, sample_2):
        cohen_es = (sample_1.mean() - sample_2.mean()) / sample_1.std()
        return cohen_es
    
    def _compute_phi_es(self, chi2, n):
        return math.sqrt(chi2 / n)
    
    def _chi_squared(self, col_1, expected=None):
        # If expected is None, assuming it is about testing for equality.
        obs = self.data[col_1].value_counts().values
        test_result = scipy.stats.chisquare(obs, expected)
        effect_size = self._compute_phi_es(test_result.chisq, len(self.data[col_1]))
        return test_result, effect_size
    
    def _chi_squared_dependence(self, col_1, col_2, groups_1, groups_2):
        group_1 = self.data[col_1]
        group_1 = group_1[group_1.isin([groups_1]).index]
        group_2 = self.data[col_2]
        group_2 = group_2[group_2.isin([groups_2]).index]
        vals, count = contingency.crosstab(group_1.values, group_2.values)
        test_result = contingency.chi2_contingency(count)
        test_result = TestResult(name='chi2 contigency', 
                                 statistic=test_result[0],
                                 pvalue=test_result[1],
                                 dof=test_result[2],
                                 expected=test_result[3],
                                 )
        effect_size = self._compute_phi_es(test_result.statistic, len(self.data[col_1]))
        return test_result, effect_size
    
    def _plot(self, columns, kind, transformed, **kwargs):
        data = None
        if self._cached['label'] is not None:
            data = self._cached['data']
        
        else:
            self.label()
            data = self._cached['data']
        if transformed:
            data[self.item_col] = self._cached['transform']
        plot_each_col(data, col_list = columns, plot_type=kind, **kwargs)

    def hist_num(self):
        pass
    
    def bar_cat(self):
        pass

    def _handle_null(self, data, col):
        return data.dropna(subset=col)