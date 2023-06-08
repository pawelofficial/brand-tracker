import unittest
import os
from logging import Logger
from backend import Utils  



class TestUtils(unittest.TestCase):

    def setUp(self):
        self.utils = Utils()

    def test_init(self):
        self.assertEqual(self.utils.level, 20)  # Default logging level is INFO, which is 20
        self.assertEqual(self.utils.mode, 'w')
        self.assertIsInstance(self.utils.formatter, logging.Formatter)
        self.assertEqual(self.utils.logs_dir, 'logs')
        self.assertIsInstance(self.utils.cur_dir, str)
        self.assertIsNone(self.utils.logger)

    def test_setup_logger(self):
        self.utils.setup_logger(log_name='test.log')
        self.assertIsInstance(self.utils.logger, Logger)
        self.assertEqual(self.utils.logger.level, 20)  # Default logging level is INFO, which is 20
        self.assertTrue(os.path.exists(self.utils._path_join('logs', 'test.log')))

    def test_path_join(self):
        path = self.utils._path_join('folder', 'file.txt')
        self.assertEqual(path, os.path.join(self.utils.cur_dir, 'folder', 'file.txt'))

    def tearDown(self):
        # Clean up created log file after each test
        os.remove(self.utils._path_join('logs', 'test.log'))


if __name__ == '__main__':
    unittest.main()
