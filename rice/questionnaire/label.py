class Label(object):
  name_generator = generate_name("label")

  def __init__(self, label_rule, name=None):
    """Label rule is a mapping from word to values
    for now, use:
    'LabelA': [0, 15]
    Since we use df.between, and it is both inclusive by default, so
    Ours are also inclusive by default too
    """
    self.label_rule = label_rule
    self.name = name
    if self.name is None:
      self.name = next(Label.name_generator)
  
  def label(self, data, score_col):
    """Only support numerical pandas series, will support multiple score_col in the future"""
    label_ss = pd.Series(index=data.index, dtype=str)
    for label, interval in self.label_rule.items():
      label_ss[data[score_col].between(*interval)] = label
    
    return label_ss