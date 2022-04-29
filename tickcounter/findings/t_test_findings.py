from .findings import Findings
from ..util import allow_values
from tickcounter import plot
import seaborn as sns
import numpy as np
from textwrap import dedent

class TTestFindings(Findings):
    def __init__(self, data, group_col, num_col, group_1, group_2, test_result, descrip=None):
        self.data = data
        self.group_col = group_col
        self.num_col = num_col
        self.group_1 = group_1
        self.group_2 = group_2
        self.test_result = test_result
        self.descrip = descrip

    def describe(self, descrip_value=False):
        group_1_mean = self.data[self.data[self.group_col] == self.group_1][self.num_col].mean()
        group_2_mean = self.data[self.data[self.group_col] == self.group_2][self.num_col].mean()
        group_1_val = self.descrip.translate(self.group_col, [self.group_1])[0] if descrip_value else self.group_1
        group_2_val = self.descrip.translate(self.group_col, [self.group_2])[0] if descrip_value else self.group_2
        return f"In column {self.group_col}, the mean of {self.num_col} for {group_1_val} " \
               f"({group_1_mean:.2f}) is {'less' if group_1_mean > group_2_mean else 'more'} than "\
               f"{group_2_val} ({group_2_mean:.2f}) with p_value of {self.test_result.pvalue:.2f}."
    
    def describe_short(self):
        return f"{self.num_col} (num) and {self.group_col} (cat) are not independent"
    
    def illustrate(self, ax=None, descrip_title=False, descrip_value=False, descrip_legend=False, **kwargs):
        #TODO: Support horizontal orient
        data = allow_values(self.data, self.group_col, [self.group_1, self.group_2])
        if ax is None:
            ax = sns.barplot(data=data, x=self.group_col, y=self.num_col, estimator=np.mean, **kwargs)
            ax.set_title(self.describe_short())
        
        else:
            sns.barplot(data=data, x=self.group_col, y=self.num_col, estimator=np.mean, ax=ax, **kwargs)
            ax.set_title(self.describe_short())
        
        self.descrip._descrip_transform(ax=ax, 
                                col=self.group_col, 
                                descrip_value=descrip_value,
                                descrip_title=descrip_title,
                                descrip_legend=descrip_legend)

        return ax