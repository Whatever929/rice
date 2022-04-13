from abc import ABC, abstractmethod

class Findings(object):
    """
    Store information about the findings to be used for findings_list object
    """
    @abstractmethod  
    def describe(self):
        pass

    @abstractmethod
    def describe_short(self):
        pass

    @abstractmethod
    def illustrate(self, ax):
        pass