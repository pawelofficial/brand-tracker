import backend 
from backend.pgworkflows import * 
from backend.ytdworkflows import * 
from backend.workflows import wf__make_report


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


wf__make_report()


