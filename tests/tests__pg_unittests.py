
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
    
def test__match_select_list(s='select foo,bark, kez from mytable;'):
    pg=mypg()
    res=pg.match_select_list(s=s)
    print(res)

    
def test__select(s= None):
    pg=mypg()
    if s is None:
        s='SELECT * from channels'
    l1,l2=pg.select(s=s,to_dicts=True)
    print(l1)
    print(l2)

    
def test__get_channels():
    pg=mypg()
    t=pg.get_channels()
    print(t)

def test__scan_df():
    u=Utils()
    pg=mypg()
    fp=u.path_join('tests','subs_df.csv')
    df=u.read_df(fp=fp)
    pg.subs_df=df
    pg.scan_subs_df()
    print(pg.subs_df)
    
    
    
    


if __name__=='__main__':
#    test__match_select_list()
    
    test__get_channels()