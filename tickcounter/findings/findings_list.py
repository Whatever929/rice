from matplotlib import pyplot as plt
import pandas as pd

from tickcounter import plot

class FindingsList(object):
    """
    Store interesting findings.
    """
    def __init__(self, findings_list):
        self.findings_list = findings_list
    
    def describe(self, descrip_value=False):
        # Return a series object
        descrip_ss = pd.Series([i.describe(descrip_value=descrip_value) for i in self.findings_list])
        return descrip_ss
    
    def describe_short(self):
        descrip_ss = pd.Series([i.describe_short(descrip_value=descrip_value) for i in self.findings_list])
        return descrip_ss

    @plot.plotter
    def illustrate(self, n_col=1, descrip_value=False, descrip_title=False, descrip_legend=False):
        for i, findings in enumerate(self.findings_list):
            ax = plt.subplot(len(self.findings_list), n_col, i + 1)
            ax.set_title(findings.describe_short())
            findings.illustrate(ax=ax, descrip_value=descrip_value, descrip_title=descrip_title, descrip_legend=descrip_legend)
    
    def set_descrip(self, descrip):
        for i in self.findings_list:
            i.descrip = descrip
