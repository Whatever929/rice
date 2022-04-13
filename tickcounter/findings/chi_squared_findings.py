from .findings import Findings
import seaborn as sns
import numpy as np

class ChiSquaredFindings(Findings):
    # Either report equal proportion (col_2 is None) or dependent relationship (col_2 is not None)
    def __init__(self, data, col, groups, test_result):
        self.data = data
        self.col = col
        self.groups = groups
        self.test_result = test_result
    
    def describe(self):
        if self.test_result.expected is None:
            self._describe_equal()
        
        else:
            self._describe_expected()
    
    def illustrate(self, ax=None):
        if self.test_result.expected is None:
            self._illustrate_equal(ax)
        
        else:
            self._illustrate_expected(ax)
    
    def _describe_short_equal(self):
        return f"{self.groups} are not equal in proportion"
    
    def _describe_short_proportion(self):
        return f"{self.groups} does not match expected proportion {self.test_result.expected}"
    
    def _describe_equal(self):
        return f"Column {self.col} with categories {self.groups} are not equal, at pvalue of {self.test_result.pvalue:.2f} ({self.test_result.name})"
    
    def _describe_expected(self):
        return f"Column {self.col} with categories {self.groups} are not equal to the expected proportion - {self.test_result.expected}, at pvalue of {self.test_result.pvalue:.2f} ({self.test_result.name})"
    
    def _illustrate_equal(self, ax=None):
        data = allow_values(self.data, self.col, self.groups)
        if ax is None:
            sns.countplot(data=data, x=self.col)
        else:
            sns.countplot(data=data, x=self.col, ax=ax)
    
    def _illustrate_expected(self, ax=None):
        data = allow_values(self.data, self.col, self.groups)
        # TODO: Still has no idea how to illustrate expected proportions
        pass
