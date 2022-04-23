from pathlib import Path
import yaml
import json
import warnings

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
  
  def _descrip_value(self, ax, col, axis='x'):
    with warnings.catch_warnings():
      warnings.simplefilter('ignore')
      if axis == 'x':
        translated = self.translate(col, [int(item.get_text()) for item in ax.get_xticklabels()])
        ax.set_xticklabels(translated)
      
      elif axis == 'y':
        translated = self.translate(col, [int(item.get_text()) for item in ax.get_yticklabels()])
        ax.set_yticklabels(translated)
      
      else:
        raise ValueError("col argument can only be 'x' or 'y'")
      
      return ax
  
  def _descrip_title(self, ax, col):
    ax.set_title(f"{self[col]['description']}")
    return ax
  
  def _descrip_transform(self, ax, col, descrip_value=False, descrip_title=False, value_axis='x'):
    try:
      if descrip_title:
        self._descrip_title(ax=ax, col=col)
    except KeyError as e:
      pass

    try:
      if descrip_value:
        self._descrip_value(ax=ax, col=col, axis=value_axis)
    except KeyError as e:
      pass

    return ax

  def get_order(self, column):
    # Get the order of a column values
    mapping = {v:k for k, v in self[column]['values'].items()}
    ordered = sorted(self[column]['values'].values(), key=lambda i: mapping[i])
    return ordered

  def reorder(self, column, values):
    # Sort according to the orders, only for description values
    mapping = {v:k for k,v in self[column]['values'].items()}
    ordered = sorted(values, key=lambda i: mapping[i])
    return ordered

  def __getitem__(self, item):
    return self.descrip[item]