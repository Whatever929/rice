import pandas as pd
from ..util import generate_name

class Encoder(object):
    name_generator = generate_name("encoder")

    def __init__(self, encoding=None, *, template=None, inverse=False, default=None, neutral=None, name=None):
        "Default is used for filling NaN values"
        "Neutral is used for scoring"
        if encoding is None and template is None:
            raise ValueError("Expected argument 'encoding'")
        
        elif template is not None:
            self.encoding = template.encoding
            
        if inverse:
            self.inverse()

        self.encoding = encoding
        self.target = self.encoding.keys()
        self.default = default
        self.neutral = neutral
        
        if name is None:
            self.name = next(Encoder.name_generator)
        
        else:
            self.name = name
    
    def inverse(self):
        "Inverse the encoding"
        encode_item = sorted(self.encoding.items(), key=lambda x:x[1], reverse=True)
        target = [i for i, j in encode_item]
        values = [j for i, j in encode_item]
        self.encoding = dict(zip(target, sorted(values)))
        
    
    def transform(self, data):
        result = data.copy()
        result.replace(self.encoding, inplace=True)
        if self.default is not None:
            data.fillna(self.default, inplace=True)
        return data.replace(self.encoding)
    
    def count_neutral(self, data):
        "Count the number of neutral responses, if 'neutral' is available"
        pass





