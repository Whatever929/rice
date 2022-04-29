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
    # TODO: Do we really want to use heuristics like this? Also there is duplicate checking already
    try:
      mapping = self[column]['values']
    except KeyError as e:
      # If the column is not in the description, return the original values.
      return values

    try:
      if values[0] in mapping.keys():
        return self._num_to_descrip(column, values)
    
    except TypeError as e:
      if values in mapping.keys():
        return self._num_to_descrip(column, values)

    else:
      return self._descrip_to_num(column, values)
  
  def _num_to_descrip(self, column, values):
    mapping = self[column]['values']
    return self._translate(values, mapping)
  
  def _descrip_to_num(self, column, values):
    mapping = {v:k for k, v in self[column]['values'].items()}
    return self._translate(values, mapping)
  
  def _translate(self, values, mapping):
    # Either a list or just a single value
    try:
      result = values.copy()
      for i in range(len(result)):
        result[i] = mapping[result[i]]
    except (AttributeError, KeyError) as e:
      # If values is not a list
      result = mapping[values]
    
    return result
  
  def _descrip_value(self, ax, col, axis='x'):
    with warnings.catch_warnings():
      warnings.simplefilter('ignore')
      try:
        if axis == 'x':
          translated = self.translate(col, [int(item.get_text()) for item in ax.get_xticklabels()])
          ax.set_xticklabels(translated)
        
        elif axis == 'y':
          translated = self.translate(col, [int(item.get_text()) for item in ax.get_yticklabels()])
          ax.set_yticklabels(translated)
        
        else:
          raise ValueError("col argument can only be 'x' or 'y'")
      
      except KeyError as e:
        pass
      
      return ax
  
  def _descrip_title(self, ax, col, default=''):
    try:
      ax.set_title(f"{self[col]['description']}")
    except KeyError as e:
      ax.set_title(default)
    return ax

  def _descrip_legend(self, ax):
    col = ax.get_legend().get_title().get_text()
    for i in ax.get_legend().get_texts():
        # TODO: Fix this, let the translate method can also take single value
        try:
          i.set_text(self.translate(col, int(i.get_text())))
        except KeyError as e:
          pass
    return ax
  
  def _descrip_transform(self, ax, col, descrip_value=False, descrip_title=False, descrip_legend=False, value_axis='x'):
    if descrip_title:
      self._descrip_title(ax=ax, col=col)

    if descrip_value:
      self._descrip_value(ax=ax, col=col, axis=value_axis)

    if ax.get_legend() is not None and descrip_legend:
      self._descrip_legend(ax)

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