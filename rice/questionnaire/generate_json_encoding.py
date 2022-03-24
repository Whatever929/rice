import json

def generate_json_encoding(data, *, neutral=False, default=False, filename="encoding.json", dtype=str):
    # Use this one https://pypi.org/project/keyboard/, for implementing undo option and also skip
    # Might need to use sampling if the data is very large
    encoding = dict()
    for col in data.columns:
        if input(f"Encode {col}? (y/n) ") == 'n':
            continue 
        else:
            cur_dict = dict()
            mapping_dict = dict()
            for value in data[col].value_counts().index:
                mapping_dict[value] = dtype(prompt_encoding(col, value))
            cur_dict['encoding'] = mapping_dict
            if neutral:
                neutral_value = prompt_neutral(col, value)
                if neutral_value != '':
                    cur_dict['neutral'] = dtype(neutral_value)
            if default:
                default_value = prompt_default(col, value)
                if default_value != '':
                    cur_dict['default'] = dtype(default_value)
            encoding[col] = cur_dict
    with open(filename, 'w') as f:
        json.dump(encoding, f, indent=4)
    return json.dumps(encoding, indent=4)


def prompt_encoding(col_name, value):
    inp = input(f"{col_name} - encode '{value}' as? ")
    return inp

def prompt_neutral(col_name, value):
    inp = input(f"{col_name} - neutral value? ")
    return inp

def prompt_default(col_name, value):
    inp = input(f"{col_name} - default value? ")
    return inp
