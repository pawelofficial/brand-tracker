import os 
import re 
import psycopg2
import json 
import os 
from utils import Utils
import psycopg2.extras as extras
import re 
class mydb:
    def __init__(self) -> None:
        self.utils=Utils()
        self.logger= self.utils.setup_logger(name='pg_log',log_file=f'pg_log.log')
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
        self.keywords=['bitcoin','cardano','gold','silver','apple']
        
        self.queries_json=os.path.abspath('./pg_scripts.json')
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
        self.utils.log_variable(logger=self.logger,msg='creating curr object')
        if conn is None:
            conn=self.conn
        try:
            cur = self.conn.cursor()
        except psycopg2.Error as e:
            print(f'error connecting to pg \n {e}')
        return cur 
    
    # pg doesnt have create or replace hence this wrapper for create table string 
    def create_or_replace(self,s,cascade=False):
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
        self.utils.log_variable(logger=self.logger,msg='executing ddl', s=s)
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
    def select(self,s,nrows : int =None,to_dicts=False, to_list=False ):
        self.utils.log_variable(logger=self.logger,msg='executing select statement', s=s)
        self.cur.execute(s)
        if nrows is None:  # select * 
            self.rows = self.cur.fetchall()
        elif isinstance(nrows,int): # select nrows 
            if nrows <= 0 : 
                print('i cannot select {nrows} from the table my brother in chryst ')
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
            return l1,l2
            
        
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
    def read_query(self,query_name,**kwargs):
        self.utils.log_variable(logger=self.logger,msg=f'reading {query_name} from json with vars: ',**kwargs)
        s=self.queries_d[query_name]
        for k,v in kwargs.items():
            if k not in s:
                print('not a correct parameter my brother in christ?')
                return 
            s= s.replace(k,v)
        return s.replace(',',',\n')
        
    def insert_subs_df_to_pg(self,subs_df = None,channel='kitco',yt_id='test',**kwargs):
        if subs_df is None:
            subs_df=self.subs_df
                
        self.utils.log_variable(logger=self.logger,msg='inserting df to pg', channel=channel)
        tablename=f'{channel}_transcript'  # insert into _transcript table for provided channel 

        # get channel id for the channel 
        channel_id=self.select(s=f'select channel_id from channels where channel_name=\'{channel}\'',to_list=True) # get channel id from channels table 
        if channel_id==[]:
            self.utils.log_variable(logger=self.logger,msg='missing channel in channels table', channel=channel)
            print('ERROR missing channel in channels table ')
            return 
        channel_id=channel_id[0]
        # get vid id for the video 
        vid_id=self.select(s=f'select vid_id from {channel}_channel where yt_id=\'{yt_id}\'',to_list=True) # get yt id from channels table 
        if channel_id==[]:
            self.utils.log_variable(logger=self.logger,msg=f'ERROR missing video in a {channel} table', yt_id=yt_id)
            print('ERROR missing video in a {channel} table ')
            return 
        vid_id=vid_id[0]

        subs_df_cols=['st','en','txt']
        tbl_cols=['channel_id','vid_id','st','en','txt']
        for k,v in kwargs.items():
            subs_df_cols.append(k)
            tbl_cols.append(v)
        
        tbl_cols=','.join(tbl_cols)
        tuples = [tuple([channel_id,vid_id] + list(r)) for r in self.subs_df[subs_df_cols].to_numpy()]
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

    def scan_subs_df(self,keywords=['bitcoin','cardano']):
        #keyword=keywords[0]
        matches={k:None for k in self.keywords}
        for no, row in self.subs_df.iterrows():
            for keyword in keywords:
                escaped_word = re.escape(keyword)
                pattern = r'\b' + escaped_word + r'\b'
                match = re.search(pattern, row['txt'])
                if match:
                    matched=True
                else:
                    matched=False
                matches[keyword]=matched
            self.subs_df.loc[no,'json'] = json.dumps(matches) # gotta do json dumps so psycopg worko

            
        
    # returns available channels
    def get_channels(self):
        tups=self.select('SELECT channel_name,url FROM CHANNELS')
        l,d=self.select('SELECT channel_name,url FROM CHANNELS',to_dicts=True)
        return {k:v for k,v in zip(d['channel_name'],d['url'])} # {'kitco': 'https://www.youtube.com/@kitco', 'tdlr': 'https://www.youtube.com/@TheDavidLinReport', 'palisades': 'https://www.youtube.com/@PalisadeRadio'}

    # returns available keywords 
    def get_keywords(self):
        return {k:None for k in self.keywords}


    





if __name__=='__main__':
    pg=mydb()
    pg.ping()
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