from matplotlib import pyplot as plt
import pandas as pd

from tickcounter import plot

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
    
    def describe_short(self):
        descrip_ss = pd.Series([i.describe_short() for i in self.findings_list])
        return descrip_ss

    @plot.plotter
    def illustrate(self, n_col=1):
        for i, findings in enumerate(self.findings_list):
            ax = plt.subplot(len(self.findings_list), n_col, i + 1)
            ax.set_title(findings.describe_short())
            findings.illustrate(ax=ax)
