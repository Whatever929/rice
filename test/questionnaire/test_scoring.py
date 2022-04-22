import unittest

import pandas as pd
import numpy as np
from tickcounter.questionnaire import Encoder, MultiEncoder, Scoring, IntervalLabel
from pandas.testing import assert_frame_equal, assert_series_equal

class TestScoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestScoring, cls).setUpClass()
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
        cls.e2 = Encoder(template=TestScoring.e1, invert=True, name='Disagree-ness')
        cls.low = [10, 30]
        cls.high = [31, 100]
        cls.l1 = IntervalLabel({'Low': TestScoring.low, 'High': TestScoring.high})
        cls.EXT = [f"EXT{i}" for i in range(1, 11)]
        cls.EST = [f"EST{i}" for i in range(1, 11)]
        cls.AGR = [f"AGR{i}" for i in range(1, 11)]
        cls.CSN = [f"CSN{i}" for i in range(1, 11)]
        cls.OPN = [f"EXT{i}" for i in range(1, 11)]
        cls.s1 = Scoring(encoding={
                        TestScoring.e1: TestScoring.EXT[0::2],
                        TestScoring.e2: TestScoring.EXT[1::2],
                        }, labeling=TestScoring.l1, name='Extraversion')
        cls.s2 = Scoring(encoding={
                        TestScoring.e1: TestScoring.CSN[0::2],
                        TestScoring.e2: TestScoring.CSN[1::2],
                        }, labeling=TestScoring.l1, name='Consciousness')
        cls.s3 = Scoring(encoding={
                        TestScoring.e1: TestScoring.EST[0::2],
                        TestScoring.e2: TestScoring.EST[1::2],
                        }, labeling=TestScoring.l1, name='Neuroticism')
        cls.s4 = Scoring(encoding={
                        TestScoring.e2: TestScoring.AGR[0::2],
                        TestScoring.e1: TestScoring.AGR[1::2],
                        }, labeling=TestScoring.l1, name='Agreeableness')
        cls.s5 = Scoring(encoding={
                        TestScoring.e1: TestScoring.OPN[0::2],
                        TestScoring.e2: TestScoring.OPN[1::2],
                        }, labeling=TestScoring.l1, name='Openness')
        # No encoding function. This means Scoring will use the original value.
        cls.s6 = Scoring(columns=TestScoring.CSN ,labeling=TestScoring.l1, name='Agreeness')

    def setUp(self):
        self.df = TestScoring.original.copy()
    
    def test_transform_df(self):
        result_1 = TestScoring.s1.transform(self.df)
        result_2 = TestScoring.s4.transform(self.df)
        assert_frame_equal(self.df, TestScoring.original)
        expected_1 = self.df.copy()
        expected_1[TestScoring.EXT[0::2]] = expected_1[TestScoring.EXT[0::2]].replace(TestScoring.scale_a)
        expected_1[TestScoring.EXT[1::2]] = expected_1[TestScoring.EXT[1::2]].replace(TestScoring.scale_b)
        expected_1[TestScoring.EXT] = expected_1[TestScoring.EXT].fillna(3)
        expected_2 = self.df.copy()
        expected_2[TestScoring.AGR[1::2]] = expected_2[TestScoring.AGR[1::2]].replace(TestScoring.scale_a)
        expected_2[TestScoring.AGR[0::2]] = expected_2[TestScoring.AGR[0::2]].replace(TestScoring.scale_b)
        expected_2[TestScoring.AGR] = expected_2[TestScoring.AGR].fillna(3)
        assert_frame_equal(result_1, expected_1, check_dtype=False)
        assert_frame_equal(result_2, expected_2, check_dtype=False)

    def test_transform_no_rule(self):
        # Test function when there is no encoding rule specified.
        with self.assertWarns(UserWarning):
            result = TestScoring.s6.transform(self.df)
        assert_frame_equal(self.df, TestScoring.original)
        assert_frame_equal(result, self.df)
    
    def test_transform_param(self):
        # Now only applicable to MultiEncoder encoding rule
        pass
    
    def test_score(self):
        result_1 = TestScoring.s2.score(self.df)
        result_2 = TestScoring.s4.score(self.df)
        assert_frame_equal(self.df, TestScoring.original)
        transformed_1 = self.df.copy()
        transformed_1[TestScoring.CSN[0::2]] = transformed_1[TestScoring.CSN[0::2]].replace(TestScoring.scale_a)
        transformed_1[TestScoring.CSN[1::2]] = transformed_1[TestScoring.CSN[1::2]].replace(TestScoring.scale_b)
        transformed_1[TestScoring.CSN] = transformed_1[TestScoring.CSN].fillna(3)
        expected_1 = transformed_1[TestScoring.CSN].sum(axis=1)
        expected_1.rename(TestScoring.s2.score_col, inplace=True)
        
        transformed_2 = self.df.copy()
        transformed_2[TestScoring.AGR[1::2]] = transformed_2[TestScoring.AGR[1::2]].replace(TestScoring.scale_a)
        transformed_2[TestScoring.AGR[0::2]] = transformed_2[TestScoring.AGR[0::2]].replace(TestScoring.scale_b)
        transformed_2[TestScoring.AGR] = transformed_2[TestScoring.AGR].fillna(3)
        expected_2 = transformed_2[TestScoring.AGR].sum(axis=1)
        expected_2.rename(TestScoring.s4.score_col, inplace=True)

        assert_series_equal(result_1, expected_1, check_dtype=False)
        assert_series_equal(result_2, expected_2, check_dtype=False)
    
    def test_score_no_rule(self):
        result = TestScoring.s6.score(self.df)
        assert_frame_equal(self.df, TestScoring.original)

        expected = self.df[TestScoring.CSN].sum(axis=1)
        expected.rename(TestScoring.s6.score_col, inplace=True)
        assert_series_equal(result, expected, check_dtype=False)
    
    def test_label(self):
        # For now, use the already tested method
        result_1 = TestScoring.s2.label(self.df)
        result_2 = TestScoring.s4.label(self.df)
        assert_frame_equal(self.df, TestScoring.original)

        expected_1 = pd.Series(index=self.df.index, dtype=str)
        expected_2 = pd.Series(index=self.df.index, dtype=str)
        expected_1.rename(TestScoring.s2.label_col[0], inplace=True)
        expected_2.rename(TestScoring.s4.label_col[0], inplace=True)
        score_1 = TestScoring.s2.score(self.df)
        score_2 = TestScoring.s4.score(self.df)
        expected_1[score_1.between(*TestScoring.low)] = "Low"
        expected_1[score_1.between(*TestScoring.high)] = "High"
        expected_2[score_2.between(*TestScoring.low)] = "Low"
        expected_2[score_2.between(*TestScoring.high)] = "High"
        expected_1 = pd.DataFrame([expected_1]).T
        expected_2 = pd.DataFrame([expected_2]).T

        assert_frame_equal(result_1, expected_1, check_dtype=False)
        assert_frame_equal(result_2, expected_2, check_dtype=False)
    
    def test_label_no_rule(self):
        result = TestScoring.s6.label(self.df)
        assert_frame_equal(self.df, TestScoring.original)
        
        score = self.df[TestScoring.CSN].sum(axis=1)
        label_ss = pd.Series(index=self.df.index, dtype=str)
        label_ss[score.between(*TestScoring.low)] = "Low"
        label_ss[score.between(*TestScoring.high)] = "High"
        label_ss.rename(TestScoring.s6.label_col[0], inplace=True)
        expected = pd.DataFrame([label_ss]).T
        assert_frame_equal(result, expected, check_dtype=False)
    
    def test_label_multiple_label(self):
        # Test Scoring object with multiple label
        pass

    def tearDown(self):
        pass