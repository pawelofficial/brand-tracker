import backend 
from backend.pgworkflows import * 
from backend.ytdworkflows import * 
from backend.workflows import wf__make_html_report
from multiprocessing import Process, freeze_support

####### yt
###wf__download_subs() # download subs 
###
####### pg:
###clear_schema()                 # clear schema of tdlr tables 
###wf__recreate_schema()          # create tdlr tables 
###wf__upload_new_channel()       # upload test video to channels table 
###wf__upload_new_vid(yt_url='https://www.youtube.com/watch?v=H2eJoZdhz_A&ab_channel=DavidLin')            # upload test video to channelname table 
####wf__upload_new_vid(yt_url='https://www.youtube.com/watch?v=s5OllulK_F0&ab_channel=DavidLin')            # upload test video to channelname table 
###wf__upload_new_transcript(vid_id='1')
####wf__upload_new_transcript(vid_id='2')    # upload test video to channel_transcript table


#wf__make_html_report()
if __name__=='__main__':
    wf__make_html_report()
    exit(1)
    an=Analyzer()
    subs_fp=an.utils.path_join(an.tmp_dir,'subs_df.csv')
    an.subs_df=an.utils.read_csv(subs_fp)
    an.subs_df=an.subs_df
    print(an.subs_df)
    df=an.wind_punctuate_unwind()
    wind_unwind_fp=an.utils.path_join(an.tmp_dir,'wind_unwind_df.csv')
    an.utils.dump_df(df,fp=wind_unwind_fp)
# download, parse, concat subs -> upload to cosmos ->  video_subs
# make ts report on out of video_subs              ->  video_ts_report , aggregates
# make png out of video subs and video ts report   ->  video plot 
# make report per user as select from cosmos       ->  user_video_report
# send report 

