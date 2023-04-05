import os 
import psycopg2
import json 
import os 
from utils import Utils

class mypg:
    def __init__(self) -> None:
        self.utils=Utils()
        self.logger= self.utils.setup_logger(name='pg_log',log_file=f'pg_log.log')
        self.conn = self._set_conn()
        self.cur = self._set_curr() 
        self.rows=None 
        
        
        
        self.queries_json=os.path.abspath('./pg_srcripts.json')
        self.queries_d=json.load( open(self.queries_json,'r'))
        
    # returns conn object
    
    def _set_conn(self,dbname='dev',user='postgres',pwd='admin',host='127.0.0.1',port='5432'):
        self.utils.log_variable(logger=self.logger,msg='connecting to pg ')
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=pwd,
            host=host,
            port=port 
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
    
    # sends select string statement and fetches nrows, all by default 
    def select(self,s,nrows : int =None ):
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
        
            
        return self.rows 

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
        return s
        
    def insert_subs_df_to_pg(self,df,tablename):
        self.utils.log_variable(logger=self.logger,msg='inserting df to pg', tablename=tablename)
        pass


if __name__=='__main__':
    
    pg=mypg()
    x=pg.read_query(query_name='_create_table_channelname_',_channelname_='foo')
    print(x)
