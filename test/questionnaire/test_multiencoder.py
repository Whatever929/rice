import unittest

import pandas as pd
import numpy as np
from rice.questionnaire import Encoder, MultiEncoder
from pandas.testing import assert_frame_equal, assert_series_equal

class TestMultiEncoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMultiEncoder, cls).setUpClass()
        cls.original = pd.read_csv("test/test_data/mental_health/data.csv")
        cls.scale_1 = {"No": -1, "Yes": 1, "Don't know": 0, "Some of them": 0, "Not sure": 0, "Maybe": 0}
        cls.scale_2 = {"1-5": 1, "6-25": 2, "26-100": 3, "100-500": 4, "500-1000": 5,  "More than 1000": 6}
        cls.scale_3 = {"Very difficult": -2, "Somewhat difficult": -1, "Don't know": 0, "Somewhat easy": 1,  "Very easy": 2}
        cls.scale_4 = {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4}
        cls.e1 = Encoder({"No": -1, "Yes": 1, "Don't know": 0, "Some of them": 0, "Not sure": 0, "Maybe": 0}, default=0, neutral=0)
        cls.e2 = Encoder({"1-5": 1, "6-25": 2, "26-100": 3, "100-500": 4, "500-1000": 5,  "More than 1000": 6})
        cls.e3 = Encoder({"Very difficult": -2, "Somewhat difficult": -1, "Don't know": 0, "Somewhat easy": 1,  "Very easy": 2}, default=0)
        cls.e4 = Encoder({"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4}, neutral=3)
        cls.col_1 = ['self_employed', 'family_history', 'treatment', 'remote_work',
       'tech_company', 'benefits', 'care_options', 'wellness_program',
       'seek_help', 'anonymity', 'mental_health_consequence',
       'phys_health_consequence', 'coworkers', 'supervisor',
       'mental_health_interview', 'phys_health_interview',
       'mental_vs_physical', 'obs_consequence']
        cls.col_2 = ['no_employees']
        cls.col_3 = ['leave']
        cls.col_4 = ['work_interfere']
        cls.me1 = MultiEncoder([TestMultiEncoder.e1,
                                TestMultiEncoder.e2,
                                TestMultiEncoder.e3,
                                TestMultiEncoder.e4,
                                ])
        cls.me2 = MultiEncoder(TestMultiEncoder.e3)
        cls.me3 = MultiEncoder(TestMultiEncoder.e1)

    def setUp(self):
        self.df = TestMultiEncoder.original.copy()

    def test_transform_default_ss(self):
        result_1 = TestMultiEncoder.me2.transform(self.df['self_employed'])
        result_2 = TestMultiEncoder.me1.transform(self.df['self_employed'])
        assert_frame_equal(self.df, TestMultiEncoder.original)

        expected_1 = self.df['self_employed']
        expected_2 = self.df['self_employed'].replace(TestMultiEncoder.scale_1)
        expected_2 = expected_2.fillna(0)
        assert_series_equal(result_1, expected_1, check_dtype=False)
        assert_series_equal(result_2, expected_2, check_dtype=False)
    
    def test_transform_default_df(self):
        result = TestMultiEncoder.me1.transform(self.df)
        assert_frame_equal(self.df, TestMultiEncoder.original)

        expected = self.df.copy()
        expected[TestMultiEncoder.col_1] = expected[TestMultiEncoder.col_1].replace(TestMultiEncoder.scale_1)
        expected[TestMultiEncoder.col_1] = expected[TestMultiEncoder.col_1].fillna(0)
        expected[TestMultiEncoder.col_2] = expected[TestMultiEncoder.col_2].replace(TestMultiEncoder.scale_2)
        expected[TestMultiEncoder.col_3] = expected[TestMultiEncoder.col_3].replace(TestMultiEncoder.scale_3)
        expected[TestMultiEncoder.col_3] = expected[TestMultiEncoder.col_3].fillna(0)
        expected[TestMultiEncoder.col_4] = expected[TestMultiEncoder.col_4].replace(TestMultiEncoder.scale_4)
        assert_frame_equal(result, expected, check_dtype=False)
    
    def test_transform_rule_map(self):
        pass
    
    def test_transform_ignore_list(self):
        ignore_list = ['self_employed', 'family_history', 'benefits', 'work_interfere']
        result = TestMultiEncoder.me1.transform(self.df, ignore_list = ignore_list)
        assert_frame_equal(self.df, TestMultiEncoder.original)
        
        expected = self.df.copy()
        expected[TestMultiEncoder.col_1] = expected[TestMultiEncoder.col_1].replace(TestMultiEncoder.scale_1)
        expected[TestMultiEncoder.col_1] = expected[TestMultiEncoder.col_1].fillna(0)
        expected[TestMultiEncoder.col_2] = expected[TestMultiEncoder.col_2].replace(TestMultiEncoder.scale_2)
        expected[TestMultiEncoder.col_3] = expected[TestMultiEncoder.col_3].replace(TestMultiEncoder.scale_3)
        expected[TestMultiEncoder.col_3] = expected[TestMultiEncoder.col_3].fillna(0)
        expected[TestMultiEncoder.col_4] = expected[TestMultiEncoder.col_4].replace(TestMultiEncoder.scale_4)
        expected[ignore_list] = self.df[ignore_list]
        assert_frame_equal(result, expected, check_dtype=False)
    
    def test_transform_return_rules(self):
        result, rule = TestMultiEncoder.me2.transform(self.df, return_rule=True)
        assert_frame_equal(self.df, TestMultiEncoder.original)

        expected = self.df.copy()
        expected[TestMultiEncoder.col_3] = expected[TestMultiEncoder.col_3].replace(TestMultiEncoder.scale_3)
        expected[TestMultiEncoder.col_3] = expected[TestMultiEncoder.col_3].fillna(0)
        expected_rule = pd.Series(index=self.df.columns, dtype=str)
        expected_rule[TestMultiEncoder.col_3] = TestMultiEncoder.e3.name
        assert_frame_equal(result, expected, check_dtype=False)
        assert_series_equal(rule, expected_rule)
    
    def test_transform_mode(self):
        result_1 = TestMultiEncoder.me1.transform(self.df, mode='any')
        result_2, rule = TestMultiEncoder.me1.transform(self.df, mode='strict', return_rule=True)
        assert_frame_equal(self.df, TestMultiEncoder.original)

        expected_1 = self.df.copy()
        expected_1[TestMultiEncoder.col_1] = expected_1[TestMultiEncoder.col_1].replace(TestMultiEncoder.scale_1)
        expected_1[TestMultiEncoder.col_1] = expected_1[TestMultiEncoder.col_1].fillna(0)
        expected_1[TestMultiEncoder.col_2] = expected_1[TestMultiEncoder.col_2].replace(TestMultiEncoder.scale_2)
        expected_1[TestMultiEncoder.col_3] = expected_1[TestMultiEncoder.col_3].replace(TestMultiEncoder.scale_3)
        expected_1[TestMultiEncoder.col_3] = expected_1[TestMultiEncoder.col_3].fillna(0)
        expected_1[TestMultiEncoder.col_4] = expected_1[TestMultiEncoder.col_4].replace(TestMultiEncoder.scale_4)
        expected_2 = expected_1.copy()
        expected_2[TestMultiEncoder.col_1] = TestMultiEncoder.original[TestMultiEncoder.col_1]
        expected_rule = pd.Series(index=self.df.columns, dtype=str)
        expected_rule[TestMultiEncoder.col_2] = TestMultiEncoder.e2.name
        expected_rule[TestMultiEncoder.col_3] = TestMultiEncoder.e3.name
        expected_rule[TestMultiEncoder.col_4] = TestMultiEncoder.e4.name
        assert_frame_equal(result_1, expected_1, check_dtype=False)
        assert_frame_equal(result_2, expected_2, check_dtype=False)
        assert_series_equal(rule, expected_rule)

    def test_transform_mix(self):
        # Test when column and ignore list are used together.
        # Test when column, ignore list and return rules are used together
        pass
    
    def test_transform_columns(self):
        # TODO this in code.
        pass
    
    def test_count_neutral_ss(self):
        # On non-matching series, should return None as there is no matching encoder.
        # We cannot assume that we will encode series, just like single encoder, because we don't know which encoder to use.
        result_1 = TestMultiEncoder.me3.count_neutral(self.df[TestMultiEncoder.col_2[0]])
        # On matching series
        result_2 = TestMultiEncoder.me1.count_neutral(self.df[TestMultiEncoder.col_1[0]])
        # On series with no neutral matching
        result_3 = TestMultiEncoder.me2.count_neutral(self.df[TestMultiEncoder.col_3[0]])
        assert_frame_equal(self.df, TestMultiEncoder.original)
        
        expected_2 = (self.df[TestMultiEncoder.col_1[0]] == "Don't know") | (self.df[TestMultiEncoder.col_1[0]].isna())
        expected_2 = expected_2.astype(int)
        expected_2.rename("Neutral count", inplace=True)
        self.assertIsNone(result_1)
        assert_series_equal(result_2, expected_2, check_dtype=False)
        self.assertIsNone(result_3)
    
    def test_count_neutral_df(self):
        # No matching columns
        result_1 = TestMultiEncoder.me2.count_neutral(self.df[TestMultiEncoder.col_1])
        # Matching columns with neutral
        result_2 = TestMultiEncoder.me1.count_neutral(self.df[["self_employed", "work_interfere"]])
        # Matching columns with no neutral
        result_3 = TestMultiEncoder.me2.count_neutral(self.df[TestMultiEncoder.col_3])
        self.assertIsNone(result_1, None)
        df_temp = self.df[["self_employed", "work_interfere"]].copy()
        df_temp['self_employed'] = df_temp['self_employed'].replace(TestMultiEncoder.scale_1)
        tally_1 = self.df['self_employed'].isna() | (self.df['self_employed'] == 0)
        tally_1 = tally_1.astype(int)
        tally_2 = (self.df['work_interfere'] == 'Sometimes').astype(int)
        expected_2 = tally_1 + tally_2
        expected_2.rename("Neutral count", inplace=True)
        assert_series_equal(result_2, expected_2, check_dtype=False)
        self.assertIsNone(result_3, None)

    def test_count_neutral_param(self):
        pass

    def tearDown(self):
        pass