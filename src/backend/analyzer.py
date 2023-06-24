
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
import base64
from transformers import pipeline
from multiprocessing import Process, freeze_support
import datetime
import string
#pd.set_option('display.max_columns', None)  # display all columns
#pd.set_option('display.max_rows', None)  # display all rows
###pd.set_option('display.max_colwidth', None)  # display all contents of a column
from fuzzywuzzy import fuzz
import nltk 
#nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

if __name__!='__main__':    
    from .utils import Utils   # import for tests 
    from .punctuate import RestorePuncts
else:
    from utils import Utils 
    from punctuate import RestorePuncts

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
            'rows_with_keywords_columns':['st','ts_url','txt','sadness','joy','love','anger','fear','surprise','how_strong','en']
            ,'plot_cols':{'x':'st','y':['sadness','joy','love','anger','fear','surprise']}
            #,'plot_markers':{'sadness':'x','joy':'x','anger':'x','fear':'x','surprise':'x','love':'x'}
            #,'plot_linestyles':{'sadness':'-','joy':'-','anger':'-','fear':'-','surprise':'-','love':'-'}
            ,'plot_markers': {'sadness': 'x', 'joy': 'o', 'anger': '^', 'fear': 's', 'surprise': 'p', 'love': '*'}
            ,'plot_linestyles': {'sadness': '-', 'joy': '--', 'anger': '-.', 'fear': ':', 'surprise': '-', 'love': '--'}

            ,'plot_colors':{'sadness':'blue','joy':'gold','anger':'black','fear':'red','surprise':'green','love':'magenta'}
            
            ,'keywords_colors':{'gold':'gold','bitcoin':'blue','crypto':'royalblue','tech':'cyan','market':'red','stock':'darkred','cash':'green','dollar':'lightgreen'}
            #,'sentiment_colors':{'sadness':'blue','joy':'gold','anger':'black','fear':'red','surprise':'green','love':'magenta'}
            ,'sentiment_colors':{'sadness':'black','joy':'black','anger':'black','fear':'black','surprise':'black','love':'black'}
            ,'aggregate_sentiment_column':None
            ,'ts_report_columns':['keyword','sadness','joy','love','anger','fear','surprise','how_strong','st','ts_url','txt']
            ,'sentiment_columns':['sadness','joy','love','anger','fear','surprise']
        }
        self.standard_columns={'json_column':'json_column'
                               ,'ts_url':'ts_url'
                               }
        self.png_name = 'plot.png'
        self.png_fp=self.tmp_dir
        self.rp=RestorePuncts()
        self.nlp = pipeline("text-classification"
                            ,model='bhadresh-savani/distilbert-base-uncased-emotion'
                            , top_k=None) # ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise']
        self.nlp_sentiments=['sadness', 'joy', 'love', 'anger', 'fear', 'surprise']
    
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
    
    # dont consider whole line when there is a keyword in string but only its vicinity for more accuracy 
    def modify_keyword_sentiment_input(self, text,span=10,keywords=None) :
        if keywords is None:
            keywords = self.keywords
        words=text.split()
        #words_lower=[k.lower() for k in words]
        words_lower = [k.lower().translate(str.maketrans('', '', string.punctuation)) for k in words]
        
        condition=[k in words_lower for k in keywords] 
        if not any(condition):
            return text 
        indexes=[]
        for keyword in keywords: # if there is more than one keyword in string then use all and a mean index 
            try:
                i=words_lower.index(keyword)
            except Exception as er:
                continue 
            indexes.append(i)
        mean_index=int(np.mean(indexes))
        new_words=words[mean_index-span:mean_index+span+1]
        #if condition:
        #    print(text)
        #    print('-----')
        #    print(' '.join(new_words))
        #    print(indexes)
        #    print(mean_index)
        #    input('wait') 
        return ' '.join(new_words)
            
        
    
    # calculates sentiment of a string 
    def calculate_sentiment_custom(self,text):
        def parse_output(result,nlp):
            keys_dic={v:'' for k,v in nlp.model.config.id2label.items()}
            for d in result:
                label=d['label']
                score=d['score']
                if label not in keys_dic:
                    raise 
                else:
                    keys_dic[label]=np.round(score,3)*100
            return keys_dic
        text=self.modify_keyword_sentiment_input(text)
        result = self.nlp(text)[0]
        d=parse_output(result,self.nlp)
        
        my_labels=['very strong','somewhat strong','neutral']
        for label in my_labels:
            vals=[v for k,v in d.items()]
            if any(vals)>75:
                label=my_labels[0]
            elif any(vals)>50:
                label=my_labels[1]
            else:
                label=my_labels[2]
            
        d['how_strong']=label
        return [d[k] for k in  d.keys()] # ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'] 

    
    # calulate sentiment on a stinr 
    def calculate_sentiment_basic(self, text) ->tuple:
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
            
    def make_ts_report_calculations(self,url = None,subs_df=None,mutate=False):
        if url is None:
            url=self.subs_meta['url']
        if subs_df is None:
            subs_df=self.subs_df
        if mutate:
            tmp_df=subs_df
        else:
            tmp_df=subs_df.copy()
            
        #self.apply_to_dataframe(subs_df=tmp_df,src_col='txt',tgt_col=['negative_sentiment','positive_sentiment','neutral_sentiment','sentiment','strong_sentiment'] ,fun=self.calculate_sentiment)
        self.apply_to_dataframe(subs_df=tmp_df,src_col='txt',tgt_col=['sadness','joy','love','anger','fear','surprise','how_strong'] ,fun=self.calculate_sentiment_custom)
        self.apply_to_dataframe(subs_df=tmp_df,src_col='txt',tgt_col=['json_column','dict_column'],fun=self.calculate_keywords)    
        self.apply_to_dataframe(subs_df=tmp_df,src_col='st',tgt_col=self.standard_columns['ts_url'],fun=lambda x: self.utils.calculate_url_ts(x,url)) # maybe i should change things so i dont have to do that 
        return tmp_df

    # makes ts report df - does not mutate subs df 
    # requires additional columns json_column,sentiment coming from make_ts_report_calculations
    def make_ts_report(self,keywords=None,subs_df=None,cols=None,json_column=None,sentiment_cols=None):
        if subs_df is None:
            subs_df=self.subs_df
        if cols is None:
            cols=self.reports_config['rows_with_keywords_columns']
        if json_column is None:
            json_column=self.standard_columns['json_column']
        if keywords is None:
            keywords=self.keywords
        if sentiment_cols is None:
            sentiment_cols=self.reports_config['sentiment_columns']
        
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


        aggregates_dic_keywords = {keyword: {sentiment_col: None for sentiment_col in sentiment_cols} for keyword in self.keywords}

        for sentiment_col in sentiment_cols:
            for keyword in self.keywords:
                msk=tmp_df['keyword']==keyword                                  # get rows with a keyword 
                data=tmp_df[msk][sentiment_col]
                aggregates_dic_keywords[keyword][sentiment_col]=np.round(data.mean(),3)

        aggregates_dic_sentiment={emotion:None for emotion in sentiment_cols}
        for col in sentiment_cols:
            msk=tmp_df[col]!=0
            aggregates_dic_sentiment[col]=np.round(tmp_df[msk][col].mean(),3)
    

        return tmp_df,aggregates_dic_keywords,aggregates_dic_sentiment

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

        tmp_df=subs_df.copy()
        aggregate_sentiment_column=self.reports_config['aggregate_sentiment_column']
        if aggregate_sentiment_column is not None:
            tmp_df[aggregate_sentiment_column+'_ema']=tmp_df[aggregate_sentiment_column].ewm(span=5, adjust=False).mean()
        tmp_df['st_bu']=tmp_df['st']
        tmp_df['st_bu'] = tmp_df['st_bu'].apply(lambda x: datetime.datetime.strptime(x, '%H:%M:%S.%f').strftime('%M:%S'))

        tmp_df['st']=tmp_df['st'].apply(lambda x: self.utils.ts_to_flt(x))
        tmp_df['en']=tmp_df['en'].apply(lambda x: self.utils.ts_to_flt(x))
        ts_report_df['st']=ts_report_df['st'].apply(lambda x: self.utils.ts_to_flt(x))
        ts_report_df['en']=ts_report_df['en'].apply(lambda x: self.utils.ts_to_flt(x))

        plt.figure(figsize=(10,6))
        y_col=cols['y']
        x_col=cols['x']
        marker_dict=self.reports_config['plot_markers']
        color_dict=self.reports_config['sentiment_colors']
        linestyle_dict=self.reports_config['plot_linestyles']

        if isinstance(y_col, list):
            for col in y_col:
                mask = tmp_df[col] != -999
                data=tmp_df[col][mask].ewm(span=5, adjust=False).mean()
                max_y = data.max()
                max_x = tmp_df[x_col][mask][data.idxmax()]
                plt.plot(tmp_df[x_col][mask], data, marker=marker_dict[col], color=color_dict[col],linestyle=linestyle_dict[col],label=col)
                plt.annotate(col, (max_x, max_y), textcoords="offset points", xytext=(10,0))
        else:
            mask = tmp_df[y_col] != -999
            data=tmp_df[y_col][mask].ewm(span=5, adjust=False).mean()
            plt.plot(tmp_df[x_col][mask], data,marker=marker_dict[col], color=color_dict[col],linestyle=linestyle_dict[col],label=col)

        keywords_colors=self.reports_config['keywords_colors']
        for keyword in self.keywords:
            condition_mask = ts_report_df['keyword'] == keyword
            for x, width in zip(ts_report_df[x_col][condition_mask], (ts_report_df['en'] - ts_report_df[x_col])[condition_mask]):
                plt.bar(x, height=100, width=width, bottom=0, color=keywords_colors[keyword], align='edge', alpha=0.3)

        handles, labels = plt.gca().get_legend_handles_labels()

        for keyword, color in keywords_colors.items():
            handles.append(mlines.Line2D([0], [0], color=color, lw=4, label=keyword))


        plt.legend(handles=handles, loc='center left', bbox_to_anchor=(1, 0.5))

        plt.xlabel('timestamp')
        plt.ylabel('Emotional load')
        plt.title('Video Emotions')
        plt.grid(axis='y', linestyle='--', linewidth=0.5, color='black')
        ax2 = plt.gca().twiny()
        ax2.grid(True, linestyle='--', linewidth=0.5, color='black')

        # Calculate new ticks locations assuming that 'st' and 'st_bu' have similar ranges
        new_ticks = np.linspace(tmp_df['st'].min(), tmp_df['st'].max(), len(tmp_df['st_bu']))

        # Set the new ticks and labels
        ax2.set_xticks(new_ticks)
        ax2.set_xticklabels(tmp_df['st_bu'], rotation=45)

        print(png_fp)
        plt.savefig(png_fp)
        plt.close()

    def make_html_report(self,ts_report_df,aggregates_dic,png_fp,meta_dic,output_dir=None,fname=None):
        if output_dir is None:
            output_dir=self.tmp_dir
        if fname is None:
            fname='html_report.html'
        out_fp=self.utils.path_join(output_dir,fname)
        
        vid_title=meta_dic['title']
        vid_url=meta_dic['url']
        
        title=f'''<h1>Transcript Report for <a href="{vid_url}">{vid_title}</a></h1>'''
        agg_d=f'''<pre>{json.dumps(aggregates_dic,indent=4)}</pre>'''
        img=open(png_fp,'rb').read()
        img_base64 = base64.b64encode(img).decode()
        html=ts_report_df.to_html()
        df_lines=[]
        df_lines.append(f"<table>")
        df_lines.append(f"<tr>")
        for col in ts_report_df.columns:
            if col in self.reports_config['ts_report_columns']:
                df_lines.append(f"<th>{col}</th>")
        df_lines.append(f"</tr>")
        for _,row in ts_report_df.iterrows():
            dic=row.to_dict()
            dic['st']=self.utils.flt_to_ts(dic['st'])
            dic['en']=self.utils.flt_to_ts(dic['en'])
            df_lines.append(f"<tr>")
            for k,v in dic.items() :
                if k in self.reports_config['ts_report_columns']:
                    df_lines.append(f"<td>{v}</td>")
            df_lines.append(f"</tr>")
        df_lines.append("</table>")
        df_lines='\n'.join(df_lines)
        
        style = '''
            <style>
                table {
                    border: 1px solid black;
                    border-collapse: collapse;
                }
                td, th {
                    border: 1px solid #ddd;
                    padding: 8px;
                }
                th {
                    padding-top: 12px;
                    padding-bottom: 12px;
                    text-align: left;
                    background-color: #4CAF50;
                    color: white;
                }
            </style>
            '''
        email_contents=f'''\
            {style}
            {title}
            {agg_d}
            <h2>Image</h2>
            <img src="data:image/png;base64,{img_base64}">
            <h2>Dataframe</h2>
            {df_lines}
            '''

        with open(out_fp, 'w') as file:
            file.write(email_contents)

    # winds all text in df into a string, applies punctuation and unwinds back into df 
    def wind_punctuate_unwind(self,subs_df=None,mutate=True,new_colname='txt',txt_colname='txt'):
        if subs_df is None:
            subs_df=self.subs_df
        if subs_df is None:
            subs_df=self.subs_df
        if not mutate:
            tmp_df=subs_df.copy()
        else:
            tmp_df=subs_df
        tmp_df['len']=tmp_df[txt_colname].apply(lambda x: len(x.split()))
        concatenated_string = ' '.join(tmp_df[txt_colname].tolist())
        punctuated_string=self.rp.punctuate(concatenated_string)
        split_string = punctuated_string.split()
        prev_len=0
        if new_colname not in tmp_df.columns:
            tmp_df[new_colname]=''
        for no,row in tmp_df.iterrows():
            row_dic=row.to_dict()
            next_len=prev_len + row_dic['len']
            row_dic[new_colname]=' '.join(split_string[prev_len:next_len])
            tmp_df.loc[no]=row_dic
            prev_len=next_len
        tmp_df.pop('len')
        return tmp_df

if __name__=='__main__':
    
    an=Analyzer()
    subs_fp=an.utils.path_join(an.tmp_dir,'subs_df.csv')
    an.subs_df=an.utils.read_csv(subs_fp)
    an.subs_df=an.subs_df[:5]
    print(an.subs_df)
    df=an.wind_unwind()
    print(df)
#    exit(1)
    
