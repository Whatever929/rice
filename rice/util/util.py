import itertools

def generate_encoding(data, default=False, neutral=False):
  # Repeatedly prompt the user for encoding, then generate a JSON for JSON_Encoder
  # Other parameters are options.
  pass

def generate_name(prefix):
  for i in itertools.count():
    yield f"{prefix}-{i}"