import unittest

class TestMultiEncoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestEncoder, cls).setUpClass()
        cls.original = pd.read_csv("test\test_data\student_performance\data.csv")
        cls.descrip = pd.read_csv("test\test_data\student_performance\descrip.csv")

    def setUp():
        self.df = TestEncoder.original.copy()

    def tearDown():
        pass