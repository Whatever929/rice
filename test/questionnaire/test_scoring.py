import unittest

import pandas as pd
import numpy as np
from rice.questionnaire import Encoder, MultiEncoder, Scoring
from pandas.testing import assert_frame_equal, assert_series_equal

class TestScoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMultiEncoder, cls).setUpClass()
        cls.original = pd.read_csv("test/test_data/big_five/data_reduced.csv")
        cls.scale_a = {
                    0.0: 3,
                    1.0: 1,
                    2.0: 2,
                    3.0: 3,
                    4.0: 4,
                    5.0: 5,
                    }
        cls.scale_b = {
                    0.0: 3,
                    1.0: 5,
                    2.0: 4,
                    3.0: 3,
                    4.0: 2,
                    5.0: 1,
                    }
        cls.e1 = Encoder(TestScoring.scale_a, default=3, neutral=3, name='Agree-ness')
        cls.e2 = Encoder(template=e1, inverse=True, name='Disagree-ness')
        cls.s1 = Scoring(encoding={
                        e1: EXT[0::2],
                        e2: EXT[1::2],
                        }, labeling=l1, name='Extraversion')
        cls.s2 = Scoring(encoding={
                        e1: [0::]
                        }, labeling=l1, name='Consciousness')
        cls.EXT = [f"EXT{i}" for i in range(1, 11)]
        cls.EST = [f"EST{i}" for i in range(1, 11)]
        cls.AGR = [f"AGR{i}" for i in range(1, 11)]
        cls.CSN = [f"CSN{i}" for i in range(1, 11)]
        cls.OPN = [f"EXT{i}" for i in range(1, 11)]
        

    def setUp(self):
        self.df = TestMultiEncoder.original.copy()

    def tearDown(self):
        pass