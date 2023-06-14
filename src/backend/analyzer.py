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
        self.subs_meta=None # metadata of subs df 
        self.keywords=['bitcoin','cardano','gold','silver','apple']
        self.use_fuzzy_matching=False
        self.fuzzy_threshold=80
        self.positive_keywords = ['good', 'improve', 'growth', 'profit', 'benefit', 'up', 'increase','moon','buy','bulish','great','long','euphoria']
        self.negative_keywords = ['bad', 'decline', 'loss', 'risk', 'down', 'decrease','sell','short','dump','crash','bearish','cliff','panic','blood','bloodbath','cautious']
        self.positive_dict = {word: 1 for word in  self.positive_keywords}
        self.negative_dict = {word: -1 for word in self.negative_keywords}
    
    # calculates sentiment based on positive and negative keywords
    def calculate_keywords(self, text, keywords=None):
        if keywords is None:
            keywords = self.keywords

        matches = {k: None for k in keywords}

        for keyword in keywords:
            escaped_word = re.escape(keyword)
            pattern = r'\b' + escaped_word + r'\b'
            match = re.search(pattern.lower(), text.lower())
            if self.use_fuzzy_matching:
                match = fuzz.ratio(keyword.lower(), text.lower()) > self.fuzzy_threshold

            matches[keyword] = bool(match)

        return json.dumps(matches)  # jsonify the matches


        # ads sentiment of a string 
    
    # calculates sentiment of a string 
    def calculate_sentiment(self,text):
        words = text.split()
        positive_score = sum(self.positive_dict.get(word, 0) for word in words)
        negative_score = sum(self.negative_dict.get(word, 0) for word in words)
        return positive_score, negative_score

    # adds series to a dataframe 
    def add_col_to_df(self,col_series,col_name, subs_df=None):
        if subs_df is None:
            subs_df=self.subs_df
        subs_df[col_name]=col_series
            
    # poor mans overloading 
    def apply_to_dataframe(self,src_col,tgt_col,fun,subs_df=None):
        if subs_df is None:
            subs_df=self.subs_df    
        if isinstance(tgt_col, list):
            # If tgt_col is a list, then we assume that multiple columns will be returned
            self.apply_to_dataframe_multiple(src_col, tgt_col, fun, subs_df)
        elif isinstance(tgt_col, str):
            # If tgt_col is a string, then we assume that only one column will be returned
            self.apply_to_dataframe_single(src_col, tgt_col, fun, subs_df)
        else:
            raise ValueError('tgt_col should be either a string or a list of strings')
        
    # applies function to dataframe - adds new column 
    def apply_to_dataframe_single(self,src_col,tgt_col,fun,subs_df=None):
        if subs_df is None:
            subs_df=self.subs_df    
        subs_df[tgt_col]=subs_df[src_col].apply(fun)
        
    # applies function to df - adds new columns 
    def apply_to_dataframe_multiple(self,src_col,tgt_col : list ,fun,subs_df=None):
        if subs_df is None:
            subs_df=self.subs_df    
        s = subs_df[src_col].apply(fun)
        out=[]
        for no in range(len(s[0])):
            out.append([i[no] for i in s])
    
        for no,col_name in enumerate(tgt_col):
            subs_df[col_name]=out[no]
            


if __name__=='__main__':
    an=Analyzer()
    subs_df_fp=an.utils.path_join(an.tmp_dir,'subs_df.h5')
    an.subs_df,an.subs_meta=an.utils.read_hdf(subs_df_fp)
    an.make_keywords_column()
    an.apply_to_dataframe(src_col='txt',tgt_col=['positive_sentiment','negative_sentiment'],fun=an.calculate_sentiment)
    an.apply_to_dataframe(src_col='txt',tgt_col='keywords_json',fun=an.calculate_keywords)
    an.utils.dump_df(df=an.subs_df,dir_fp=an.tmp_dir,fname='subs_df.csv')
    print(an.subs_df)
    print(an.subs_meta)
    