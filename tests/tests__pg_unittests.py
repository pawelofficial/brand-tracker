
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from mypg import mypg
from utils import Utils
import pandas as pd 

def test__ddl(channel='kitco'):
    pg=mypg()
    s=pg.read_query(query_name='create_table_channels')
    s='drop table foobar;'
    pg.ddl(s=s )
    
def test__select():
    pg=mypg()
    s='SELECT channel_id from channels'
    x=pg.select(s=s)
    x2=pg.select(s=s,to_list=True)
    print(x)
    print(x2)
    
def test__get_channels():
    pg=mypg()
    t=pg.get_channels()
    print(t)

    
    

def test__create_or_replace_sequences(channel='kitco'):
    pg=mypg()
    pg.ddl('drop sequence test__sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_='test__sequence')
    pg.ddl(s=s)
    
if __name__=='__main__':
    test__get_channels()
    exit(1)
    test__select()