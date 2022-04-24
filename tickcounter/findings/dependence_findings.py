from .findings import Findings
from ..util import allow_values
from tickcounter import plot
import seaborn as sns
import numpy as np

class DependenceFindings(Findings):
    def __init__(self, data, col_1, col_2, groups_1, groups_2, test_result, descrip=None):
        self.data = data
        self.col_1 = col_1
        self.col_2 = col_2
        self.groups_1 = groups_1
        self.groups_2 = groups_2
        self.test_result = test_result
        self.descrip = descrip
    
    def describe(self, descrip_value=False):
        groups_1_val = self.descrip.translate(self.col_1, list(self.groups_1)) if descrip_value else list(self.groups_1)
        groups_2_val = self.descrip.translate(self.col_2, list(self.groups_2)) if descrip_value else list(self.groups_2)
        return f"{self.col_1} (with categories {groups_1_val}) and {self.col_2} " \
               f"(with categories {groups_2_val}) are not independent, with pvalue of " \
               f"{self.test_result.pvalue:.2f} (chi-squared)"

    def describe_short(self):
        return f"{self.col_1} and {self.col_2} are not independent"
    
    def illustrate(self, ax=None, descrip_title=False, descrip_value=False, descrip_legend=False, **kwargs):
        data = allow_values(self.data, self.col_1, self.groups_1)
        data = allow_values(data, self.col_2, self.groups_2)
        if ax is None:
            ax = sns.countplot(data=data, x=self.col_1, hue=self.col_2)
            ax.set_title(self.describe_short())
        else:
            sns.countplot(data=data, x=self.col_1, hue=self.col_2, ax=ax)
            ax.set_title(self.describe_short())
        
        self.descrip._descrip_transform(ax=ax, 
                                col=self.col_1, 
                                descrip_value=descrip_value,
                                descrip_title=descrip_title,
                                descrip_legend=descrip_legend)
        return ax