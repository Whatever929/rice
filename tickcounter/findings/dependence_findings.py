from .findings import Findings
from ..util import allow_values
import seaborn as sns
import numpy as np

class DependenceFindings(Findings):
    def __init__(self, data, col_1, col_2, groups_1, groups_2, test_result):
        self.data = data
        self.col_1 = col_1
        self.col_2 = col_2
        self.groups_1 = groups_1
        self.groups_2 = groups_2
        self.test_result = test_result
    
    def describe(self):
        return f"{self.col_1} (with categories {list(self.groups_1)}) and {self.col_2} " \
               f"(with categories {list(self.groups_2)}) are not independent, with pvalue of " \
               f"{self.test_result.pvalue:.2f} (chi-squared)"

    def describe_short(self):
        return f"{self.col_1} and {self.col_2} are not independent"
    
    def illustrate(self, ax=None):
        data = allow_values(self.data, self.col_1, self.groups_1)
        data = allow_values(data, self.col_2, self.groups_2)
        if ax is None:
            ax = sns.countplot(data=data, x=self.col_1, hue=self.col_2)
            ax.set_title(self.describe_short())
        else:
            sns.countplot(data=data, x=self.col_1, hue=self.col_2, ax=ax)
            ax.set_title(self.describe_short())