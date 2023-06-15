
import inspect 
import logging 
import chardet
import json 
import pandas as pd 
import numpy as np 
import re 

# i will never learn how to do the imports in python 
if __name__!='__main__':    
    from .utils import Utils   # import for tests 
else:
    from utils import Utils 

class Ytd:
    def __init__(self) -> None:
        # objects 
        self.utils = Utils()
        self.logger=self.utils.setup_logger(log_name='ytd.log')
        
        # settings
        self.tmp_dir=self.utils.path_join(self.utils.cur_dir,'data','tmp')  # used by download_subs,parse_subs
        self.subs_lang='en'                                                 # used by download_subs                                  
        self.subs_format='json3'                                            # used by download_subs
        
        # results
        self.vid_title=None                                                 # set by get_url_title  |
        self.raw_fp=None                                                    # set by download_subs  | used by parse_subs
        self.subs_fp=None                                                   # set by parse_subs     |
        self.subs_df=None                                                   # set by parse_subs     |
        
    # gets url title 
    def get_url_title(self,url):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        vid_url=self.utils.parse_url(url)['vid_url'] 
        l=["yt-dlp","--skip-download",vid_url,"--get-title"]
        stdout, stderr,returncode =self.utils.subprocess_run(l) 
        title=stdout.replace(' ','_').replace('|','').strip() 
        title=''.join([c for c in title if c.isalnum() or c in ('_') ])
        self.vid_title=title
        return title 
    
    # checks if lang is available 
    def check_available_langs(self,url):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')   
        vid_url=self.utils.parse_url(url)['vid_url']
        l=["yt-dlp","--skip-download",vid_url,"--list-subs"]    
        stdout, stderr,returncode =self.utils.subprocess_run(l) 
        langs_d={}
        isavailable = False 
        for line in stdout.splitlines():
            if 'json3' not in line: # skip lines that do not specify language 
                continue
            line=[i.strip() for i in line.split(' ') if i!='']
            ytlang=line[0]
            lang_long=line[1] # not used 
            formats_available=line[1:]
            langs_d[ytlang]=[formats_available]
        isavailable=any([self.subs_lang == k for k in langs_d.keys()]) # check if lang is available
        return isavailable, langs_d
    
    # downloads subs 
    def download_subs(self,url,out_dir=None):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')   
        vid_url=self.utils.parse_url(url)['vid_url'] 
        if out_dir is None:
            out_dir=self.tmp_dir
        if self.vid_title is None:
            fname=f'raw_subs_' 
        else:
            fname=f'raw_subs_{self.vid_title}_'
        self.raw_fp=self.utils.path_join(out_dir,fname)
