import pandas as pd
from ..util import generate_name

class Label(object):
  name_generator = generate_name("label")

  def __init__(self, label_function, name=None):
    self.label_function = label_function
    self.name = name
    if self.name is None:
      self.name = next(Label.name_generator)
  
  def label(self, data, score_col, **kwargs):
    return self.label_function(data, score_col, **kwargs)