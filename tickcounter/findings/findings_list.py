from matplotlib import pyplot as plt
import pandas as pd

class FindingsList(object):
    """
    Store interesting findings.
    """
    def __init__(self, findings_list):
        self.findings_list = findings_list
    
    def describe(self):
        # Return a series object
        descrip_ss = pd.Series([i.describe() for i in self.findings_list])
        return descrip_ss
    
    def illustrate(self, n_col=1):
        for i, findings in enumerate(self.findings_list):
            ax = plt.subplot(len(self.findings_list), 1, i + 1)
            findings.illustrate(ax=ax)
