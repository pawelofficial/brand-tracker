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
        self.url='https://www.youtube.com/watch?v=ammoIiY3MZo&ab_channel=DavidLin'
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
        enhanced_subs_df=self.an.make_ts_report_calculations() # making json column
        self.assertTrue(isinstance(enhanced_subs_df, pd.DataFrame))
        self.assertTrue(len(enhanced_subs_df.columns)!=len(self.an.subs_df.columns))

        
    def test_make_ts_report(self):
        enhanced_subs_df=self.an.make_ts_report_calculations() # making json column
        ts_report_df,aggregates_d,aggregates_dic_sentiment=self.an.make_ts_report(subs_df=enhanced_subs_df) # making ts report
        print(aggregates_dic_sentiment)
        self.assertTrue(isinstance(ts_report_df, pd.DataFrame))
        self.assertTrue(isinstance(aggregates_d, dict))
        cols=self.an.reports_config['ts_report_columns']
        self.an.utils.dump_df(ts_report_df[cols],dir_fp=self.tests_outputs_dir,fname='ts_report_df.csv')
        self.an.utils.dump_df(enhanced_subs_df,dir_fp=self.tests_outputs_dir,fname='enhanced_subs_df.csv')
###        
    def test_make_plot(self):
        enhanced_subs_df=self.an.make_ts_report_calculations() # making json column
        ts_report_df,aggregates_d,aggregates_dic_sentiment=self.an.make_ts_report(subs_df=enhanced_subs_df) # making ts report 
        png_fp=self.tests_outputs_dir
        self.an.make_plot(ts_report_df=ts_report_df,subs_df=enhanced_subs_df,png_fp=png_fp)
###        
    def test_make_html_report(self):
        enhanced_subs_df=self.an.make_ts_report_calculations()                                           
        ts_report_df,aggregates_d,aggregates_dic_sentiment=self.an.make_ts_report(subs_df=enhanced_subs_df) # making ts report
        png_fp=self.an.utils.path_join(self.tests_inputs_dir,'plot.png')
        self.an.make_plot(ts_report_df=ts_report_df,subs_df=enhanced_subs_df,png_fp=png_fp)
        _,meta_dic=self.an.utils.read_hdf(self.hdf_fp)
        self.an.make_html_report(
            ts_report_df=ts_report_df
            ,aggregates_dic=aggregates_d
            ,png_fp=png_fp
            ,meta_dic=meta_dic
            ,output_dir=self.tests_outputs_dir
        )
###        
    def test_modify_keyword_sentiment_input(self):
        s='bad bad good bitcoin good bad bad market bad bad'
        s='''so is the bull market over or just getting started let's jump in take a look at the news take a look at the charts we also have BlackRock coming out with an ETF application Bitcoin spot ETF um trust application which is a little nuanced but at the end of the day they buy Spot Bitcoin and it's instantly liquid for the investors uh that are also making their bet on coinbase as the custodian and finance continues to be'''
        s2=self.an.modify_keyword_sentiment_input(s,span=1,keywords=['bitcoin','market'])
        self.assertTrue(s2!=s)
        self.assertTrue(s2!='')