import seaborn as sns
from matplotlib import pyplot as plt

import math

def plotter(f):
  def plotter_function(*args, figsize=(12, 12), title=None, y=1.05, tight_layout=True, **kwargs):
    plt.figure(figsize=figsize, tight_layout=tight_layout)
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
                  rotate=False,
                  suffix="Distribution of",
                  **kwargs):
  '''
  Plot a subplot of specified type on each selected column. 

  Arguments:
  data: Input DataFrame
  col_list: The columns to be plotted.
  n_col: Number of subplots on each row.
  plot_type: Graph type.
  x: The column for x-axis, used for graphs type like line and trend graph.
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

    if rotate:
      _rotate_label(ax, axis='x', rotation=90)

    ax.set_title(f"{suffix} {col}")

def _rotate_label(ax, axis, rotation, **kwargs):
  if axis == 'x':
    ax.set_xticklabels(ax.get_xticklabels(), rotation=rotation, **kwargs)
  
  elif axis == 'y':
    ax.set_yticklabels(ax.get_yticklabels(), rotation=rotation, **kwargs)
  
  else:
    raise ValueError("axis must be either 'x' or 'y'")

def _create_moving_average(data, average=7, min_periods=1):
  return data.rolling(average, min_periods=min_periods).mean()

def _plot_trend(data, y, x=None, ax=None, 
               date_index=True, date_index_name=None, 
               moving_average=None, min_periods=1,
               label=None, ax_format=None):
  '''
  Plot a line graph on the trend on a new or existing ax object.

  Arguments:
  data: A pandas DataFrame. Do not pass a pandas Series
  y: Column name for plotting y-axis
  ax: If None, plot on a new ax object.
  date_index: If passed, the x-axis will be formatted nicely for a date_index
  date_index_name: The index level name holding the date values.
  moving_average: If integer is passed, will create a moving average on y-value.
  min_periods: min_periods for moving_average.
  label: Name for legend
  ax_format: Function that takes an ax for formatting.
  '''
  if date_index:
    if date_index_name is None:
      raise ValueError("Must pass in date_index_name")
    
    if x is not None:
      raise ValueError("Cannot pass x argument when setting date_index to True")
    
    x = data.index.get_level_values(date_index_name).map(lambda x: dt.datetime.strptime(str(x), "%Y-%m-%d %H:%M:%S"))

  if label is None:
    label = y

  if moving_average is not None:
    data = _create_moving_average(data[[y]], average=moving_average, min_periods=min_periods)
  
  if ax is None:
    ax = sns.lineplot(data=data, x=x, y=y, label=label)

    if date_index:
      ax_format(ax)

  else:
    ax = sns.lineplot(data=data, x=x, y=y, ax=ax, label=label)

  return ax

#TODO: Make a function for each plot type
#TODO: Migrate top plotting function, trend and line function to here