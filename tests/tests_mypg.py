
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from mypg import mypg
from utils import Utils
import pandas as pd 

def test_ddl(channel='kitco'):
    pg=mypg()
    s=pg.read_query(query_name='create_table_channels')
    s='drop table foobar;'
    pg.ddl(s=s )

def test_create_or_replace_sequences(channel='kitco'):
    pg=mypg()
    pg.ddl('drop sequence test_sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_='test_sequence')
    pg.ddl(s=s)


    # 
def test_create_or_replace_tables(channel='kitco'):
    pg=mypg()
    # channels sequence 
    pg.ddl(s='drop sequence channels_sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_='channels_sequence')
    pg.ddl(s=s)
    # channels table 
    s=pg.read_query(query_name='_create_table_channels_',_sequencename_='channels_sequence')
    pg.create_or_replace(s=s,cascade=True )
    # a channel sequence 
    pg.ddl(s=f'drop sequence {channel}_sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_=f'{channel}_sequence')
    pg.ddl(s=s)
    # a channel table -> refers channels 
    s_channel=pg.read_query(query_name='_create_table_channelname_',_channelname_=channel,_sequencename_=f'{channel}_sequence')
    pg.create_or_replace(s=s_channel,cascade=True )
    # transcript sequence -> refers channel, channels
    pg.ddl(s=f'drop sequence {channel}_transcript_sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_=f'{channel}_transcript_sequence')
    pg.ddl(s=s)
    # transcript table  
    s_channel_transcript=pg.read_query(query_name='_create_table_channel_transcript_',_channelname_=channel,_sequencename_=f'{channel}_transcript_sequence')    
    pg.create_or_replace(s=s_channel_transcript,cascade=False )    


def test_insert_into_channels(channel='kitco',channel_id=1,vid_id=1):
    u=Utils()
    fp=u.path_join('tests','subs_df.csv')
    df=u.read_df(fp=fp)
    
    d={'st_flt':[0.0,0.2],'en_flt':[1.0,2.0],'txt':['foo','bar']}
    df=pd.DataFrame(d)
    
    
    print(df)
    mapper_df_to_tbl={'st_flt':'start_ms','en_flt':'end_ms','txt':'transcript','channel_id':channel_id,'vid_id':vid_id,}

    data=[]
    for no,row in df.iterrows():
        d=row.to_dict()
        print(d) 
    
    query = "INSERT INTO channels (channel_id, vid_id, start_ms,end_ms,transcript) VALUES %s"

# Use the execute_values() function to insert the data in bulk
   # execute_values(cur, query, data)

    
    
    
    
if __name__=='__main__':
    test_insert_into_channels()
    exit(1)
    test_create_or_replace_sequences()
    test_create_or_replace_tables()
    test_insert_into_transcript()
#    test_ddl()
#    test_create_or_replace_tables(channel='kitco')
#    test_create_tables_if_not_exist(channel='kitco')
