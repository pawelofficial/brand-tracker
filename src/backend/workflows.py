if __name__!='__main__':    
    from .utils import Utils   
    from .mypg import mydb
    from .ytd import Ytd
    from .analyzer import Analyzer
else:
    from utils import Utils 
    from mypg import mydb 
    from analyzer import Analyzer
    from ytd import YTd
    


# ------- pg workflows ----------------
def clear_schema(schemaname='public'
                 ,and_mask={'table_type':'BASE TABLE','table_name':'%tdlr%'}
                 ,tables_list=['channels']) :
    """ clears provided schema based on and mask and specific tables """
    pg=mydb()
    s=pg.read_query('_list_tables_',_schemaname_=schemaname) # list tables
    df=pg.select(s=s)
    if and_mask is not None:
        for k, v in and_mask.items():
            if '%' in v:  # If value contains '%', use 'not like' condition
                df = df[df[k].str.contains(v.strip('%'))]
            if '%' not in v:  # Else, use 'equal' condition
                df = df[df[k] == v]
    
    tables_to_drop=df['table_name'].to_list()
    for t in tables_to_drop:
        s= pg.read_query('_drop_table_cascade_',_tablename_=t,_schemaname_=schemaname)
        pg.ddl(s=s)
    
    if tables_list is not None:
        for t in tables_list:
            s= pg.read_query('_drop_table_cascade_',_tablename_=t,_schemaname_=schemaname)
            pg.ddl(s=s)

    s3=pg.read_query('_list_tables_',_schemaname_='public') # list tables
    df=pg.select(s=s3)
    print(df)
    
    # creates tables in a schema 

def wf__recreate_schema(channelname='tdlr'): # channelname --> channel_id
    """ creates tables channels, channelname and channel_transcript """
    pg=mydb()

    s0=pg.read_query('_create_table_channels_') # create table channels 
    pg.create_or_replace(s=s0,cascade=True)

    s1=pg.read_query('_create_table_channelname_',_channelname_=channelname) # create table channelname 
    pg.create_or_replace(s=s1,cascade=True)
    
    s2=pg.read_query('_create_table_channel_transcript_',_channelname_=channelname) # create table transcripts 
    pg.create_or_replace(s=s2,cascade=True)
    
    s3=pg.read_query('_list_tables_',_schemaname_='public') # list tables
    df=pg.select(s=s3)
    print(df)

def wf__upload_new_channel(channelname='tdlr',url=None): 
    """ uploads new channel to channels table """
    if url is None:
        url='https://www.youtube.com/@TheDavidLinReport'
    pg=mydb()
    # insert into channels table 
    
    s=pg.read_query('_insert_into_channels_',_channelname_=channelname,_channelurl_=url)
    pg.ddl(s=s)
    
    s=pg.read_query('_select_',_tablename_='channels')
    df=pg.select(s=s)
    print(df)
    # insert into channelname table
    
def wf__upload_new_vid(channelname='tdlr', vid_title=None,yt_url=None,yt_id=None):
    yt_url=yt_url or  'https://www.youtube.com/watch?v=H2eJoZdhz_A&ab_channel=DavidLin' 
    vid_title=vid_title or  'test'
    yt_id=yt_id or 'test'

    pg=mydb()
    s=pg.read_query('_select_',_tablename_=f'{channelname}_channel')
    df=pg.select(s=s)
    print(df)

    s=pg.read_query('_insert_into_channelname_',_channelname_=channelname,
                    _channel_id_='1'          # reference to channels table 
                    ,_vid_title_=vid_title
                    ,_yt_id_=yt_id
                    ,_yt_url_=yt_url)
    pg.ddl(s=s)
    
    s=pg.read_query('_select_',_tablename_=f'{channelname}_channel')
    df=pg.select(s=s)
    print(df)

def wf__upload_new_transcript(subs_fp=None,channelname='tdlr',vid_id='1'):
    pg=mydb()
    an=Analyzer()
    if subs_fp is None:
        subs_fp=pg.utils.path_join('data','tmp','subs_df.csv')
        subs_df=pg.utils.read_csv(subs_fp)
        
    print(subs_df)

    #subs_df=an.make_keywords_column(subs_df=subs_df)
    an.apply_to_dataframe(src_col='txt',tgt_col='json',fun=an.calculate_keywords)
    subs_df=an.subs_df
    print(subs_df)
    pg.insert_subs_df_to_pg(subs_df=subs_df
                            ,channelname=channelname
                            ,vid_id=vid_id
                            )

# ------- ytd workflows ----------------

def wf__download_subs(url = None):
    """ downloads and parses subs into data tmp directory """
    if url is None:
        url='https://www.youtube.com/watch?v=T3UtaZB0UjY&ab_channel=DavidLin'
    ytd=Ytd()
    ytd.download_subs(url=url)
    ytd.parse_subs()
    ytd.concat_on_time(N=30)
    ytd.utils.dump_df(ytd.subs_df,fp=ytd.utils.path_join('data','tmp','subs_df.csv'))


def wf__make_html_report(url=None):
    if url is None:
        url='https://www.youtube.com/watch?v=T3UtaZB0UjY&ab_channel=DavidLin'
        #url='https://www.youtube.com/watch?v=ammoIiY3MZo&ab_channel=DavidLin'
        #url='https://www.youtube.com/watch?v=9_uvb_8Hd5I&ab_channel=DavidLin'
        #url='https://www.youtube.com/watch?v=ammoIiY3MZo&ab_channel=DavidLin'
        #url='https://www.youtube.com/watch?v=JPGe_VXkOHU&ab_channel=DavidLin'
        #url='https://www.youtube.com/watch?v=8idT_lYJkeU&ab_channel=GregDickerson'
        #url='https://www.youtube.com/watch?v=xlHXBSE00DM&ab_channel=DavidLin'
        #url='https://www.youtube.com/watch?v=XKP6TBcL9IA&ab_channel=CommodityCulture'
    ytd=Ytd()
    ytd.download_subs(url=url)
    ytd.parse_subs()
    ytd.concat_on_time(N=15)
    title=ytd.get_url_title(url=url)
    meta_dic={'url':url,'title':title}
    ytd.utils.dump_hdf(ytd.subs_df,fp=ytd.utils.path_join('data','tmp','subs_df.h5'),meta_dic=meta_dic)
    ytd.utils.dump_df(ytd.subs_df,fp=ytd.utils.path_join('data','tmp','subs_df.csv'))
    ytd.tmp_dir=ytd.utils.path_join('data','tmp')
    
    an=Analyzer()
    an.tmp_dir=ytd.tmp_dir
    an.subs_df,an.subs_meta=an.utils.read_hdf(hdf_fp=ytd.utils.path_join('data','tmp','subs_df.h5'))
    #an.wind_punctuate_unwind(mutate=True)
    enhanced_subs_df=an.make_ts_report_calculations()    
    ts_report_df,aggregates_dic,aggregates_dic_sentiment=an.make_ts_report(subs_df=enhanced_subs_df) 
    png_fp=an.utils.path_join(an.tmp_dir,'plot.png')   
    an.make_plot(ts_report_df=ts_report_df,subs_df=enhanced_subs_df,png_fp=png_fp)
    an.make_html_report(
            ts_report_df=ts_report_df
            ,aggregates_dic=aggregates_dic
            ,png_fp=png_fp
            ,meta_dic=meta_dic
            ,output_dir=an.tmp_dir
        )



if __name__=='__main__':
    #wf__recreate_schema()
    
    wf__make_html_report()