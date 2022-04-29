import seaborn as sns
from matplotlib import pyplot as plt

import math
import warnings

def plotter(f):
  def plotter_function(*args, figsize=(12, 12), title=None, title_y=1.03, tight_layout=True, **kwargs):
    plt.figure(figsize=figsize, tight_layout=tight_layout)
    f(*args, **kwargs)
    figure = plt.gcf()
    if title is not None:
      figure.suptitle(title, fontsize=16, y=title_y)
  return plotter_function
  
@plotter
def plot_each_col(data, 
                  col_list, 
                  plot_type, 
                  n_col=2, 
                  rotate=False,
                  orient='vertical',
                  suffix="Distribution of ",
                  reorder=False,
                  descrip=None,
                  descrip_value=False,
                  descrip_title=False,
                  descrip_legend=False,
                  **kwargs):
  '''
  Plot a subplot of specified type on each selected column. 

  Arguments:
  data: Input DataFrame
  col_list: The columns to be plotted.
  n_col: Number of subplots on each row.
  plot_type: Graph type.
  '''
  if len(col_list) < n_col:
    n_col = len(col_list)

  n_row = math.ceil(len(col_list) / n_col)
  for i, col in enumerate(col_list):
    ax = plt.subplot(n_row, n_col, i + 1)
    order = None
    if reorder and descrip is not None:
      try:
        order = descrip.get_order(col)
      
      except KeyError as e:
        pass
      
    if orient == 'vertical':
      plot_orient = {'x': col}
    elif orient == 'horizontal':
      plot_orient = {'y': col}
    else:
      raise ValueError("orient argument can only be vertical or horizontal")

    if plot_type == "hist": 
      sns.histplot(data=data, **plot_orient, **kwargs)
    
    elif plot_type == "bar":
      sns.barplot(data=data, order=order, **plot_orient, **kwargs)

    elif plot_type == "count":
      sns.countplot(data=data, order=order, **plot_orient, **kwargs)

    elif plot_type == "box":
      sns.boxplot(data=data, **plot_orient, **kwargs)
    
    elif plot_type == 'kde':
      sns.kdeplot(data=data, **plot_orient, **kwargs)

    else:
      raise ValueError(f"Invalid plot_type argument: {plot_type}")

    if rotate:
      _rotate_label(ax, axis='x', rotation=90)

    if descrip is None:
      ax.set_title(f"{suffix}{col}")
    
    else:
      if descrip_title:
        descrip._descrip_title(ax=ax, col=col, default=f"{suffix}{col}")
        
      else:
        ax.set_title(f"{suffix}{col}")

      if descrip_value:
        if orient == 'vertical':
          descrip._descrip_value(ax=ax, col=col, axis='x')
        
        elif orient == 'horizontal':
          descrip._descrip_value(ax=ax, col=col, axis='y')

      if descrip_legend:
        descrip._descrip_legend(ax=ax)
      

def _rotate_label(ax, axis, rotation, **kwargs):
  with warnings.catch_warnings():
    warnings.simplefilter('ignore')
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

@plotter
def compare_dist(data, 
                   feat_1, 
                   feat_2, 
                   n_col=2, 
                   figsize=(8, 8), 
                   kind='pie', 
                   suffix='', 
                   descrip=None, 
                   descrip_title=False,
                   descrip_value=False,
                   **kwargs):
  # TODO: also add descrip_value
  groups = data[feat_1].value_counts()

  if len(groups) < n_col:
    n_col = len(groups)
  n_row = math.ceil(len(groups) / n_col)

  for i, group in enumerate(groups.index):
    ax = plt.subplot(n_row, n_col, i + 1)
    ax.set_title(f"{suffix}{group}")
    data_group = data[data[feat_1] == group][feat_2]
    payload = _plot_pie(data_group, ax, **kwargs)
    
    if len(payload) == 3:
      patches, texts, autotexts = payload
    else:
      patches, texts = payload

    if descrip is not None:
      if descrip_title:
        ax.set_title(descrip.translate(column=feat_1, values=int(ax.get_title())))
    
      if descrip_value:
        for i in texts:
          i.set_text(descrip.translate(column=feat_2, values=int(i.get_text())))

def _plot_pie(data, ax, top=None, **kwargs):
  groups = data.value_counts()
  total = groups.sum()
  def my_fmt(x):
    # Source: https://stackoverflow.com/questions/59644751/matplotlib-pie-chart-show-both-value-and-percentage
    return '{:.2f}%\n({:.0f})'.format(x, total*x/100)
  return ax.pie(groups.values, labels=groups.index, 
                autopct=my_fmt, **kwargs)

#TODO: Make a function for each plot type
#TODO: Migrate top plotting function, trend and line function to here