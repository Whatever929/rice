import numpy as np
import pandas as pd

from scipy.stats import ttest_ind, chisquare, f_oneway, contingency
from scipy import stats
from ..findings import TTestFindings, DependenceFindings, ChiSquaredFindings, TestResult, FindingsList, AnovaFindings

import math
import itertools

def _anova(data, num_col, group_col, groups):
    group_samples = []
    for i in groups:
        group_samples.append(data[data[group_col] == i][num_col])
    test_result = f_oneway(*group_samples)
    effect_size = _compute_eta_squared(*group_samples)
    return test_result, effect_size

def _compute_eta_squared(*args):
    # args refer to the samples for each 
    all_data = np.asarray(list(itertools.chain(*args)))
    group_mean = [i.mean() for i in args]
    group_mean = np.array(group_mean)
    return group_mean.var() / all_data.var()

def _t_test(data, num_col, group_col, group_1, group_2, **kwargs):
    first_sample = data[data[group_col] == group_1][num_col]
    second_sample = data[data[group_col] == group_2][num_col]
    test_result = ttest_ind(a = first_sample,
                            b = second_sample,
                            **kwargs)
    effect_size = _compute_cohen_es(first_sample, second_sample)
    return test_result, effect_size

def _compute_cohen_es(sample_1, sample_2):
    cohen_es = (sample_1.mean() - sample_2.mean()) / sample_1.std()
    return cohen_es

def _compute_phi_es(chi2, n):
    return math.sqrt(chi2 / n)

def _chi_squared(data, col_1, expected=None):
    # If expected is None, assuming it is about testing for equality.
    obs = data[col_1].value_counts().values
    test_result = chisquare(obs, expected)
    effect_size = _compute_phi_es(test_result.chisq, len(data[col_1]))
    return test_result, effect_size

def _chi_squared_dependence(data, col_1, col_2, groups_1, groups_2):
    group_1 = data[col_1]
    group_1 = group_1[group_1.isin([groups_1]).index]
    group_2 = data[col_2]
    group_2 = group_2[group_2.isin([groups_2]).index]
    vals, count = contingency.crosstab(group_1.values, group_2.values)
    test_result = contingency.chi2_contingency(count)
    test_result = TestResult(name='chi2 contigency', 
                             statistic=test_result[0],
                             pvalue=test_result[1],
                             dof=test_result[2],
                             expected=test_result[3],
                            )
    effect_size = _compute_phi_es(test_result.statistic, len(data[col_1]))
    return test_result, effect_size

def _compare_group(data, col_1, col_2, p_value=0.05, phi_es=0.2, min_sample=20):
    groups_1, ignored_1 = _filter_sparse_group(data, col_1, min_sample)
    groups_2, ignored_2 = _filter_sparse_group(data, col_2, min_sample)
    if len(groups_1) <= 1 or len(groups_2) <= 1:
        pass
    
    else:
        test_result, effect_size = _chi_squared_dependence(data, col_1, col_2, groups_1, groups_2)
        if test_result.pvalue <= p_value and effect_size >= phi_es:
            return DependenceFindings(data=data,
                                    col_1=col_1,
                                    col_2=col_2,
                                    groups_1=groups_1,
                                    groups_2=groups_2,
                                    test_result=test_result
                                    )
    return None

def _compare_mean(data, num_col, group_col, *, cohen_es=0.2, eta=0.06, p_value=0.05, min_sample=20):
    groups, ignored = _filter_sparse_group(data, group_col, min_sample)
    if not ignored.empty:
        print(f"Ignoring groups {list(ignored)} when comparing {num_col} and {group_col}")

    if len(groups) == 1:
        print(f"Skipping comparing {num_col} and {group_col}, only one group available")
    
    elif len(groups) == 2:
        group_1 = groups[0]
        group_2 = groups[1]
        test_result, effect_size = _t_test(data, num_col, group_col, group_1, group_2)
        if test_result.pvalue <= p_value and effect_size >= cohen_es:
            return TTestFindings(data=data,
                                group_col=group_col,
                                num_col=num_col,
                                group_1=group_1,
                                group_2=group_2,
                                test_result=test_result)

    else:
        test_result, effect_size = _anova(data, num_col, group_col, groups)
        if test_result.pvalue <= p_value and effect_size >= eta:
            return AnovaFindings(data=data,
                                    group_col=group_col,
                                    groups=groups,
                                    num_col=num_col,
                                    test_result=test_result
                                    )
    
    return None

def _filter_sparse_group(data, group_col, min_sample):
    group_count = data[group_col].value_counts()
    ignored = group_count[(group_count < min_sample)]
    result = group_count.drop(ignored.index)
    return result.index, ignored.index

def _auto_detect(data, 
                 num_col, 
                 cat_col, 
                 cohen_es=0.2, 
                 eta=0.06, 
                 phi_es=0.2, 
                 p_value=0.05, 
                 min_sample=20, 
                 ignore_list=None):
    findings_list = []
    ignore_list = [] if ignore_list is None else ignore_list
    # Compare mean
    for n_col, c_col in itertools.product(num_col, cat_col):
        # TODO: Check if this is inefficient.
        if ((n_col, c_col) in ignore_list) or ((c_col, n_col) in ignore_list):
            continue
        else:
            findings = _compare_mean(data, n_col, c_col, cohen_es=cohen_es, eta=eta, p_value=p_value, min_sample=min_sample)
            if findings is not None:
                findings_list.append(findings)

    # Compare dependency of two cat_col
    for col_1, col_2 in itertools.combinations(cat_col, r=2):
        # TODO: Check if this is inefficient.
        if ((col_1, col_2) in ignore_list) or ((col_2, col_1) in ignore_list):
            continue
        else:
            findings = _compare_group(data, col_1, col_2, p_value=p_value, phi_es=phi_es, min_sample=min_sample)
            if findings is not None:
                findings_list.append(findings)
    
    return FindingsList(findings_list)

