import pandas as pd
from tickcounter.questionnaire import Label
from ..util import generate_name

class QuartileLabel(Label):
    def __init__(self, q, labels, name=None):
        self.q = q
        self.labels = labels
        super().__init__(self.generate_label_function(self.q, self.labels), name)
    
    def generate_label_function(self, q, labels):
        def label(data, score_col):
            label_ss = pd.qcut(data[score_col], q=q, labels=labels)
            return label_ss
        return label