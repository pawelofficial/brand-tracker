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

class mydb:
    def __init__(self) -> None:
        self.utils=Utils()
        self.logger=self.utils.setup_logger(log_name='pg.log')
        self.pg_schema={
            'db':'citus'
            ,'usr':'citus'
            ,'pwd':'!QA2ws3ed'
            ,'host':'c.cosmos-pgsql-dev.postgres.database.azure.com' #   '127.0.0.1'
            ,'port':'5432'
            ,'sslmode':'require'
        }
        self.conn = self._set_conn()
        self.cur = self._set_curr() 
        self.rows=None 
        self.channels_d={'kitco':1} # ids of channels 
        self.subs_df=None
        
        self.queries_json=self.utils.path_join('pg_scripts.json')   
        self.queries_d=json.load( open(self.queries_json,'r'))


        
    # returns conn object
    def _set_conn(self):
        self.utils.log_variable(logger=self.logger,msg='connecting to pg ')
        conn = psycopg2.connect(
            dbname=self.pg_schema['db'],
            user=self.pg_schema['usr'],
            password=self.pg_schema['pwd'],
            host=self.pg_schema['host'],
            port=self.pg_schema['port'] 
        )
        return conn 
    
    # returs cursor object 
    def _set_curr(self,conn=None):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')

        if conn is None:
            conn=self.conn
        try:
            cur = self.conn.cursor()
        except psycopg2.Error as e:
            print(f'error connecting to pg \n {e}')
        return cur 
    
    # pg doesnt have create or replace hence this wrapper for create table string 
    def create_or_replace(self,s,cascade=False):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        match = re.search(r'create\s+table\s+(\w+)\s+\(', s, re.IGNORECASE)
        match = re.search(r'create\s+table\s+(\w+)\s*\(', s, re.IGNORECASE)
        if match:
            table_name = match.group(1)
        else:
            print('couldnt parse string')
            print(s)
            return 
        if cascade:                
            self.ddl(s=f'drop table if exists {table_name} cascade;')
        else:
            print(f'recreating  table {table_name}')
            self.ddl(s=f'drop table if exists {table_name};')
        self.ddl(s=s)
        return 
    
    def ddl(self,s): # executes ddl 
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        try:
            self.cur.execute(s)
            self.conn.commit()
            print('ddl worked')
        except  Exception as er:
            self.conn.rollback()
            self.cur=self._set_curr()
            print(f'ddl didnt work. {er}')
            self.utils.log_variable(logger=self.logger,msg='ddl error',er=er)
            
        self.utils.log_variable(logger=self.logger,msg='ddl status',status=self.cur.statusmessage)
        return self.cur.statusmessage
    
    # sends select string statement and fetches nrows, all by default 
    def select(self,s,nrows : int =None,to_dicts=False, to_list=False,to_df=True ):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        self.cur.execute(s)
        if nrows is None:
            self.rows = self.cur.fetchall()
        elif isinstance(nrows,int): 
            if nrows <= 0 : 
                print('i cannot select {nrows} from the table my brother in christ ')
                return 
            self.rows=self.cur.fetchmany(nrows)
        self.utils.log_variable(logger=self.logger,msg=f'select fetched {len(self.rows)} rows')
        
        # returns list of first items 
        if to_list:
            l=[t[0] for t in self.rows]
            return l 
        
        # returns lists of dictionaries corresponding to data 
        if to_dicts: 
            colnames = [desc[0] for desc in self.cur.description]
            l1=[dict(zip(colnames, row)) for row in self.rows]
            l2 = {col: [row[i] for row in self.rows] for i, col in enumerate(colnames)}
            return l1
        
        if to_df:
            colnames = [desc[0] for desc in self.cur.description]
            l1=[dict(zip(colnames, row)) for row in self.rows]
            return pd.DataFrame(l1)
            
        
        return self.rows 
    
    def match_select_list(self,s):
        select_pattern = re.compile(r'SELECT\s+(.*?)\s+FROM', re.IGNORECASE)
        match = select_pattern.search(s)
        if match:
            column_list = match.group(1)
            return [col.strip() for col in column_list.split(',')]
        else:
            return None
        
    # pings pg 
    def ping(self):
        self.utils.log_variable(logger=self.logger, msg = ' pinging pg ')
        self.select("select current_timestamp")
        print(self.rows)
        return self.rows 

    # reads query from pg_scripts json and lets you parameterize it, ORMs are too difficult my brother in christ 
    def read_query(self,query_name, **kwargs):
        self.utils.log_variable(logger=self.logger,msg=f'reading {query_name} from json with vars: ',**kwargs)
        s=self.queries_d[query_name]
        for k,v in kwargs.items():
            if k not in s:
                print(f'not a correct parameter my brother in christ? {k}')
                print(s)
                return 
            s= s.replace(k,v)
        return s.replace(',',',\n')
        
    def insert_subs_df_to_pg(self,subs_df = None,channelname='tdlr',vid_id='1',columns_mapping=None,**kwargs):
        if subs_df is None:
            subs_df=self.subs_df
                
        self.utils.log_variable(logger=self.logger,msg='inserting df to pg', channel=channelname)
        
        tablename=f'{channelname}_transcript'  # insert into _transcript table for provided channel 

        # get channel id for the channel 
        channel_id=self.select(s=f'select channel_id from channels where channel_name=\'{channelname}\'',to_list=True) # get channel id from channels table 
        if channel_id==[]:
            self.utils.log_variable(logger=self.logger,msg='missing channel in channels table', channel=channelname)
            print('ERROR missing channel in channels table ')
            return 
        channel_id=channel_id[0]
        # get vid id for the video 

        subs_df_cols=['st','en','txt','json']
        tbl_cols=['channel_id','vid_id','st','en','txt','json']
        for k,v in kwargs.items():
            subs_df_cols.append(k)
            tbl_cols.append(v)
        
        tbl_cols=','.join(tbl_cols)
        tuples = [tuple([channel_id,vid_id] + list(r)) for r in subs_df[subs_df_cols].to_numpy()]
        query=f"INSERT INTO {tablename}({tbl_cols}) VALUES %s"           
        try:
            extras.execute_values(self.cur, query, tuples)
            self.conn.commit()
            print('bulk insert worked')
        except  Exception as er:
            self.conn.rollback()
            self.cur=self._set_curr()
            print(f'bulk insert didnt work. {er}')
            self.utils.log_variable(logger=self.logger,msg='bulk insert error',er=er)
        return 



    # returns available channels
    def get_channels(self):
        tups=self.select('SELECT channel_name,url FROM CHANNELS')
        l,d=self.select('SELECT channel_name,url FROM CHANNELS',to_dicts=True)
        return {k:v for k,v in zip(d['channel_name'],d['url'])} # {'kitco': 'https://www.youtube.com/@kitco', 'tdlr': 'https://www.youtube.com/@TheDavidLinReport', 'palisades': 'https://www.youtube.com/@PalisadeRadio'}

    # returns available keywords 
    def get_keywords(self):
        return {k:None for k in self.keywords}



if __name__=='__main__':
    #wf__recreate_schema()
    
    exit(1)
    
    fp=pg.utils.path_join('tests','subs_df.csv')
    df=pg.utils.read_df(fp=fp)
    pg.insert_subs_df_to_pg(df=df)
    exit(1)    
    cols=df.columns
    mapper={'st', 'en', 'st_flt', 'en_flt', 'dif', 'pause_flt', 'txt'}
    tbl_cols=['channel_id','vid_id','start_ms','end_ms','transcript']
    
    exit(1)
    
    pg.insert_subs_df_to_pg(df=df,tablename='kitco_transcript',mapper=mapper)