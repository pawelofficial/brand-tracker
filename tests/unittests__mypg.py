import unittest
from unittest.mock import patch, MagicMock
import sys 
import os 
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from mypg import mypg

class TestMypg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mypg = mypg()

    def test_set_conn(self):
        conn = self.mypg._set_conn()
        self.assertIsNotNone(conn)

    def test_set_curr(self):
        curr = self.mypg._set_curr()
        self.assertIsNotNone(curr)

    @patch.object(mypg, '_set_curr', return_value=MagicMock())
    def test_select_all(self, mock_set_curr):
        self.mypg.select('SELECT * FROM test_table')
        self.assertIsNotNone(self.mypg.rows)

    @patch.object(mypg, '_set_curr', return_value=MagicMock())
    def test_select_nrows(self, mock_set_curr):
        self.mypg.select('SELECT * FROM test_table', nrows=10)
        self.assertIsNotNone(self.mypg.rows)

    def test_ping(self):
        with patch('builtins.print') as mock_print:
            res = self.mypg.ping()
            self.assertIsNotNone(res)

    def test_read_query(self):
        query = self.mypg.read_query('_select_', _tablename_='test_table')
        self.assertIsNotNone(query)
        self.assertIn('test_table', query)

if __name__ == '__main__':
    unittest.main()
