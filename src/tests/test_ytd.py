import unittest
from backend.ytd import Ytd
import os 
import pandas as pd 

# go to src python -m unittest tests.test_ytd
# nadgarstki 
class TestYtd(unittest.TestCase):
    def setUp(self):
        self.ytd = Ytd()
        self.cur_dir=os.path.dirname(os.path.realpath(__file__))
        self.tests_inputs_dir=os.path.join(self.cur_dir,'tests_inputs')
        self.tests_outputs_dir=os.path.join(self.cur_dir,'tests_outputs')
  

    def test_get_url_title(self, url = None):
        if url is None:
            url='https://www.youtube.com/watch?v=mQExk0xl4_E&ab_channel=belangp'
        title=self.ytd.get_url_title(url=url)
        self.assertEqual(title,'My_10_Year_Outlook')

    def test_download_subs(self,url=None):
        if url is None:
            url='https://www.youtube.com/watch?v=mQExk0xl4_E&ab_channel=belangp'
        self.ytd.vid_title='test'
        self.ytd.download_subs(url=url)
        exists=os.path.exists(self.ytd.raw_fp)
        self.assertTrue(exists)
    
    def test_parse_subs(self,raw_fp=None):
        if raw_fp is None:
            raw_fp=os.path.join(self.tests_inputs_dir,'raw_subs_test_.en.json3')
        exists=os.path.exists(raw_fp)
        self.ytd.raw_fp=raw_fp
        subs_df,subs_fp=self.ytd.parse_subs(output_dir_fp=self.tests_outputs_dir)
        exist=os.path.exists(subs_fp)
        
        print(raw_fp)
        self.assertTrue(exists)
        self.assertTrue(isinstance(subs_df, pd.DataFrame))

    def test_scan_channel(self,url=None):
        if url is None:
            url='https://www.youtube.com/watch?v=mQExk0xl4_E&ab_channel=belangp'
        ds,urls=self.ytd.scan_channel(url=url)
        self.assertTrue(urls!=[])
        self.assertTrue(ds!={})

    def test_concat_on_time(self,subs_fp=None):
        if subs_fp is None:
            subs_fp=os.path.join(self.tests_inputs_dir,'subs_df.csv')
        exists=os.path.exists(subs_fp)
        self.ytd.subs_df=self.ytd.utils.read_csv(subs_fp)
        original_len=len(self.ytd.subs_df)
        self.ytd.concat_on_time()
        new_len=len(self.ytd.subs_df)
        self.assertTrue(original_len>new_len)

        


if __name__=='__main__':
    t=TestYtd()
#    unittest.main()