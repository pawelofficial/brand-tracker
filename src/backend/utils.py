import os
import logging
import subprocess 
import inspect 
import re 
import pandas as pd 
#logging.DEBUG (10)
#logging.INFO (20)
#logging.WARNING (30)
#logging.ERROR (40)
#logging.CRITICAL (50)

class Utils:
    def __init__(self) -> None:
        self.BASIC_FORMAT="%(levelname)s:%(name)s:%(message)s"
        self.BASIC_FORMAT="%(levelname)s:%(name)s:%(asctime)s:%(message)s"
        self.level=logging.INFO
        self.mode='w'
        self.formatter= logging.Formatter(self.BASIC_FORMAT)
        self.logs_dir='logs'
        self.cur_dir=os.path.dirname(os.path.abspath(__file__))
        self.logger=None
        self.log_fp=None    # log filepath 
        self.log_name=None  # log name
        

    def setup_logger(self,log_name='log',level=None,mode=None,formatter=None):
        if self.logger is not None:
            self.log_variable(msg=f'closing {self.log_name} recreating a new log  {log_name}')
            self.close_logger()

        level=  level or self.level 
        mode=mode or self.mode
        formatter=formatter or self.formatter
        self.log_name=log_name
        self.log_fp = self.path_join(self.logs_dir, log_name)
        handler = logging.FileHandler(self.log_fp, mode=mode, encoding="utf-8") 
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)
        self.logger.propagate = False
        self.log_variable( msg=f'setting up {log_name} at {self.log_fp} ')
        return self.logger 
        
    def log_variable(self, msg,lvl=None, **kwargs ):
        if self.logger is None:
            print('no logger')
            return 
        lvl=lvl or self.level
        s=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}'

        
        self.logger.log(self.level,s)
        s=''
        for k,v in kwargs.items():
            s+= f'\n{k} : {v}'
        self.logger.log(lvl, f'{msg} {s} '   )

    def path_join(self,*args) -> str:
        if self.logger is not None:
            self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')   
        try:
            return os.path.join(self.cur_dir, *args)
        except TypeError:
            #logging.error("Arguments must be strings.")
            raise ValueError("All arguments to path_join must be strings.") from None
            return None
        
    def close_logger(self):
        if self.logger is None:
            self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')

        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def subprocess_run(self,l,logger=None,**kwargs):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ',l=l)
        q=subprocess.run(l,capture_output=True, text=True,shell=True,**kwargs)  
        self.log_variable(msg='subprocess run',l=l,stdout=q.stdout,stderr=q.stderr,returncode=q.returncode)
        if q.returncode !=1:
            self.log_variable(msg='error in executing subprocess run',lvl=logging.ERROR)
        
        return q.stdout,q.stderr,q.returncode

    def make_dir(self,fp):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if not os.path.exists(fp):
            os.makedirs(fp)
            self.log_variable(msg=f'creating {fp} ')

    def remove_dir(self,fp):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if os.path.exists(fp):
            os.rmdir(fp)
            self.log_variable(msg=f'removed {fp} ')
    def build_url(self,id):
        prefix='https://www.youtube.com/watch?v='
        return prefix+id

    def parse_url(self,url) -> dict:
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        id_reg=r'v=([^&]+)'
        channel_reg=r'ab_channel=(.*)|(\@.*)'
        vid_reg=r'\&ab_channel.*'
        vid_reg=r'watch\?v=([aA0-zZ9]+)'
        base_reg=r'(.*com/)'    
        id=re.findall(id_reg,url)
        #print('id: ', id)
        channel=re.findall(channel_reg,url)
        #print('channel: ',channel)
        vid_url=re.findall(vid_reg,url)
        base_url=re.findall(base_reg,url)[0]
        channel_url = None 
        vid_url = None 
        if id==[]:
            id=None 
        else:
            id=id[0]
        if channel==[]:
            channel=None
        else:
            channel=max(channel[0])
        if id is not None:
            vid_url=base_url+'watch?v='+id 
        if channel is not None:
            channel_url = base_url+channel+'/videos'

        d={"id":id
           ,"channel":channel
           ,"vid_url":vid_url
           ,"channel_url":channel_url
           ,"orig_url":url }
        return d

    def df_insert_d(self,df: pd.DataFrame, d : dict,clear_d=True ):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        df.loc[len(df)]=d 
        if clear_d:
            for k,v in d.items():
                d[k]=None
                
    def dump_df(self,df,fp=None,dir_fp=None,fname=None):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if fp is None:
            fp=self.path_join(dir_fp,fname)
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        x=df.to_csv(fp,index=False)

    def parse_stdout(self,stdout):
        out=[]
        for l in stdout.splitlines():
            out.append(l.strip())
        return out
            


if __name__=='__main__':
    u=Utils() 
    u.setup_logger(log_name='test.log')
    u.log_variable(msg='test',u_logger=u.logger,mode=u.mode)
    u.close_logger