from pathlib import Path
import yaml
import json

class Description(object):
  def __init__(self, descrip):
    if isinstance(descrip, dict):
      self.descrip = descrip
    
    elif isinstance(descrip, str):
      filepath = Path(descrip)
      if filepath.suffix == '.json':
        self.descrip = json.load(descrip)
      
      elif filepath.suffix == '.yaml' or filepath.suffix == '.yml':
        with open(descrip, "r") as stream:
          try:
              self.descrip = yaml.safe_load(stream)
          except yaml.YAMLError as exc:
              print(exc)
      else:
        raise ValueError()
    
    else:
      raise TypeError(f"Must take either dict object or str object")
  
  def translate(self, column, values):
    # Can be two ways, will use heuristics to decide the mapping
    mapping = self[column]['values']
    if values[0] in mapping.keys() and values[1] in mapping.keys():
      return self._num_to_descrip(column, values)

    else:
      return self._descrip_to_num(column, values)
  
  def _num_to_descrip(self, column, values):
    mapping = self[column]['values']
    result = values.copy()
    for i in range(len(result)):
      result[i] = mapping[result[i]]
    return result
  
  def _descrip_to_num(self, column, values):
    mapping = {v:k for k, v in self[column]['values'].items()}
    result = values.copy()
    for i in range(len(result)):
      result[i] = mapping[result[i]]
    return result
  
  def get_order(self, column):
    # Get the order of a column values
    mapping = {v:k for k, v in self[column]['values'].items()}
    ordered = sorted(self[column]['values'].values(), key=lambda i: mapping[i])
    return ordered

  def reorder(self, column, values):
    # Sort according to the orders, only for description values
    mapping = {v:k for k,v in self[column]['values'].items()}
    ordered = sorted(values, key=lambda i: mapping[i])

  def __getitem__(self, item):
    return self.descrip[item]