import os 
import re 
import psycopg2
import json 
import os 
import psycopg2.extras as extras
import re 
import inspect 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.lines as mlines
#pd.set_option('display.max_columns', None)  # display all columns
#pd.set_option('display.max_rows', None)  # display all rows
pd.set_option('display.max_colwidth', None)  # display all contents of a column
from fuzzywuzzy import fuzz
import nltk 
#nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


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
        self.keywords=['market','gold','bitcoin','cash','tech','stock','crypto'] #   ['cardano','silver','apple','market','fed']
        self.use_fuzzy_matching=False
        self.fuzzy_threshold=80
        self.positive_keywords = ['good', 'improve', 'growth', 'profit', 'benefit', 'up', 'increase','moon','buy','bulish','great','long','euphoria']
        self.negative_keywords = ['bad', 'decline', 'loss', 'risk', 'down', 'decrease','sell','short','dump','crash','bearish','cliff','panic','blood','bloodbath','cautious']
        self.positive_dict = {word: 1 for word in  self.positive_keywords}
        self.negative_dict = {word: -1 for word in self.negative_keywords}
        self.reports_config={
            #'rows_with_keywords_columns':['txt','ts_url','positive_sentiment','negative_sentiment','st']
            'rows_with_keywords_columns':['sentiment','st','ts_url','txt','positive_sentiment','negative_sentiment','en']
            ,'plot_cols':{'x':'st','y':['sentiment','sentiment_ema']}
            ,'plot_markers':{'sentiment':'x','sentiment_ema':'o'}
            ,'plot_colors':{'sentiment':'b','sentiment_ema':'k'}
            ,'plot_linestyles':{'sentiment':'','sentiment_ema':'-'}
            ,'keywords_colors':{'gold':'gold','bitcoin':'blue','crypto':'royalblue','tech':'cyan','market':'red','stock':'darkred','cash':'green','dollar':'lightgreen'}
        
        }
        self.standard_columns={'json_column':'json_column'
                               ,'ts_url':'ts_url'
                               }
        self.png_name = 'plot.png'
        self.png_fp=self.tmp_dir
    
    # find keywords in a string  
    def calculate_keywords(self, text, keywords=None) -> tuple:
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
        return json.dumps(matches),matches  # {'bitcoin': True, 'gold': False, ...}
    
    # calculates sentiment of a string 
    def calculate_sentiment_custom(self,text):
        words = text.split()
        positive_score = sum(self.positive_dict.get(word, 0) for word in words)
        negative_score = sum(self.negative_dict.get(word, 0) for word in words)
        return positive_score, negative_score
    # calulate sentiment on a stinr 
    def calculate_sentiment(self, text) ->tuple:
        sia = SentimentIntensityAnalyzer()
        sentiment_score = sia.polarity_scores(text)
        strong_sentiment=False
        if abs(sentiment_score['compound'])>0.75:
            strong_sentiment=True
        return -sentiment_score['neg'],sentiment_score['pos'],sentiment_score['neu'],sentiment_score['compound'],strong_sentiment 
        
    # poor mans overloading 
    def apply_to_dataframe(self,src_col,tgt_col,fun,subs_df=None):
        if subs_df is None:
            subs_df=self.subs_df    
        if isinstance(tgt_col, list):
            self.apply_to_dataframe_multiple(src_col, tgt_col, fun, subs_df)
        elif isinstance(tgt_col, str):
            self.apply_to_dataframe_single(src_col, tgt_col, fun, subs_df)
        else:
            raise ValueError('tgt_col should be either a string or a list of strings')
        
    # applies function to dataframe - adds new column 
    def apply_to_dataframe_single(self,src_col,tgt_col,fun,subs_df=None,mutate=True):
        if subs_df is None:
            subs_df=self.subs_df    
        tmp_df=subs_df.copy()
        tmp_df[tgt_col]=tmp_df[src_col].apply(fun)
        
        if mutate:
            subs_df[tgt_col]=tmp_df[tgt_col]
            return subs_df
        else:
            return tmp_df    
    
    # applies function to df - adds new columns 
    def apply_to_dataframe_multiple(self,src_col,tgt_col : list ,fun,subs_df=None,mutate=True):
        if subs_df is None:
            subs_df=self.subs_df    
        s = subs_df[src_col].apply(fun)
        out=[]
        for no in range(len(s[0])):
            out.append([i[no] for i in s])
    
        for no,col_name in enumerate(tgt_col):
            subs_df[col_name]=out[no]
            
    def make_ts_report_calculations(self,url = None):
        if url is None:
            url=self.subs_meta['url']
        self.apply_to_dataframe(src_col='txt',tgt_col=['negative_sentiment','positive_sentiment','neutral_sentiment','sentiment','strong_sentiment'] ,fun=self.calculate_sentiment)
        self.apply_to_dataframe(src_col='txt',tgt_col=['json_column','dict_column'],fun=self.calculate_keywords)    
        self.apply_to_dataframe(src_col='st',tgt_col=self.standard_columns['ts_url'],fun=lambda x: self.utils.calculate_url_ts(x,url)) # maybe i should change things so i dont have to do that 

    # makes ts report df - does not mutate subs df 
    def make_ts_report(self,keywords=None,subs_df=None,cols=None,json_column=None):
        if subs_df is None:
            subs_df=self.subs_df
        if cols is None:
            cols=self.reports_config['rows_with_keywords_columns']
        if json_column is None:
            json_column=self.standard_columns['json_column']
        if keywords is None:
            keywords=self.keywords
        
        tmp_df=pd.DataFrame(columns=['keyword',*cols])
        # Create a boolean mask for each keyword and combine them using the logical OR operator
        for keyword in keywords:
            boolean_mask = subs_df[json_column].apply(lambda x: json.loads(x)[keyword] if keyword in json.loads(x) else False)
            selected_rows = subs_df[boolean_mask][cols]
            # Add a new column 'keyword' that stores the current keyword
            selected_rows['keyword'] = keyword
            # Concatenate the selected_rows DataFrame to tmp_df
            tmp_df = pd.concat([tmp_df, selected_rows], ignore_index=True)
            tmp_df=self.utils.move_col_to_end(df=tmp_df,column_to_move='ts_url')
            tmp_df=self.utils.move_col_to_end(df=tmp_df,column_to_move='txt')

        aggregates_d={}
        for keyword in self.keywords:
            msk=tmp_df['keyword']==keyword
            data=tmp_df[msk]['sentiment']
            aggregates_d[keyword]=np.round(data.mean(),3)
            
        msk=subs_df['sentiment']!=0
        aggregates_d['overall_sentiment']=np.round(subs_df[msk]['sentiment'].mean(),3)
        return tmp_df,aggregates_d
        
    def make_plot(self,ts_report_df,subs_df=None,cols=None,png_name=None,png_fp=None):
        if subs_df is None :
            subs_df=self.subs_df
        if cols is None:
            cols=self.reports_config['plot_cols']
        if png_name is None :
            png_name=self.png_name
        if png_fp is None:
            png_fp=self.png_fp
        png_fp=self.utils.path_join(png_fp,png_name)
        print(png_fp)
        tmp_df=subs_df.copy()
        tmp_df['sentiment_ema']=tmp_df['sentiment'].ewm(span=5, adjust=False).mean()
        
        tmp_df['st']=tmp_df['st'].apply(lambda x: self.utils.ts_to_flt(x))
        tmp_df['en']=tmp_df['en'].apply(lambda x: self.utils.ts_to_flt(x))
        ts_report_df['st']=ts_report_df['st'].apply(lambda x: self.utils.ts_to_flt(x))
        ts_report_df['en']=ts_report_df['en'].apply(lambda x: self.utils.ts_to_flt(x))

        plt.figure(figsize=(10,6))
        y_col=cols['y']
        x_col=cols['x']
        marker_dict=self.reports_config['plot_markers']
        color_dict=self.reports_config['plot_colors']
        linestyle_dict=self.reports_config['plot_linestyles']
        if isinstance(y_col, list):
            for col in y_col:
                mask = tmp_df[col] != -999
                plt.plot(tmp_df[x_col][mask], tmp_df[col][mask], marker=marker_dict[col], color=color_dict[col],linestyle=linestyle_dict[col],label=col)

        else:
            mask = tmp_df[y_col] != -999
            plt.plot(tmp_df[x_col][mask], tmp_df[y_col][mask],marker=marker_dict[col], color=color_dict[col],linestyle=linestyle_dict[col],label=col)

        keywords_colors=self.reports_config['keywords_colors']
        for keyword in self.keywords:
            condition_mask = ts_report_df['keyword'] == keyword
            for x, width in zip(ts_report_df[x_col][condition_mask], (ts_report_df['en'] - ts_report_df[x_col])[condition_mask]):
                plt.bar(x, height=2, width=width, bottom=-1, color=keywords_colors[keyword], align='edge', alpha=0.3)

        # Get the legend handles and labels for the plot
        handles, labels = plt.gca().get_legend_handles_labels()

        # For each keyword, create a legend entry and add it to the list
        for keyword, color in keywords_colors.items():
            handles.append(mlines.Line2D([0], [0], color=color, lw=4, label=keyword))

        # Add the combined legend to the plot
       # plt.legend(handles=handles, loc='upper left')
        plt.legend(handles=handles, loc='center left', bbox_to_anchor=(1, 0.5))

        plt.xlabel(x_col)
        plt.ylabel('Sentiment score 1 - positive / -1 -> negative')
        plt.title('Video sentiment')
        plt.grid(True)
        print(png_fp)
        plt.savefig(png_fp)
        plt.close()
