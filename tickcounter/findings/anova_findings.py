from .findings import Findings
from ..util import allow_values
from tickcounter import plot
import seaborn as sns
import numpy as np

class AnovaFindings(Findings):
    def __init__(self, data, group_col, num_col, groups, test_result, descrip=None):
        self.data = data
        self.group_col = group_col
        self.num_col = num_col
        self.groups = groups
        self.test_result = test_result
        self.descrip = descrip
    
    def describe(self, descrip_value=False):
        group_mean = self.data.groupby(self.group_col)[self.num_col].mean()
        descrip_mean = [(i, f"{j:.2f}") for i,j in group_mean.iteritems()]
        group_val = self.descrip.translate(self.group_col, list(self.groups)) if descrip_value else list(self.groups)
        descrip = f"Value of {self.num_col} is dependent on {self.group_col} (with groups {group_val}) at " \
                  f"ANOVA pvalue of {self.test_result.pvalue:.2f},. Respective group means are " \
                    + str(descrip_mean)
        return descrip
    
    def describe_short(self):
        return f"Value of {self.num_col} between {self.groups} are not independent."

    def illustrate(self, ax=None, descrip_title=False, descrip_value=False, **kwargs):
        data = allow_values(self.data, self.group_col, self.groups)
        if ax is None:
            ax = sns.barplot(data=data, x=self.group_col, y=self.num_col, estimator=np.mean, **kwargs)
            ax.set_title(self.describe_short())
        
        else:
            sns.barplot(data=data, x=self.group_col, y=self.num_col, estimator=np.mean, ax=ax, **kwargs)
            ax.set_title(self.describe_short())
        
        self.descrip._descrip_transform(ax=ax, 
                                col=self.group_col, 
                                descrip_value=descrip_value,
                                descrip_title=descrip_title)
        
        return ax