def _diff_group(data, group_col, num_col):
    df_group = data.groupby(group_col)[num_col].mean().T
    result = pd.DataFrame(index=df_group.index)
    for i in itertools.combinations(df_group.columns, 2):
        result[f"{i[0]} - {i[1]}"] = df_group[i[0]] - df_group[i[1]]
    return result

def _diff(data, *args):
    # TODO: Check the len of each args sample.
    result = pd.DataFrame(index=pd.RangeIndex(len(args[0])))
    for i in itertools.combinations(df_group.columns, 2):
        result[f"{i[0]} - {i[1]}"] = df_group[i[0]] - df_group[i[1]]
    return result

def _t_test_group(data, group_col, num_col, **kwargs):
    test_result = dict()
    for i in itertools.combinations(data[group_col].value_counts().index, r=2):
        test_result[f"{i[0]} vs {i[1]}"] = ttest_ind(a = df[df[group_col] == i[0]][num_col],
                                                     b = df[df[group_col] == i[1]][num_col],
                                                     **kwargs)
    return test_result

def _locate_outlier_zscore(data, columns, zscore_threshold, any=True, exclude=False):
  '''
  Locate outliers from numerical columns.
  Arguments:
  data: pandas DataFrame
  columns: A list of column's names for checking outliers. Must be numerical columns
  zscore_threshold: Threshold for classifying outliers.
  any: If True, classify the data point as outlier if value from one of the column is a outlier.
  exclude: If True, return non-outliers. If False, return outliers.

  Returns pandas DataFrame.
  '''
  mean = data[columns].mean(axis=0)
  std = data[columns].std(axis=0)
  lower_bound = (std * zscore_threshold - mean).rename("Lower_bound")
  upper_bound = (std * zscore_threshold + mean).rename("Upper_bound")
  outlier_range = pd.concat([lower_bound, upper_bound], axis=1)
  # TODO: Make this more efficient
  # The above workflow is equivalent to below, at 3 decimal points
  mask_include = np.abs(stats.zscore(data[columns])) > zscore_threshold
  mask_exclude = np.abs(stats.zscore(data[columns])) < zscore_threshold

  if any:
    if exclude:
      return data[mask_exclude.any(axis=1)]
    else:
      data = data[mask_include.any(axis=1)]
      outlier_field = pd.DataFrame(mask_include, columns=columns)
      outlier_field = outlier_field.apply(lambda x: x.replace(True, x.name).replace(False, ""))
      outlier_field = outlier_field.apply(lambda x: x.str.cat(sep=''), axis=1)
      outlier_field = outlier_field.replace("", np.nan).dropna()
      outlier_field.rename("Outlier_field", inplace=True)
      assert data.index.equals(outlier_field.index)
      return (pd.concat([data, outlier_field], axis=1), outlier_range)
  
  else:
    if exclude:
      return data[mask_exclude.all(axis=1)]

    else:
      data = data[mask_include.all(axis=1)]
      outlier_field = pd.DataFrame(mask_include, columns=columns)
      outlier_field = outlier_field.apply(lambda x: x.replace(True, x.name).replace(False, ""))
      outlier_field = outlier_field.apply(lambda x: x.str.cat(sep=''), axis=1)
      outlier_field = outlier_field.replace("", np.nan).dropna()
      outlier_field.rename("Outlier_field", inplace=True)
      assert data.index.equals(outlier_field.index)
      return (pd.concat([data, outlier_field], axis=1), outlier_range)

def _locate_outlier_iqr(data, columns):
  """
  Return all rows that are outliers in at least 1 feature.

  Values exceed Q3 or below Q1 by more than 1.5 IQR will be classified as outliers. 

  Parameters
  ----------
  data : pandas.DataFrame
      Data containing outliers.
  
  Returns
  -------
  outliers : pandas.DataFrame
      DataFrame containing all the outliers.
  
  outlier_range: pandas.DataFrame.
      Contains the interval non-outliers values.
  """

  q1 = data[columns].quantile(0.25)
  q3 = data[columns].quantile(0.75)
  out_iqr = 1.5 * (q3 - q1)
  lower_bound = (q1 - out_iqr).rename("Lower bound")
  upper_bound = (q3 + out_iqr).rename("Upper bound")
  outlier_range = pd.concat([lower_bound, upper_bound], axis=1)

  mask = (data[columns] > out_iqr + q3) | (data[columns] < q1 - out_iqr)
  outlier_field = pd.DataFrame(mask, columns=columns)
  outlier_field = outlier_field.apply(lambda x: x.replace(True, x.name).replace(False, ""))
  outlier_field = outlier_field.apply(lambda x: x.str.cat(sep=''), axis=1)
  outlier_field = outlier_field.replace("", np.nan).dropna()
  outlier_field.rename("Outlier_field", inplace=True)
  outliers = data[mask.any(axis=1)]
  return (pd.concat([outliers, outlier_field], axis=1), outlier_range)