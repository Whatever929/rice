import itertools

from matplotlib import pyplot as plt
import seaborn as sns

def generate_name(prefix):
  for i in itertools.count():
    yield f"{prefix}-{i}"

def plotter(f):
  def plotter_function(*args, figsize=(12, 12), title='Big title', **kwargs):
    plt.figure(figsize=figsize, tight_layout=True)
    f(*args, **kwargs)
    figure = plt.gcf()
    figure.suptitle(title, fontsize=16, y=1.05)
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
  n_row = len(col_list) // n_col + 1
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
    
    elif plot_type == "line":
      if x:
        sns.lineplot(data=data, x=x, y=col, ax=ax, **kwargs)

      else:
        sns.lineplot(data=data, x=data.index, y=col, ax=ax, **kwargs)
    
    elif plot_type == "trend":
      plot_trend(data=data, x=x, y=col, ax=ax, **kwargs)

    elif plot_type == "top":
      temp = data[col].value_counts()
      if top > 0:
        sns.barplot(x=temp.index[0:top], y=temp[0:top])
      else:
        sns.barplot(x=temp.index[-1:top:-1], y=temp[-1:top:-1])

    else:
      raise ValueError(f"Invalid plot_type argument: {plot_type}")

    ax.set_title(f"Distribution of {col}")

def create_moving_average(data, average=7, min_periods=1):
  return data.rolling(average, min_periods=min_periods).mean()

def plot_trend(data, y, x=None, ax=None, 
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
    data = create_moving_average(data[[y]], average=moving_average, min_periods=min_periods)
  
  if ax is None:
    ax = sns.lineplot(data=data, x=x, y=y, label=label)

    if date_index:
      ax_format(ax)

  else:
    ax = sns.lineplot(data=data, x=x, y=y, ax=ax, label=label)

  return ax

def allow_values(data, col, values):
  return data[data[col].isin(values)]