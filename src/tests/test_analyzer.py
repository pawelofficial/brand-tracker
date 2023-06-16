import unittest
from backend.analyzer import Analyzer
import os 
import pandas as pd 

# go to src python -m unittest tests.test_analyzer
# nadgarstki 
class testAnalyzer(unittest.TestCase):
    def setUp(self):
        self.an = Analyzer()
        self.cur_dir=os.path.dirname(os.path.realpath(__file__))
        self.tests_inputs_dir=os.path.join(self.cur_dir,'tests_inputs')
        self.tests_outputs_dir=os.path.join(self.cur_dir,'tests_outputs')
        self.url='https://www.youtube.com/watch?v=tZe0HFFWyoc&ab_channel=DavidLin'
        
        self.hdf_fp=self.an.utils.path_join(self.tests_inputs_dir,'subs_df.h5')
        self.csv_fp=self.an.utils.path_join(self.tests_inputs_dir,'subs_df.csv')
        self.an.subs_df,self.an.subs_meta=self.an.utils.read_hdf(self.hdf_fp)
  

    def test_read_hdf(self):
        self.an.subs_df,self.an.subs_meta=self.an.utils.read_hdf(self.hdf_fp)
        self.assertTrue(isinstance(self.an.subs_df, pd.DataFrame))
        self.assertTrue(isinstance(self.an.subs_meta, dict))

    def test_read_csv(self):
        self.an.subs_df=self.an.utils.read_csv(self.csv_fp)
        self.assertTrue(isinstance(self.an.subs_df, pd.DataFrame))
        self.assertTrue(isinstance(self.an.subs_meta, dict))
        
    def test_calculate_keywords(self):
        s='bitcoin gold silver apple foobar hejo'
        test_keywords=['bitcoin','gold','silver','moon']
        s,d=self.an.calculate_keywords(s,keywords=test_keywords)
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d!={})
        self.assertTrue(d['bitcoin']==True)
        self.assertTrue(['moon'==False])

    def test_make_calulations(self):
        self.an.make_ts_report_calculations() # making json column
        
    def test_make_ts_report(self):
        self.an.make_ts_report_calculations() # making json column 
        ts_report_df,aggregates_d=self.an.make_ts_report() # making ts report
        self.assertTrue(isinstance(ts_report_df, pd.DataFrame))
        self.assertTrue(isinstance(aggregates_d, dict))
        
    def test_make_plot(self):
        self.an.make_ts_report_calculations() # making json column 
        ts_report_df,aggregates_d=self.an.make_ts_report() # making ts report
        png_fp=self.tests_outputs_dir
        self.an.make_plot(ts_report_df=ts_report_df,png_fp=png_fp)
        
        
#        self.an.make_plot(self.an.subs_df)
#        self.assertTrue(os.path.exists(os.path.join(self.tests_outputs_dir,'plot.png')))