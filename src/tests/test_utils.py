import unittest
import os,logging 
from logging import Logger
from backend.utils import Utils  # absolute import
logging.basicConfig(level=logging.DEBUG)
# go to \src and run python -m unittest tests.test_utils



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
        self.assertTrue(os.path.exists(self.utils.path_join('logs', 'test.log')))

    def test_path_join(self):
        path = self.utils.path_join('folder', 'file.txt')
        self.assertEqual(path, os.path.join(self.utils.cur_dir, 'folder', 'file.txt'))

    def test_tearDown(self):
        self.utils.setup_logger(log_name='teardown.log')
        self.utils.close_logger()
        os.remove(self.utils.path_join('logs', 'teardown.log'))

    def test_make_dir(self):
        fp=self.utils.path_join('test_dir')
        self.assertFalse(os.path.exists(fp))
        self.utils.make_dir(fp)
        self.assertTrue(os.path.exists(fp))
        self.utils.remove_dir(fp)

    def test_dump_df(self):
        input_fp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tests_inputs','subs_df.csv')
        output_fp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tests_outputs','subs_df.csv')
        df=self.utils.read_csv(input_fp)        
        self.utils.dump_df(df,output_fp)
        self.assertTrue(os.path.exists(input_fp))
        self.assertTrue(os.path.exists(output_fp))

    def test_dump_hdf(self):
        input_fp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tests_inputs','subs_df.csv')
        output_fp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tests_outputs','subs_df.h5')
        df=self.utils.read_csv(input_fp)        
        yt_url='https://www.youtube.com/watch?v=tZe0HFFWyoc&ab_channel=DavidLin'
        self.utils.dump_hdf(df,output_fp,meta_dic={'meta':'test','url':yt_url,'title':'test_title'})
        self.assertTrue(os.path.exists(input_fp))
        self.assertTrue(os.path.exists(output_fp))
        
    def test_read_hdf(self):
        input_fp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tests_outputs','subs_df.h5')     
        df,meta=self.utils.read_hdf(input_fp)
        self.assertTrue(len(df)!=0)
        self.assertTrue(len(meta)!=0)
        

###
###
if __name__ == '__main__':
    unittest.main()
