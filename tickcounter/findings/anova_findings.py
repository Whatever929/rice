from .findings import Findings
from ..util import allow_values
import seaborn as sns
import numpy as np

class AnovaFindings(Findings):
    def __init__(self, data, group_col, num_col, groups, test_result):
        self.data = data
        self.group_col = group_col
        self.num_col = num_col
        self.groups = groups
        self.test_result = test_result
    
    def describe(self):
        group_mean = self.data.groupby(self.group_col)[self.num_col].mean()
        descrip_mean = [(i, f"{j:.2f}") for i,j in group_mean.iteritems()]
        descrip = f"Value of {self.num_col} is dependent on {self.group_col} (with groups {list(self.groups)}) at " \
                  f"ANOVA pvalue of {self.test_result.pvalue:.2f},. Respective group means are " \
                    + str(descrip_mean)
        return descrip
    
    def describe_short(self):
        return f"Value of {self.num_col} between {self.groups} are not independent."

    def illustrate(self, ax=None, **kwargs):
        data = allow_values(self.data, self.group_col, self.groups)
        if ax is None:
            ax = sns.barplot(data=data, x=self.group_col, y=self.num_col, estimator=np.mean, **kwargs)
            ax.set_title(self.describe_short())
        
        else:
            sns.barplot(data=data, x=self.group_col, y=self.num_col, estimator=np.mean, ax=ax, **kwargs)
            ax.set_title(self.describe_short())
