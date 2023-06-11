import os 
import re 
import psycopg2
import json 
import os 
import psycopg2.extras as extras
import re 
import inspect 
import pandas as pd 
from fuzzywuzzy import fuzz

if __name__!='__main__':    
    from .utils import Utils   # import for tests 
else:
    from utils import Utils 

# class for analyzing and doing stuff with text 
class Analyzer():
    def __init__(self) -> None:
        # objects 
        self.utils = Utils()
        self.logger=self.utils.setup_logger(log_name='ytd.log')
        self.tmp_dir=self.utils.path_join(self.utils.cur_dir,'data','tmp')
        
        self.subs_fp=None 
        self.subs_df=None 
        self.keywords=['bitcoin','cardano','gold','silver','apple']
        self.use_fuzzy_matching=False
        self.fuzzy_threshold=80
        self.positive_keywords = ['good', 'improve', 'growth', 'profit', 'benefit', 'up', 'increase','moon','buy','bulish','great','long']
        self.negative_keywords = ['bad', 'decline', 'loss', 'risk', 'down', 'decrease','sell','short','dump','crash','bearish','cliff']
    
    def scan_subs_df(self,keywords=None,subs_df=None):
        #keyword=keywords[0]
        if subs_df is None:
            subs_df=self.subs_df
        if keywords is None:
            keywords=self.keywords
        matches={k:None for k in keywords}
        for no, row in subs_df.iterrows():
            for keyword in keywords:
                
                escaped_word = re.escape(keyword)
                pattern = r'\b' + escaped_word + r'\b'
                match = re.search(pattern.lower(), row['txt'].lower() )
                if self.use_fuzzy_matching:
                    match=fuzz.ratio(keyword.lower(), row['txt'].lower()) > self.fuzzy_threshold
                
                if match:
                    matched=True
                else:
                    matched=False
                matches[keyword]=matched
            subs_df.loc[no,'json'] = json.dumps(matches) # gotta do json dumps so psycopg worko
        return subs_df
        
    def calculate_sentiment(self,text):
        positive_score = sum(word in text.lower().split() for word in self.positive_keywords)
        negative_score = sum(word in text.lower().split() for word in self.negative_keywords)
        return positive_score - negative_score




if __name__=='__main__':
    pass
    #wf__recreate_schema()
    