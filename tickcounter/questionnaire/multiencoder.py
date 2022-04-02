import pandas as pd
from ..util import generate_name

from tickcounter.questionnaire import Encoder

class MultiEncoder(object):
  def __init__(self, encoding_rule):
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
    
  def transform(self, data,*, rule_map=None, columns=None, ignore_list=None, return_rule=False, mode="any"):
    result = data.copy()
    encode_rule = None
    if isinstance(data, pd.DataFrame):
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
        # Check for correct format for rule_map
        # Transform according to the rules
        pass

    elif isinstance(data, pd.Series):
      encode_rule = pd.Series(dtype=str, index=[data.name])
      unique_values = result.value_counts().index
      for rule in self.rules.values():
        if mode == "strict":
          if len(set(unique_values) ^ set(rule.target)) == 0:
            result = rule.transform(result)
            encode_rule[data.name] = rule.name
            break
        elif mode == "any":
          if len(set(unique_values) - set(rule.target)) == 0:
            result = rule.transform(result)
            encode_rule[data.name] = rule.name
            break
        else:
          raise ValueError("rule argument can only be strict or any")

    else: 
      raise TypeError(f"Expected pandas Series or DataFrame, got {type(data)} instead")
    
    if return_rule:
      return (result, encode_rule)
    
    else:
      return result
    
  def count_neutral(self, data, **kwargs):
    # Might need to refactor this
    return_flag = False
    if 'return_rule' in kwargs.keys() and kwargs['return_rule']:
        return_flag = True
    else:
        kwargs['return_rule'] = True

    df_encoded, rule = self.transform(data, **kwargs)
    total = None
    if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
      for col, encoder in rule.dropna().iteritems():
        # Need to rewrite this. We transform the thing twice to get the count of neutral! 
        ss_tally = self.rules[encoder].count_neutral(data[col] if isinstance(data, pd.DataFrame) else data)
        # If encoder does not have neutral, it will return None
        if ss_tally is not None:
          if total is None:
            total = pd.DataFrame([ss_tally]).T
          
          else:
            total = pd.concat([total, ss_tally], axis=1)
        else:
          continue
      
      # None will result if there is no neutral specified
      if total is not None:
        total = total.sum(axis=1)
        total.rename("Neutral count", inplace=True)
    
    if return_flag:
      return (total, rule)
    
    else:
      return total