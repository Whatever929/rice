import pandas as pd
from rice.questionnaire import Label
from ..util import generate_name

class Quartile_Label(Label):
    def __init__(self, q, labels, name=None):
        """Label rule is a mapping from word to values
        for now, use:
        'LabelA': [0, 15]
        Since we use df.between, and it is both inclusive by default, so
        Ours are also inclusive by default too
        """
        self.q = q
        self.labels = labels
        super(self.generate_label_function(self.q, self.labels), name)
    
    def generate_label_function(self, q, labels):
        def label(self, data, score_col):
            label_ss = pd.qcut(data[score_col], q=q. labels=labels)
        return label