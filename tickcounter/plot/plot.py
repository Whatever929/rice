import seaborn as sns
from matplotlib import pyplot as plt

import math

def plotter(f):
  def plotter_function(*args, figsize=(12, 12), title=None, y=1.05, **kwargs):
    plt.figure(figsize=figsize, tight_layout=True)
    f(*args, **kwargs)
    figure = plt.gcf()
    if title is not None:
      figure.suptitle(title, fontsize=16, y=y)
  return plotter_function
  
@plotter
def plot_each_col(data, 
                  col_list, 
                  plot_type, 
                  n_col=2, 
                  x=None,
                  top=10, 
                  **kwargs):
  '''
  Plot a subplot of specified type on each selected column. 

  Arguments:
  data: Input DataFrame
  col_list: The columns to be plotted.
  n_col: Number of subplots on each row.
  plot_type: Graph type.
  x: The column for x-axis, used for graphs type like line and trend graph.
  top: For "top" plot_type. If positive, get the top most frequent values, else get the least frequent values.
  '''
  if len(col_list) < n_col:
    n_col = len(col_list)
  n_row = math.ceil(len(col_list) / n_col)
  for i, col in enumerate(col_list):
    ax = plt.subplot(n_row, n_col, i + 1)
    if plot_type == "hist":
      sns.histplot(data=data, x=col, multiple="stack", **kwargs)
    
    elif plot_type == "bar":
      sns.barplot(data=data, x=col, **kwargs)

    elif plot_type == "count":
      sns.countplot(data=data, x=col, **kwargs)

    elif plot_type == "box":
      sns.boxplot(data=data, x=col, **kwargs)
    
    elif plot_type == 'kde':
      sns.kdeplot(data=data, x=col, **kwargs)

    else:
      raise ValueError(f"Invalid plot_type argument: {plot_type}")

    ax.set_title(f"Distribution of {col}")