
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from mypg import mypg
from utils import Utils
import pandas as pd 


# recreates sequence and channels table 
def test__create_or_replace_channels_table():
    pg=mypg()
    # recreate channels sequence 
    pg.ddl(s='drop sequence channels_sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_='channels_sequence')
    pg.ddl(s=s)
    # recreate channels table 
    s=pg.read_query(query_name='_create_table_channels_',_sequencename_='channels_sequence')
    pg.create_or_replace(s=s,cascade=True )
# recreates sequences, a channel table and a transcript table 
def test__create_or_replace_a_channel_tables(channel='kitco'):
    pg=mypg()
    # recreate sequence for a channel  
    pg.ddl(s=f'drop sequence {channel}_sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_=f'{channel}_sequence')
    pg.ddl(s=s)
    # recreate a channel table  (refers channels) 
    s_channel=pg.read_query(query_name='_create_table_channelname_',_channelname_=channel,_sequencename_=f'{channel}_sequence')
    pg.create_or_replace(s=s_channel,cascade=True )
    # recreate transcript sequence 
    pg.ddl(s=f'drop sequence {channel}_transcript_sequence cascade;')
    s=pg.read_query(query_name='_create_sequence_sequencename_',_sequencename_=f'{channel}_transcript_sequence')
    pg.ddl(s=s)
    # recreate transcript table  
    s_channel_transcript=pg.read_query(query_name='_create_table_channel_transcript_',_channelname_=channel,_sequencename_=f'{channel}_transcript_sequence')    
    pg.create_or_replace(s=s_channel_transcript,cascade=False )    

#TBD:  inserts dummy data into channels table 
def test__insert_into_channels():
    pg=mypg()
    print('test tbd  ')
    
# TBD inserts test df into a channel table
def test__insert_into_a_channel(channel='kitco'):
    pg=mypg()
    print('test tbd ')


# inserts dummy stuff 
def test__insert_dummy_data(channel='kitco',channel_id=1,url='dummy'):
    u=Utils()
    pg=mypg()
    # insert entry into channels 
    q=f'INSERT INTO CHANNELS(CHANNEL_ID,CHANNEL_NAME,URL) VALUES({channel_id},\'{channel}\',\'{url}\');'
    pg.ddl(q)
    # insert entry into a channel 
    url=url
    #yt_id=pg.utils.parse_yt_url(url=url)
    yt_id='TBD'
    q=f'INSERT INTO {channel}_channel( channel_id,vid_title,yt_id,yt_url ) values (1,\'test\', \'{yt_id}\',\'{url}\')'
    pg.ddl(q)
    #insert into transcript table 
    fp=u.path_join('tests','subs_df.csv')
    df=u.read_df(fp=fp)
    pg.insert_subs_df_to_pg(df=df,channel=channel,yt_id=yt_id)
    
    
    
    
    


# Use the execute_values() function to insert the data in bulk
   # execute_values(cur, query, data)

    

    
    
    
if __name__=='__main__':
    test__create_or_replace_channels_table()
    test__create_or_replace_a_channel_tables(channel='kitco')
    test__create_or_replace_a_channel_tables(channel='tdlr')
    test__create_or_replace_a_channel_tables(channel='palisades')

    test__insert_dummy_data(channel='kitco',channel_id=1,url='https://www.youtube.com/@kitco')
    test__insert_dummy_data(channel='tdlr',channel_id=2,url='https://www.youtube.com/@TheDavidLinReport')
    test__insert_dummy_data(channel='palisades',channel_id=3,url='https://www.youtube.com/@PalisadeRadio')

