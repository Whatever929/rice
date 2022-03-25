import pandas as pd
from ..util import generate_name

class Scoring(object):
    name_generator = generate_name("scoring")
    def __init__(self, encoding, labeling, *, name=None):
        """Encoding must a mapping of encoding object and corresponding column.
        Might support array of SingleEncoder in the future.

        Can support multiple labeling, this is because for data with unknown labeling or no labeling,
        the user can try on different label.

        Might need to implement auto mode instead of specifying the encoding manually. You can
        infer the columns using the return rule in the encoding.

        TODO: It should possible for scoring to not have encoding, as some data are already encoded
        TODO: For the above case, need to support taking in arbitrary columns
        """
        self.encoding = encoding
        self.name = name
        self.labeling = labeling if isinstance(labeling, list) else [labeling] # Used for categorization
        self.columns = []

        for i in encoding.values():
            self.columns.extend(i)

        if self.name is None:
            self.name = next(Scoring.name_generator)

    def transform(self, data, **kwargs):
        df = data.copy()
        if isinstance(self.encoding, dict):
            for encoder, columns in self.encoding.items():
                df[columns] = encoder.transform(df[columns])
        
        elif isinstance(self.encoding, MultiEncoder):
            df = self.encoding.transform(df, **kwargs)
        
        else:
            raise ValueError(f"Invalid encoder type {type(self.encoding)}")

        return df

    def score(self, data):
        df = data.copy()
        df = self.transform(df)
        score_ss = df[self.columns].sum(axis=1)
        score_ss.rename(f"Score - {self.name}", inplace=True)
        return score_ss

    def label(self, data, score_col):
        df = data.copy()
        label_df = None
        
        for i in self.labeling:
            label_ss = i.label(df, score_col)
            label_ss.rename(f"Label - {i.name}", inplace=True)
        
        if label_df is None:
            label_df = pd.DataFrame([label_ss]).T
        
        else:
            label_df = pd.concat([label_df, label_ss], axis=1)
        
        return label_df