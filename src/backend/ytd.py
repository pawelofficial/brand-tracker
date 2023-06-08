from utils import Utils
import inspect 
import logging 
import chardet
import json 
import pandas as pd 
import numpy as np 
import re 

class ytd:
    def __init__(self) -> None:
        # objects 
        self.utils = Utils()
        self.logger=self.utils.setup_logger(log_name='ytd.log')
        
        # settings
        self.tmp_dir=self.utils.path_join(self.utils.cur_dir,'data','tmp')  # used by download_subs
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
    def download_subs(self,url):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')   
        vid_url=self.utils.parse_url(url)['vid_url'] 
        if self.vid_title is None:
            fname=f'raw_subs_' 
        else:
            fname=f'raw_subs_{self.vid_title}_'
        self.raw_fp=self.utils.path_join(self.tmp_dir,fname)+f'.{self.subs_lang}.{self.subs_format}'
        l=["yt-dlp","-o", f"{self.raw_fp}","--skip-download"]
        l+=[vid_url,"--force-overwrites",
            "--no-write-subs",  
            "--write-auto-sub",
            "--sub-format",self.subs_format,
            "--sub-langs",self.subs_lang] # en.* might be better here 
        stdout, stderr,returncode  =self.utils.subprocess_run(l) 
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
        
        
    def _parse_json_pld(self,p,no):
        subs_d={}
        subs_d['no']=no
        subs_d['st_flt']=np.round(int(p['tStartMs'])/1000.0,2)
        if 'dDurationMs' not in p.keys():       # some rows don't have this key 
            subs_d['en_flt']=subs_d['st_flt']+0 # so much math 
        else:
            subs_d['en_flt']=np.round(subs_d['st_flt']+int(p['dDurationMs'])/1000.0,2)
            
        subs_d['st']=self.utils.flt_to_ts(ff=subs_d['st_flt'])
        subs_d['en']=self.utils.flt_to_ts(ff=subs_d['en_flt'])
        txt=' '.join([d['utf8'] for d in p['segs'] if d['utf8']!='\n']  ).replace('  ',' ').strip()
        
        rs=[r'\[.*\]',r"^,|,$",r"^\[\w+",r"[aA-zZ]*\]"] # clean up stuff from yt 
        for r in rs:
            txt=re.sub(r,'',txt).replace('[','').replace(']','') # 
        subs_d['txt']=self.utils.clean_txt(txt)
        return subs_d    
    
        
if __name__=='__main__':
    ytd=ytd()


    url='https://www.youtube.com/watch?v=L_spEO5IpcQ&ab_channel=KitcoNEWS'
    ytd.get_url_title(url=url)
    ytd.download_subs(url=url)
    ytd.parse_subs()