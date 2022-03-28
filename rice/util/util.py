import itertools

def generate_encoding(data, default=False, neutral=False):
  # Repeatedly prompt the user for encoding, then generate a JSON for JSON_Encoder
  # Other parameters are options.
  pass

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
                  n_col, 
                  plot_type, 
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