if __name__=='__main__':
    an=Analyzer()
    s="""like to talk about the dollar relationship but the higher dollar does put a little pressure on gold I think go all will make new heights this year there's no doubt that I think it's going higher uh I think right now you're"""
    s='gold'
    score=an.calculate_sentiment(s)
    print(score)
    exit(1)
    
    subs_df_fp=an.utils.path_join(an.tmp_dir,'subs_df.h5')
    an.subs_df,an.subs_meta=an.utils.read_hdf(subs_df_fp)

    an.apply_to_dataframe(src_col='txt',tgt_col=['positive_sentiment','negative_sentiment'],fun=an.calculate_sentiment_custom)
    an.apply_to_dataframe(src_col='txt',tgt_col=['negative_sentiment','positive_sentiment','neu','comp'] ,fun=an.calculate_sentiment)
    an.apply_to_dataframe(src_col='txt',tgt_col=an.standard_columns['json_column'],fun=an.calculate_keywords)    
    url='https://www.youtube.com/watch?v=tZe0HFFWyoc&ab_channel=DavidLin'
    url='https://www.youtube.com/watch?v=tZe0HFFWyoc&ab_channel=DavidLin'
    an.apply_to_dataframe(src_col='st',tgt_col=an.standard_columns['ts_url'],fun=lambda x: an.utils.calculate_url_ts(x,url)) # maybe i should change things so i dont have to do that 
    
    an.utils.dump_df(df=an.subs_df,dir_fp=an.tmp_dir,fname='subs_df.csv')
    an.select_rows_with_keywords()

