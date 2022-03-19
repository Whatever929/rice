import pandas as pd
from ..util import generate_name

class Questionnaire(object):
    """
    Does not support transform as we have different multiple encodings.
    """  
    def __init__(self, data, scoring=None, descrip=None):
        self.data = data.copy() # Original data
        self.descrip = descrip # Used for plotting and analysis, takes a Description object
        self._cached = {
            "score": None,
            "label": None,
            "data": self.data,
        }

        if scoring:
            self.scoring = scoring if isinstance(scoring, list) else [scoring] # Used for calculating score
        else:
            self.scoring = None

    def score(self):
        if self.scoring:
            if self._cached['score']:
                return self._cached['score']
            
            else:
                result_df = None
                for i in self.scoring:
                    score_ss = i.score(self.data)
                    
                    if result_df is None:
                        result_df = pd.DataFrame([score_ss]).T
                    
                    else:
                        result_df = pd.concat([result_df, score_ss], axis=1)
                
                self._cached['score'] = result_df
                self._cached['data'] = pd.concat([self._cached['data'], self._cached['score']])
                return result_df
            
        else:
            return None

    def label(self):
        if self.scoring:
            if self._cached['label']:
                return self._cached['label']

            else:
                data = None
                if self._cached['score']:
                    data = self._cached['data']
                
                else:
                    data = self.score()

                label_df = None
                for i in self.labeling:
                    cur_label_df = i.label(self.data)
                    cur_label_df.rename(f"Label - {i.name}")
                    
                    if label_df is None:
                        label_df = cur_label_df 
                    
                    else:
                        label_df = pd.concat([label_df, cur_label_df], axis=1)
                return label_df

        else:
            return None


    def hist(self):
        pass

    def hist_item(self):
        pass

    def boxplot(self):
        pass

    def drop(self, idx):
        """
        Do we want to keep the original?
        """
        self.data.drop(idx, inplace=True)
        self.reset_cache()

    def reset_cache(self):
        self._cached = {
            "score": None,
            "label": None,
            "data": self.data,
        }