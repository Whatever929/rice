import pandas as pd
from ..util import generate_name

class MultiEncoder(object):
  def __init__(self, encoding_rule):
    """If more than one encoding rule can be applied in a specific column, the first encoding rule
    will take precedence.
    """
    if isinstance(encoding_rule, Encoder):
      self.rules = {
        encoding_rule.name: encoding_rule
      }
    
    elif isinstance(encoding_rule, list):
      if isinstance(encoding_rule[0], Encoder):
        self.rules = dict()
        for i in encoding_rule:
          self.rules[i.name] = i

      else:
        pass
        # Need to convert the dictionary to encoders, and give default name
    
    else:
      raise ValueError(f"Expected list of encoder or dictionary objects, got {type(encoding_rule)} instead")
    
  def transform(self, data, rule_map=None, ignore_list=None, return_rule=False, mode="any"):
    """For each column, value count them, then, if the match all, transform, else, can skip"""
    "If rule map is specified, encode using the rule map, else, use the auto one"
    "Need to support pd.Series"
    "Can rewrite this, since encoder already support the encoding of the DataFrame, but can be more inefficient"
    result = data.copy()
    encode_rule = pd.Series(dtype=str, index=data.columns)
    if rule_map is None:
      for i in result.columns:
        if ignore_list is not None and i in ignore_list:
          continue

        else:
          unique_values = result[i].value_counts().index
          for rule in self.rules.values():
            if mode == "strict":
              if len(set(unique_values) ^ set(rule.target)) == 0:
                result[i] = rule.transform(result[i])
                encode_rule[i] = rule.name
                break
            elif mode == "any":
              if len(set(unique_values) - set(rule.target)) == 0:
                result[i] = rule.transform(result[i])
                encode_rule[i] = rule.name
                break
            else:
              raise ValueError("rule argument can only be strict or any")

    else:
      pass
      # Check for correct format for rule_map
      # Transform according to the rules

    if return_rule:
      return (result, encode_rule)
    
    else:
      return result
    
    def count_neutral(self, data, **kwargs):
      return_flag = False
      if 'return_rule' in kwargs.keys() and kwargs['return_rule']:
          return_flag = True
      else:
          kwargs['return_rule'] = True

      df_encoded, rule = self.transform(data, **kwargs)
      df_tally = None
      for col, encoder in rule.dropna().iteritems():
        # Need to rewrite this. We transform the thing twice to get the count of neutral! 
        ss_tally = self.rules[encoder].count_neutral(data[col])
        if df_tally is None:
          df_tally = pd.DataFrame([ss_tally]).T
        
        else:
          df_tally = pd.concat([df_tally, ss_tally])
      
      df_tally = df_tally.sum(axis=1)
      
      if return_flag:
        return (df_tally, rule)
      
      else:
        return df_tally