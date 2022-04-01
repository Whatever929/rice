import pandas as pd
from rice.questionnaire import Label
from ..util import generate_name

class Interval_Label(Label):
    def __init__(self, label_rule, name=None):
        """Label rule is a mapping from word to values
        for now, use:
        'LabelA': [0, 15]
        Since we use df.between, and it is both inclusive by default, so
        Ours are also inclusive by default too
        """
        self.label_rule = label_rule
        super(self.generate_label_function(self.label_rule), name)
    
    def generate_label_function(self, label_rule):
        def label(self, data, score_col):
            """Only support numerical pandas series, will support multiple score_col in the future"""
            label_ss = pd.Series(index=data.index, dtype=str)
            for label, interval in label_rule.items():
                label_ss[data[score_col].between(*interval)] = label

            return label_ss
        return label