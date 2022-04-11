import pandas as pd
import warnings
from ..util import generate_name

class Encoder(object):
    name_generator = generate_name("encoder")

    def __init__(self, encoding=None, *, template=None, inverse=False, default=None, neutral=None, dtype=None, name=None):
        if encoding is not None:
            self.encoding = encoding
            self.target = self.encoding.keys()
            self.default = default
            self.neutral = neutral
            # At the moment, dtype is not used
            if dtype is None:
                self.dtype = str
            else:
                self.dtype = dtype
        
        elif template is not None:
            # Default and neutral will be overwritten later if they are specified in kwargs.
            self.encoding = template.encoding
            self.target = self.encoding.keys()
            self.default = default if default is not None else template.default
            self.neutral = neutral if neutral is not None else template.neutral
            self.dtype = dtype if dtype is not None else template.dtype
            
        else:
            raise ValueError("Expected argument 'encoding'")

        if inverse:
            self.inverse()
        
        # TODO: If template is used, we can use other name instead.
        if name is None:
            self.name = next(Encoder.name_generator)
        
        else:
            self.name = name
    
    def inverse(self):
        encode_item = sorted(self.encoding.items(), key=lambda x:x[1], reverse=True)
        target = [i for i, j in encode_item]
        values = [j for i, j in encode_item]
        self.encoding = dict(zip(target, sorted(values)))
        
    
    def transform(self, data, *, columns=None, ignore_list=None, return_rule=False, mode='any'):
        result = data.copy()

        if isinstance(data, pd.Series):
            result.replace(self.encoding, inplace=True)
            if self.default is not None:
                result.fillna(self.default, inplace=True)
            return result
        
        elif isinstance(data, pd.DataFrame):
            encode_rule = pd.Series(index=data.columns, dtype=str)

            if ignore_list is None:
                ignore_list = []

            # TODO: Rewrite this section
            for i in result.columns:
                if i in ignore_list:
                    continue

                if columns is not None:
                    if i in columns:
                        result[i] = result[i].replace(self.encoding)
                        if self.default is not None:
                            result[i] = result[i].fillna(self.default)
                        encode_rule[i] = self.name

                else:
                    unique_values = result[i].value_counts().index
                    if mode == "strict":
                        if len(set(unique_values) ^ set(self.encoding.keys())) == 0:
                            result[i] = result[i].replace(self.encoding)
                            if self.default is not None:
                                result[i] = result[i].fillna(self.default)
                            encode_rule[i] = self.name
                    elif mode == "any":
                        if len(set(unique_values) - set(self.encoding.keys())) == 0:
                            result[i] = result[i].replace(self.encoding)
                            if self.default is not None:
                                result[i] = result[i].fillna(self.default)
                            encode_rule[i] = self.name
                    else:
                        raise ValueError("rule argument can only be strict or any")
            
            if return_rule:
                return (result, encode_rule)

            else:
                return result
        else:
            raise TypeError(f"Expected pandas Series or DataFrame, got {type(data)} instead")
    
    def count_neutral(self, data, **kwargs):
        if self.neutral is not None:
            if isinstance(data, pd.Series):
                total = (self.transform(data) == self.neutral).astype(int)
                return total

            elif isinstance(data, pd.DataFrame):
                return_flag = False
                if 'return_rule' in kwargs.keys() and kwargs['return_rule']:
                    return_flag = True
                
                else:
                    kwargs['return_rule'] = True

                df_encoded, rule = self.transform(data, **kwargs)
                total = (df_encoded[rule.dropna().index] == self.neutral).sum(axis=1)

                if return_flag:
                    return (total, rule)
                
                else:
                    return total
            
            else:
                raise TypeError(f"Expected pandas Series or DataFrame, got {type(data)} instead")

        else:
            warnings.warn(f"Encoder {self.name} does not have neutral argument specified, count_neutral will return None")
            return None
