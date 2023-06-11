if __name__!='__main__':    
    from .ytd import Ytd
else:
    from ytd import Ytd 

    # clears schema based on mask and tables list 
def wf__download_subs(url = None):
    """ downloads and parses subs into data tmp directory """
    if url is None:
        url='https://www.youtube.com/watch?v=T3UtaZB0UjY&ab_channel=DavidLin'
    ytd=Ytd()
    ytd.download_subs(url=url)
    ytd.parse_subs()
    ytd.concat_on_time(N=30)
    ytd.utils.dump_df(ytd.subs_df,fp=ytd.utils.path_join('data','tmp','subs_df.csv'))

if __name__=='__main__':
    #wf__recreate_schema()
    
    wf__download_subs()