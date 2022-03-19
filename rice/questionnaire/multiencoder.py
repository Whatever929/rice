import pandas as pd
from ..util import generate_name

class MultiEncoder(object):
  def __init__(self, encoding_rule):
    if isinstance(encoding_rule, Encoder):
      self.rules = [encoding_rule]
    
    elif isinstance(encoding_rule, list):
      if isinstance(encoding_rule[0], Encoder):
        self.rules = encoding_rule

      else:
        pass
        # Need to convert the dictionary to encoders, and give 
    
    else:
      raise ValueError(f"Expected list of encoder or dictionary objects, got {type(encoding_rule)} instead")
    
  def transform(self, data, rule_map=None, ignore_list=None, return_rule=False, mode="any"):
    """For each column, value count them, then, if the match all, transform, else, can skip"""
    "If rule map is specified, encode using the rule map, else, use the auto one"
    result = data.copy()
    encode_rule = pd.Series(dtype=str, index=data.columns)
    if rule_map is None:
      for i in result.columns:
        if ignore_list is not None and i in ignore_list:
          continue

        else:
          unique_values = result[i].value_counts().index
          for rule in self.rules:
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
      # Check for correct format
      # Transform according to the rules

    if return_rule:
      return (result, encode_rule)
    
    else:
      return result