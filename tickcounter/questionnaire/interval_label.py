import pandas as pd
from tickcounter.questionnaire import Label
from ..util import generate_name

class IntervalLabel(Label):
    def __init__(self, label_rule, name=None):
        self.label_rule = label_rule
        super().__init__(self.generate_label_function(self.label_rule), name)
    
    def generate_label_function(self, label_rule):
        def label(data, score_col):
            # Only support numerical pandas series, will support multiple score_col in the future
            label_ss = pd.Series(index=data.index, dtype=str)
            for label, interval in label_rule.items():
                label_ss[data[score_col].between(*interval)] = label
            return label_ss
        return label