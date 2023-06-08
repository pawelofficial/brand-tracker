from typing import Any
import pyodbc
from utils import Utils
import os 
import psycopg2 
import psycopg2.extras as extras

from dotenv import load_dotenv
load_dotenv()
#with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
#    with conn.cursor() as cursor:
#        cursor.execute("SELECT c1 from test;")
#        row = cursor.fetchall()
#        print(row)

class mysql_server:
    def __init__(self) -> Any:
        self.utils=Utils()
        self.logger= self.utils.setup_logger(name='db_log',log_file=f'db_log.log')        
        self.constring = pyodbc.connect(
            f"DRIVER={os.environ.get('SQL_DRIVER')};"
            f"SERVER=tcp:{os.environ.get('SQL_SERVER')};"
            f"PORT={os.environ.get('SQL_PORT')};"
            f"DATABASE={os.environ.get('SQL_DB')};"
            f"UID={os.environ.get('SQL_UID')};"
            f"PWD={os.environ.get('SQL_PWD')}"
        )
        self.cursor=None
        self._create_cursor()
        
    # creates cursor object
    def _create_cursor(self):
        try:
            self.cursor=self.constring.cursor()
        except Exception as e:
            self.utils.log_variable(logger=self.logger,msg='error setting cursor',e=e)
            self.cursor=None 
            
    # checks if query works 
    def test_con(self):
        self.cursor.execute("SELECT @@VERSION;")
        row = self.cursor.fetchall()
        self.utils.log_variable(logger=self.logger,msg='connecting to sql',row=row)
        print(row)
#-------------------------------------------------------------------------------------------
class my_cosmospg:
    def __init__(self) -> None:
        self.utils=Utils()
        self.logger= self.utils.setup_logger(name='pg_log',log_file=f'pg_log.log')
        username=os.environ.get('PGSQL_UID')
        pwd=os.environ.get('PGSQL_PWD')
        port=os.environ.get('PGSQL_PORT')
        catalog=os.environ.get('PGSQL_CATALOG')
        server='c.cosmos-pgsql-dev.postgres.database.azure.com'
        self.constring=f'postgres://{username}:{pwd}@{server}:{port}/{catalog}?sslmode=require'
        self.con=psycopg2.connect(self.constring)
        self.cursor=None
        self.con=None
        self._create_con() 
        self._create_cursor()
        self.scripts=os.path.abspath('./pg_scripts.json')

    # returs cursor object 
    def _create_con(self):
        try:
            self.con=psycopg2.connect(self.constring)
        except Exception as e:
            print('error setting con object')
            self.utils.log_variable(logger=self.logger,msg='error setting con',e=e)
            self.con=None
    
    def _create_cursor(self):
        try:
            self.cursor=self.con.cursor()
        except Exception as e:
            print('error setting cursor')
            self.utils.log_variable(logger=self.logger,msg='error setting cursor',e=e)
            self.cursor=None 
    
    def test_con(self):
        self.cursor.execute("select current_timestamp;")
        row = self.cursor.fetchall()
        self.utils.log_variable(logger=self.logger,msg='connecting to pgsql',row=row)
        print(row)
        return row
    


if __name__=='__main__':
    db=mypg()
    db.test_con()
    

from utils import Utils
class mydb:
    def __init__(self) -> None:
        self.utils=Utils()
        self.logger= self.utils.setup_logger(name='pg_log',log_file=f'pg_log.log')
        self.sql_server_conn_str = (
            r'Driver={ODBC Driver 18 for SQL Server};'
            r'Server=tcp:your_server.database.windows.net,1433;'
            r'Database=your_database;'
            r'Uid=your_username;'
            r'Pwd={your_password_here};'
            r'Encrypt=yes;'
            r'TrustServerCertificate=no;'
            r'Connection Timeout=30;'
        )
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
        self.utils.log_variable(logger=self.logger,msg='connecting to SQL Server')
        conn = pyodbc.connect(self.sql_server_conn_str)
        return conn 
    
    # returs cursor object 
    def _set_curr(self,conn=None):
        self.utils.log_variable(logger=self.logger,msg='creating curr object')
        if conn is None:
            conn=self.conn
        try:
            cur = self.conn.cursor()
        except pyodbc.Error as e:
            print(f'error connecting to SQL Server \n {e}')
        return cur 

    # ... rest of your class ...

if __name__=='__main__':
    db=mydb()
    