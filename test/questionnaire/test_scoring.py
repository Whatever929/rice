import unittest

import pandas as pd
import numpy as np
from rice.questionnaire import Encoder, MultiEncoder, Scoring
from pandas.testing import assert_frame_equal, assert_series_equal

class TestMultiEncoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMultiEncoder, cls).setUpClass()
        cls.original = pd.read_csv("test/test_data/mental_health/data.csv")

    def setUp(self):
        self.df = TestMultiEncoder.original.copy()

    def tearDown(self):
        pass