#        self.raw_fp=self.utils.path_join(self.tmp_dir,fname)+f'.{self.subs_lang}.{self.subs_format}'
        l=["yt-dlp","-o", f"{self.raw_fp}","--skip-download"]
        l+=[vid_url,"--force-overwrites",
            "--no-write-subs",  
            "--write-auto-sub",
            "--sub-format",self.subs_format,
            "--sub-langs",self.subs_lang] # en.* might be better here 
        stdout, stderr,returncode  =self.utils.subprocess_run(l) 
        self.raw_fp=self.utils.path_join(out_dir,fname)+f'.{self.subs_lang}.{self.subs_format}'
        return self.raw_fp
        
    def parse_subs(self,dump_df=True,fname='subs_df',output_dir_fp=None):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if self.raw_fp is None:
            self.utils.log_variable(lvl=logging.ERROR, msg='raw_fp is None cant parse subs')
            return None
        cols=['no','st','en','st_flt','en_flt','dif','pause_flt','txt']
        subs_d={k:None for k in cols}  
        
        with open(self.raw_fp,'rb') as f:                       # getting encoding 
            encoding=chardet.detect(f.read())['encoding']
            
        with open(self.raw_fp,'r',encoding=encoding) as f:     # read data to list 
            pld=json.load(f)['events']                  
        
        pld=[i for i in pld if 'segs' in i.keys()]      # remove items without text 
        tmp_df=pd.DataFrame(columns=subs_d.keys())      # declare temporary df 
        
        for no,p in enumerate(pld):                     # insert data to temporary df 
            subs_d=self._parse_json_pld(p=p,no=no)
            txt=subs_d['txt'].strip()
            if txt not in ['']:                         # don't write empty rows 
                self.utils.df_insert_d(df=tmp_df,d=subs_d)
        tmp_df['dif']=np.round(tmp_df['en_flt']-tmp_df['st_flt'],2 ) # calculate dif col 
        self.subs_df=tmp_df
        if dump_df:
            fname=fname.replace('.csv','')+'.csv'
            output_dir_fp=output_dir_fp or self.tmp_dir
            self.utils.dump_df(df=self.subs_df,dir_fp=output_dir_fp,fname=fname)
            self.subs_fp=self.utils.path_join(output_dir_fp,fname)
        self.subs_df=tmp_df    
        return self.subs_df,self.subs_fp
        
        # concats df on time 
    def concat_on_time(self, subs_df=None, N=60):
        # Determine whether the input dataframe was provided or not
        external = False if subs_df is None else True
        subs_df = self.subs_df if subs_df is None else subs_df

        # Define the function that will be applied to 'txt' column
        def replace_double_spaces(s):
            return s.replace('  ', ' ')

        # Apply the function to 'txt' column
        for no, row in subs_df.iterrows():
            subs_df.loc[no, 'txt'] = replace_double_spaces(row['txt'])

        # Define the condition for '_concat_on_condition' method
        cond = lambda prev_row, cur_row:  cur_row['st_flt'] // N == prev_row['st_flt'] // N

        # Define the function for '_concat_on_condition' method
        def concatenate_rows(prev_row, cur_row):
            prev_row['txt'] += ' ' + cur_row['txt']
            prev_row['en_flt'] = cur_row['en_flt']
            prev_row['en'] = cur_row['en']
            return prev_row, cur_row, True

        # Apply '_concat_on_condition' method
        subs_df = self._concat_on_condition(subs_df=subs_df, cond=cond, func=concatenate_rows)

        # Calculate 'dif' column
        subs_df['dif'] = np.round(subs_df['en_flt'] - subs_df['st_flt'], 2 )

        # Update self.subs_df if the input dataframe was not provided
        if not external:
            self.subs_df = subs_df

        return subs_df


    def _concat_on_condition(self,subs_df,cond = None,func=None ):
        df=subs_df.copy(deep=True)
        no=1                            
        df['index']=df.index
        while no<len(df):
            #self._calculate_pause_to_next(df=df)
            df['dif']=np.round(df['en_flt']-df['st_flt'],2 ) # calculate dif col 
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            c=cond(prev_row,cur_row)
            if not c:
                no+=1
            else:
                prev_row,cur_row,bl = func(prev_row,cur_row)
                df.loc[prev_row['index']]=prev_row
                df.loc[cur_row['index']]=cur_row
                if bl:
                    df.drop(cur_row['index'],inplace=True)
                    no-=1
                no+=1
        df.drop('index',axis=1,inplace=True)
        return df
        
    def _clean_txt(self,s : str,**kwargs): # cleans up string 
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        
        custom_d={k:v for k,v in kwargs.items()}
        translation_table = str.maketrans({'\xa0': ' ', '\n': ' ', '\t': ' ', '\r': ' ','\u200b':''})
        translation_table.update(custom_d)
        translation_table[ord("\n")] = " "
        clean_string = s.translate(translation_table)
        return clean_string.strip().replace('  ',' ')
        
    def _parse_json_pld(self,p,no):
        subs_d={}
        subs_d['no']=no
        subs_d['st_flt']=np.round(int(p['tStartMs'])/1000.0,2)
        if 'dDurationMs' not in p.keys():       # some rows don't have this key 
            subs_d['en_flt']=subs_d['st_flt']+0 # so much math 
        else:
            subs_d['en_flt']=np.round(subs_d['st_flt']+int(p['dDurationMs'])/1000.0,2)
            
        subs_d['st']=self._flt_to_ts(ff=subs_d['st_flt'])
        subs_d['en']=self._flt_to_ts(ff=subs_d['en_flt'])
        txt=' '.join([d['utf8'] for d in p['segs'] if d['utf8']!='\n']  ).replace('  ',' ').strip()
        
        rs=[r'\[.*\]',r"^,|,$",r"^\[\w+",r"[aA-zZ]*\]"] # clean up stuff from yt 
        for r in rs:
            txt=re.sub(r,'',txt).replace('[','').replace(']','') # 
        subs_d['txt']=self._clean_txt(txt)
        return subs_d    
    
    def _flt_to_ts(self,ff : float): # float to timestamp string
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if ff != ff: # float is nan:
            ff=0
        hh=ff/60/60//1
        mm=(ff-hh*60*60)/60//1
        ss=(ff-hh*60*60-mm*60)//1
        fff=(ff-hh*60*60-mm*60-ss)*1000
        return '{:02d}:{:02d}:{:02d}.{:03d}'.format(int(hh), int(mm), int(ss),int(fff))

    # tessted up to n = 100 
    def scan_channel(self,url,n=10):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        vid_url=self.utils.parse_url(url)['channel_url']   
        l=["yt-dlp","--get-id","--skip-download",vid_url,"--playlist-end", f"{n}"]
        stdout, stderr,returncode =self.utils.subprocess_run(l)
        ids=self.utils.parse_stdout(stdout=stdout)
        urls=[self.utils.build_url(id) for id in ids]
        ds=[self.utils.parse_url(url) for url in urls]
        return ds,urls
    
    ###def scan_channel_scrape(self,url,n=10): # needs this wierd id of a channel 
    ###    d=self.utils.parse_url(url)
    ###    videos = scrapetube.get_channel("KitcoNEWS")
    ###    for video in videos:
    ###        print(video['videoId'])
        
        
def wf__download_subs(url = None):
    """ downloads and parses subs into data tmp directory """
    if url is None:
        url='https://www.youtube.com/watch?v=T3UtaZB0UjY&ab_channel=DavidLin'
    ytd=Ytd()
    ytd.download_subs(url=url)
    ytd.parse_subs()
        
        
if __name__=='__main__':
    wf__download_subs()
