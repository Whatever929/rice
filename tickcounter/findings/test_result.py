class TestResult(object):
    def __init__(self, name, statistic, pvalue, dof=None, expected=None):
        self.name = name
        self.statistic = statistic
        self.pvalue = pvalue
        self.dof = dof
        self.expected = expected