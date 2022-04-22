import unittest

import pandas as pd
import numpy as np
from tickcounter.questionnaire import Encoder
from pandas.testing import assert_frame_equal, assert_series_equal

class TestEncoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestEncoder, cls).setUpClass()
        cls.original = pd.read_csv("test/test_data/time_management/data.csv")
        cls.descrip = pd.read_csv("test/test_data/time_management/descrip.csv")
        cls.scale_a = {"Strong Agree": 5, "Agree": 4, "Neither": 3, "Disagree": 2, "Strong Disagree": 1}
        cls.scale_b = {"Strong Agree": 1, "Agree": 2, "Neither": 3, "Disagree": 4, "Strong Disagree": 5}
        cls.question_col = [str(i) for i in range(6, 18)]
        cls.encoder_1 = Encoder({
            "Strong Agree": 5,
            "Agree": 4,
            "Neither": 3,
            "Disagree": 2,
            "Strong Disagree": 1
        }, neutral=3, default=3, name="Agreeness", dtype=int)
        cls.encoder_2 = Encoder(template=TestEncoder.encoder_1, invert=True, dtype=int)
        cls.encoder_3 = Encoder(encoding=TestEncoder.encoder_1.encoding, neutral=3, dtype=int)

    def setUp(self):
        self.df = TestEncoder.original.copy()
    
    def test_transform_default_df(self):
        result = TestEncoder.encoder_1.transform(self.df)
        # The original df should not be mutated.
        assert_frame_equal(TestEncoder.original, self.df)
        
        expected = self.df.copy()
        expected[TestEncoder.question_col] = self.df[TestEncoder.question_col].replace(TestEncoder.scale_a)
        expected[TestEncoder.question_col] = expected[TestEncoder.question_col].fillna(3)
        assert_frame_equal(result, expected, check_dtype=False)

    def test_transform_default_ss(self):
        result = TestEncoder.encoder_2.transform(self.df['6'])
        assert_series_equal(TestEncoder.original['6'], self.df['6'])

        expected = self.df['6'].replace(TestEncoder.scale_b)
        expected.fillna(3, inplace=True)
        assert_series_equal(result, expected, check_dtype=False)
    
    def test_transform_columns(self):
        result = TestEncoder.encoder_3.transform(self.df, columns=['6', '7', '8'])
        assert_frame_equal(TestEncoder.original, self.df)

        expected = self.df.copy()
        expected[['6', '7', '8']] = self.df[['6', '7', '8']].replace(TestEncoder.scale_a)
        assert_frame_equal(result, expected, check_dtype=False)
    
    def test_transform_ignore_list(self):
        result = TestEncoder.encoder_1.transform(self.df, ignore_list=['6', '7', '8'])
        assert_frame_equal(TestEncoder.original, self.df)

        expected = self.df.copy()
        expected[TestEncoder.question_col] = self.df[TestEncoder.question_col].replace(TestEncoder.scale_a)
        expected[TestEncoder.question_col] = expected[TestEncoder.question_col].fillna(3)
        expected[['6', '7', '8']] = self.df[['6', '7', '8']]
        assert_frame_equal(result, expected, check_dtype=False)

    def test_transform_return_rule(self):
        result, rule = TestEncoder.encoder_1.transform(self.df, return_rule=True)
        assert_frame_equal(TestEncoder.original, self.df)
        
        expected = pd.Series(index=self.df.columns, dtype='str')
        expected[TestEncoder.question_col] = 'Agreeness'
        assert_series_equal(rule, expected, check_dtype=False)

    def test_transform_mode(self):
        df_new = self.df.copy()
        df_new[['7', '8', '9']] = df_new[['7', '8', '9']].replace("Strong Agree", "Agree")

        df_before = df_new.copy()
        result_1, rule_1 = TestEncoder.encoder_3.transform(df_new, mode='any', return_rule=True)
        result_2, rule_2 = TestEncoder.encoder_3.transform(df_new, mode='strict', return_rule=True)
        assert_frame_equal(df_before, df_new)
        
        expected_1 = df_new.copy()
        expected_1[TestEncoder.question_col] = df_new[TestEncoder.question_col].replace(TestEncoder.scale_a)
        assert_frame_equal(result_1, expected_1, check_dtype=False)

        expected_2 = expected_1.copy()
        expected_2[["7", "8", "9"]] = df_new[["7", "8", "9"]]
        assert_frame_equal(result_2, expected_2, check_dtype=False)

        rule_exp = pd.Series(index=df_new.columns, dtype=str)
        rule_exp[TestEncoder.question_col] = TestEncoder.encoder_3.name
        rule_exp[['7', '8', '9']] = np.NaN
        assert_series_equal(rule_2, rule_exp, check_dtype=False)
    
    def test_transform_mix(self):
        # Test when column and ignore list are used together.
        # Test when column, ignore list and return rules are used together
        # Test when mode and return_rule are used together.
        pass
    
    def test_invert(self):
        # TODO: Might need to rewrite this test
        TestEncoder.encoder_1.invert()
        result_1 = TestEncoder.encoder_1.transform(self.df)
        TestEncoder.encoder_1.invert()
        result_2 = TestEncoder.encoder_1.transform(self.df)
        assert_frame_equal(self.df, TestEncoder.original)

        expected_1 = self.df.copy()
        expected_1[TestEncoder.question_col] = self.df[TestEncoder.question_col].replace(TestEncoder.scale_b)
        expected_1[TestEncoder.question_col] = expected_1[TestEncoder.question_col].fillna(3)
        assert_frame_equal(result_1, expected_1, check_dtype=False)

        expected_2 = self.df.copy()
        expected_2[TestEncoder.question_col] = self.df[TestEncoder.question_col].replace(TestEncoder.scale_a)
        expected_2[TestEncoder.question_col] = expected_2[TestEncoder.question_col].fillna(3)
        assert_frame_equal(result_2, expected_2, check_dtype=False)
    
    def test_count_neutral_ss(self):
        result = TestEncoder.encoder_2.count_neutral(self.df['6'])
        assert_frame_equal(TestEncoder.original, self.df)

        expected = self.df['6'].replace(TestEncoder.scale_b)
        expected.fillna(3, inplace=True)
        expected = (expected == 3).astype(int)
        assert_series_equal(result, expected, check_dtype=False)
    
    def test_count_neutral_df(self):
        result = TestEncoder.encoder_3.count_neutral(self.df)
        assert_frame_equal(TestEncoder.original, self.df)

        expected = self.df.copy()
        expected = (expected == 'Neither')
        expected = expected.sum(axis=1)
        assert_series_equal(result, expected, check_dtype=False)
    
    def test_count_neutral_param(self):
        result = TestEncoder.encoder_1.count_neutral(self.df, columns=['6', '7'], ignore_list=['8'])
        assert_frame_equal(TestEncoder.original, self.df)

        expected = self.df[['6', '7']]
        expected = expected.fillna(3)
        expected = expected.replace(TestEncoder.scale_a)
        expected = (expected == 3).sum(axis=1)
        assert_series_equal(result, expected, check_dtype=False)

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()