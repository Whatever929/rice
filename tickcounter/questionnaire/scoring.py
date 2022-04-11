import pandas as pd
import warnings
from ..util import generate_name

class Scoring(object):
    name_generator = generate_name("scoring")
    def __init__(self, labeling, encoding=None,*, name=None, columns=None):
        self.encoding = encoding
        self.name = name
        self.labeling = labeling if isinstance(labeling, list) else [labeling] # Used for categorization

        if self.encoding is not None:
            self.columns = []

            for i in encoding.values():
                self.columns.extend(i)
        
        elif (self.encoding is None) and (columns is not None):
            self.columns = columns
        
        elif (self.encoding is not None) and (columns is not None):
            raise ValueError("Can only pass either encoding or columns argument.")

        else:
            raise ValueError("Expected either encoding or columns argument.")

        if self.name is None:
            self.name = next(Scoring.name_generator)

    def transform(self, data, **kwargs):
        if self.encoding is not None:
            df = data.copy()
            if isinstance(self.encoding, dict):
                for encoder, columns in self.encoding.items():
                    df[columns] = encoder.transform(df[columns])
                
                return df
            
            elif isinstance(self.encoding, MultiEncoder):
                if 'return_rule' in kwargs and kwargs['return_rule']:
                    df, rule = self.encoding.transform(df, **kwargs)
                    return df, rule
                
                else:
                    df = self.encoding.transform(df, **kwargs)
                    return df
            
            else:
                raise ValueError(f"Invalid encoder type {type(self.encoding)}")
        else:
            warnings.warn(f"Scoring object {self.name} has no encoding, original DataFrame is returned")
            return data

    def score(self, data):
        df = self.transform(data)
        score_ss = df[self.columns].sum(axis=1)
        score_ss.rename(f"{self.name} score", inplace=True)
        return score_ss

    def label(self, data, score_col=None):
        label_df = None
        if score_col is None:
            data = data.copy()
            data = pd.concat([data, self.score(data)], axis=1)
            score_col = self.score_col
        
        for i in self.labeling:
            label_ss = i.label(data, score_col)
            label_ss.rename(f"{self.name} - Label {i.name}", inplace=True)
        
            if label_df is None:
                label_df = pd.DataFrame([label_ss]).T
        
            else:
                label_df = pd.concat([label_df, label_ss], axis=1)

        return label_df
    
    @property
    def score_col(self):
        return f"{self.name} score"
    
    @property
    def label_col(self):
        return [f"{self.name} - Label {i.name}" for i in self.labeling]