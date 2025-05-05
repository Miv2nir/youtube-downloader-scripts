import yt_dlp
import os
import copy
import time
import requests
import toml 
import json
import shutil
from datetime import datetime
from pytz import timezone
from math import inf
import random


#params
move_to_share=True
force_keyframes=False
download_sponsor_free_video=True
cut_selfpromo_from_sponsor_free_video=True
handle_crashes=True
log_url=False
rate_limiter=False

if os.name=='nt': #home machine, windows
    dump_path="A:/Unsorted/"
    dump_path_2="A:/Sorted/Videos/YouTube and Twitch Channel Downloads/"
else: #unix
    if 'com.termux' in os.getcwd(): #running from termux
        dump_path='/data/data/com.termux/files/home/archive_mount/archive/Unsorted/'
        dump_path_2='/data/data/com.termux/files/home/archive_mount/archive/Sorted/Videos/YouTube and Twitch Channel Downloads/'
    else: #assuming regular linux
        dump_path='/home/miv2nir/archive_mount/archive/Unsorted/'
        dump_path_2='/home/miv2nir/archive_mount/archive/Sorted/Videos/YouTube and Twitch Channel Downloads/'


channel_url=input("Enter channel URL: ")

#form a list of videos to download
opts_list={'cookiefile': 'cookies.txt',
           'dump_single_json': True,
 'extract_flat': 'in_playlist',
 'fragment_retries': inf,
 'noprogress': True,
 'postprocessors': [{'key': 'FFmpegConcat',
                     'only_multi_video': True,
                     'when': 'playlist'}],
 'quiet': True,
 'retries': inf,
 'simulate': True}

print('Retrieving metadata...')
channel_info_json=yt_dlp.YoutubeDL(opts_list).extract_info(channel_url)
print('channel_info_json obtained.')

def random_wait(x,distance=25):
    if rate_limiter:
        t=random.randint(x,x+distance)
        print('Waiting',t,'seconds...')
        time.sleep(t)
    else:
        print('rate_limiter flag off, not waiting...')
    return True

#import json
#with open('result.json', 'w',encoding="utf-8") as fp:
#    json.dump(channel_info_json, fp)

urls=[]
try:    
    for i in channel_info_json["entries"]:
        #print(i)
        urls.append(i['url'])
except KeyError:
    print('Channel too large, attempting another pulling method')
    urls=[]
    for i in channel_info_json["entries"]:
        for j in i['entries']:
            #print(j['url'])
            urls.append(j['url'])

#print(urls)
if rate_limiter:
    random_wait(30)

print('Scan for already downloaded videos...',end=' ')

already_downloaded_urls=[]
no_directory=False
try:
    dirs=os.listdir(dump_path+channel_info_json['channel']+'/')
    print('OK')
except:
    print('Target directory not found, continuing on')
    no_directory=True
if not no_directory:
    for i in dirs:
        with open(dump_path+channel_info_json['channel']+'/'+i+'/info.toml','r',encoding="utf-8") as f:
            d=toml.loads(f.read())
            already_downloaded_urls.append(d['video_link'])
    
print(already_downloaded_urls)
#scan sorted folder
print('Scanning the Sorted folder...',end='')
no_directory=False
try:
    dirs_new=os.listdir(dump_path_2+channel_info_json['channel']+'/')
    print('OK')
except:
    print('Target directory not found, continuing on')
    no_directory=True
if not no_directory:
    for i in dirs_new:
        dirs_2=os.listdir(dump_path_2+channel_info_json['channel']+'/'+i+'/')
        for j in dirs_2:
            with open(dump_path_2+channel_info_json['channel']+'/'+i+'/'+j+'/info.toml','r',encoding="utf-8") as f:
                d=toml.loads(f.read())
                already_downloaded_urls.append(d['video_link'])
print(already_downloaded_urls)
    


print("Iterating through the code from download_video.py")


# urls=['https://www.youtube.com/watch?v=qQL9lA2meYc']

print('Waiting before downloading...',end=' ')
random_wait(7)
print('OK')

for url in urls: #download_video.py
    if url in already_downloaded_urls:
        print(url,'has already been downloaded, skipping...')
        continue
    
    is_patreon_exclusive=False
    patreon_post_link=""
    
    def is_short(url):
        return ('short' in url)

    print("Currently processing "+url+'... ')
    try:
        final_filename = None

        def yt_dlp_monitor(d):
            global final_filename
            final_filename  = d.get('info_dict').get('_filename')

        opts={'cookiefile': 'cookies.txt',
            'compat_opts': {'filename-sanitization'},
        'extract_flat': 'discard_in_playlist',
        'final_ext': 'mp4',
        'format_sort': ['res:1440', 'ext:mp4:m4a'],
        'fragment_retries': inf,
        #'ignoreerrors': 'only_download',
        'postprocessors': [{'format': 'jpg',
                            'key': 'FFmpegThumbnailsConvertor',
                            'when': 'before_dl'},
                            #{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                            {'key': 'FFmpegVideoRemuxer',      
                            'preferedformat': 'aac>m4a/mp4'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'},{'api': 'https://sponsor.ajay.app',
                            'categories': {'chapter',
                                            'filler',
                                            'interaction',
                                            'intro',
                                            'music_offtopic',
                                            'outro',
                                            'poi_highlight',
                                            'preview',
                                            'selfpromo',
                                            'sponsor'},
                            'key': 'SponsorBlock',
                            'when': 'after_filter'},
                            {'force_keyframes': False,
                            'key': 'ModifyChapters',
                            'remove_chapters_patterns': [],
                            'remove_ranges': [],
                            'remove_sponsor_segments': set(),
                            'sponsorblock_chapter_title': '[SponsorBlock]: '
                                                        '%(category_names)l'},
                            {'add_chapters': True,
                            'add_infojson': None,
                            'add_metadata': False,
                            'key': 'FFmpegMetadata'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}],
        'overwrites': False,
        'retries': inf,
        'writesubtitles': True,
        'writedescription': True,
        'writethumbnail': True,
        'outtmpl': {'default': '%(title)s.%(ext)s', 'thumbnail': 'thumbnail.%(ext)s','description':'description.txt'},
        "progress_hooks":[yt_dlp_monitor]}

        opts_metadata=copy.deepcopy(opts)
        opts_metadata['skip_download']=True
        opts_metadata['writesubtitles']=False
        opts_metadata['writedescription']=False
        opts_metadata['writethumbnail']=False
        opts_metadata['postprocessors']=[{'format': 'jpg',
                            'key': 'FFmpegThumbnailsConvertor',
                            'when': 'before_dl'},
                            #{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                            {'key': 'FFmpegVideoRemuxer','preferedformat': 'aac>m4a/mp4'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'},{'api': 'https://sponsor.ajay.app',
                            'categories': {'sponsor'},
                            'key': 'SponsorBlock',
                            'when': 'after_filter'},
                            {'force_keyframes': False,
                            'key': 'ModifyChapters',
                            'remove_chapters_patterns': [],
                            'remove_ranges': [],
                            'remove_sponsor_segments': set(),
                            'sponsorblock_chapter_title': '[SponsorBlock]: '
                                                        '%(category_names)l'},
                            {'add_chapters': False,
                            'add_infojson': None,
                            'add_metadata': False,
                            'key': 'FFmpegMetadata'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}]

        #get only the metadata at first
        print('Retrieving sponsor info...')
        info_json=yt_dlp.YoutubeDL(opts_metadata).extract_info(url)
        print('info_json obtained.')
        if rate_limiter:
            random_wait(27)
            
        sponsor_present=(info_json["sponsorblock_chapters"]!=[])

        print('Retrieving selfpromo info...')
        opts_metadata['postprocessors']=[{'format': 'jpg',
                        'key': 'FFmpegThumbnailsConvertor',
                        'when': 'before_dl'},
                        #{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                        {'key': 'FFmpegVideoRemuxer','preferedformat': 'aac>m4a/mp4'},
                        {'key': 'FFmpegConcat',
                        'only_multi_video': True,
                        'when': 'playlist'},{'api': 'https://sponsor.ajay.app',
                            'categories': {'selfpromo'},
                            'key': 'SponsorBlock',
                            'when': 'after_filter'},
                        {'force_keyframes': False,
                            'key': 'ModifyChapters',
                            'remove_chapters_patterns': [],
                            'remove_ranges': [],
                            'remove_sponsor_segments': set(),
                            'sponsorblock_chapter_title': '[SponsorBlock]: '
                                                        '%(category_names)l'},
                        {'add_chapters': False,
                            'add_infojson': None,
                            'add_metadata': False,
                            'key': 'FFmpegMetadata'},
                        {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}]
        info_json=yt_dlp.YoutubeDL(opts_metadata).extract_info(url)
        print('info_json obtained.')
        if rate_limiter:
            random_wait(21)

        selfpromo_present=(info_json["sponsorblock_chapters"]!=[])

        print('Retrieving metadata...')
        opts_metadata['postprocessors']=[{'format': 'jpg',
                        'key': 'FFmpegThumbnailsConvertor',
                        'when': 'before_dl'},
                        #{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                        {'key': 'FFmpegVideoRemuxer','preferedformat': 'aac>m4a/mp4'},
                        {'key': 'FFmpegConcat',
                        'only_multi_video': True,
                        'when': 'playlist'},{'api': 'https://sponsor.ajay.app',
                            'categories': {'selfpromo','sponsor'},
                            'key': 'SponsorBlock',
                            'when': 'after_filter'},
                        {'force_keyframes': False,
                            'key': 'ModifyChapters',
                            'remove_chapters_patterns': [],
                            'remove_ranges': [],
                            'remove_sponsor_segments': set(),
                            'sponsorblock_chapter_title': '[SponsorBlock]: '
                                                        '%(category_names)l'},
                        {'add_chapters': False,
                            'add_infojson': None,
                            'add_metadata': False,
                            'key': 'FFmpegMetadata'},
                        {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}]

        info_json=yt_dlp.YoutubeDL(opts_metadata).extract_info(url)
        print('info_json obtained.')
            
        with open('result.json', 'w',encoding="utf-8") as fp:
            json.dump(info_json, fp)
            
        #exit()


        #exit()

        #get relevant video information
        title=info_json['title']
        like_count=info_json['like_count']
        date=info_json['upload_date'][:4]+'.'+info_json['upload_date'][4:6]+'.'+info_json['upload_date'][6:]
        print(date)
        #get dislikes
        print('Retrieving dislikes...',end=' ')
        def get_dislikes(video_id):
            url="https://returnyoutubedislikeapi.com/votes?videoId="+video_id
            try:
                # Make a GET request to the API endpoint using requests.get()
                response = requests.get(url)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    posts = response.json()
                    return posts
                else:
                    print('Error:', response.status_code)
                    return None
            except requests.exceptions.RequestException as e:

                # Handle any network-related errors or exceptions
                print('Error:', e)
                return None

        dislikes_info=get_dislikes(info_json['id'])
        dislikes_number=dislikes_info['dislikes']
        print('OK')
        #compose a directory
        print('Creating a new directory...',end=' ')
        if is_short(url):
            dir_name=date+' SHORT '+title
        else:
            dir_name=date+' '+title
        for i in dir_name:
            if i in "<>:\"/\\|?*":
                dir_name=dir_name.replace(i,'')
        while dir_name[-1]=='.':
            dir_name=dir_name[:-1]
        os.makedirs(dir_name,exist_ok=True)
        print('OK')

        #move into the new directory and perform all the necessary work there
        print('Moving into a new directory...',end=' ')
        os.chdir(dir_name)
        print('OK')

        #downloading the video
        if rate_limiter:
            random_wait(42)
        opts['cookiefile']="../cookies.txt"
        if (sponsor_present or selfpromo_present) and download_sponsor_free_video:
            print('Downloading sponsor-free video...')
            opts_sponsor=copy.deepcopy(opts)
            if force_keyframes:
                opts_sponsor['force_keyframes_at_cuts']=True
                opts_sponsor['fragment_retries']=inf
            if cut_selfpromo_from_sponsor_free_video:
                opts_sponsor['postprocessors']=[{'format': 'jpg',
                            'key': 'FFmpegThumbnailsConvertor',
                            'when': 'before_dl'},
                            #{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                            {'key': 'FFmpegVideoRemuxer','preferedformat': 'aac>m4a/mp4'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'},{'api': 'https://sponsor.ajay.app',
                            'categories': {'chapter',
                                            'filler',
                                            'interaction',
                                            'intro',
                                            'music_offtopic',
                                            'outro',
                                            'poi_highlight',
                                            'preview',
                                            'selfpromo',
                                            'sponsor'},
                            'key': 'SponsorBlock',
                            'when': 'after_filter'},
                            {'force_keyframes': force_keyframes,
                            'key': 'ModifyChapters',
                            'remove_chapters_patterns': [],
                            'remove_ranges': [],
                            'remove_sponsor_segments': {'selfpromo','sponsor'},
                            'sponsorblock_chapter_title': '[SponsorBlock]: '
                                                        '%(category_names)l'},
                            {'add_chapters': True,
                            'add_infojson': None,
                            'add_metadata': False,
                            'key': 'FFmpegMetadata'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}]
            else:
                opts_sponsor['postprocessors']=[{'format': 'jpg',
                            'key': 'FFmpegThumbnailsConvertor',
                            'when': 'before_dl'},
                            #{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                            {'key': 'FFmpegVideoRemuxer','preferedformat': 'aac>m4a/mp4'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'},{'api': 'https://sponsor.ajay.app',
                            'categories': {'chapter',
                                            'filler',
                                            'interaction',
                                            'intro',
                                            'music_offtopic',
                                            'outro',
                                            'poi_highlight',
                                            'preview',
                                            'selfpromo',
                                            'sponsor'},
                            'key': 'SponsorBlock',
                            'when': 'after_filter'},
                            {'force_keyframes': force_keyframes,
                            'key': 'ModifyChapters',
                            'remove_chapters_patterns': [],
                            'remove_ranges': [],
                            'remove_sponsor_segments': {'sponsor'},
                            'sponsorblock_chapter_title': '[SponsorBlock]: '
                                                        '%(category_names)l'},
                            {'add_chapters': True,
                            'add_infojson': None,
                            'add_metadata': False,
                            'key': 'FFmpegMetadata'},
                            {'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}]
            with yt_dlp.YoutubeDL(opts_sponsor) as ydl:
                ydl.download(url)
            print('Download done.')
            if rate_limiter:
                random_wait(30)
        #if sponsor_present and download_sponsor_free_video:
        if sponsor_present or selfpromo_present:
            print('Downloading full video...')
            opts['outtmpl']['default']="[Untrimmed] %(title)s.%(ext)s"
            
        else:
            print('Downloading the video...')
        with yt_dlp.YoutubeDL(opts) as ydl:
            if rate_limiter:
                random_wait(29)
            cwd=os.getcwd()
            ydl.download(url)
        print('Download done.')
        #verify and remove excess thumbnail files
        print('Check for and clear out an excess thumbnail file...',end=' ')
        cwd_list= os.listdir(os.getcwd())
        for i in cwd_list:
            if '.jpg' in i and i!='thumbnail.jpg':
                os.remove(i)
        print('OK')

        #generate playlists
        print('Generating playlists...',end=' ')

        def handle_special_characters(s):
            rfc3986={
                ' ':'%20',
                '!':'%21',
                '#':'%23',
                '$':'%24',
                '&':'%26',
                "'":'%27',
                '(':'%28',
                ')':'%29',
                '*':'%2A',
                '+':'%2B',
                ',':'%2C',
                '/':'%2'+'F',
                ':':'%3A',
                ';':'%3B',
                '=':'%3D',
                '?':'%3'+'F',
                '@':'%40',
                '[':'%5B',
                ']':'%5D'
            }
            new_s=''
            for i in s:
                if i in rfc3986.keys():
                    new_s+=rfc3986[i]
                else:
                    new_s+=i
            return new_s

        def make_playlist(categories,filename,video_name):
            durations=[]
            last_end=0
            for i in info_json['sponsorblock_chapters']:
                if i['category'] in categories:
                    if i['start_time']!=0 and not(last_end>=i['start_time']):
                        durations.append((last_end,i['start_time']))
                    last_end=max(last_end,i['end_time'])
            if not durations: #empty case
                return False
            else:
                with open(filename,'w',encoding="utf-8") as f:
                    f.write('#EXTM3U\n')
                    for i in durations:
                        f.write('#EXTINF:3310,'+video_name+'\n')
                        f.write('#EXTVLCOPT:start-time='+str(i[0])+'\n')
                        f.write('#EXTVLCOPT:stop-time='+str(i[1])+'\n')
                        f.write(handle_special_characters(video_name)+'\n')
                    #last segment
                    f.write('#EXTINF:3310,'+video_name+'\n')
                    f.write('#EXTVLCOPT:start-time='+str(last_end)+'\n')
                    f.write(handle_special_characters(video_name)+'\n')
                return True
        #playlist_name will only be properly created if final_filename's last 4 characters are the extension name (aka .mp4 or .mkv)
        playlist_name=final_filename[:-4]+'.m3u'
        if playlist_name[:11]=='[Untrimmed]':
            playlist_name=playlist_name[12:]
        if sponsor_present:
            make_playlist(('sponsor'),'[No Sponsor] '+playlist_name,final_filename)
        if selfpromo_present and not sponsor_present:
            make_playlist(('selfpromo','sponsor'),'[No Self Promotion] '+playlist_name,final_filename)
        if selfpromo_present and sponsor_present:
            make_playlist(('selfpromo','sponsor'),'[No Sponsor Nor Self Promotion] '+playlist_name,final_filename)




                    
            

        #for whatever reason yt-dlp disobeys custom extensions setting so the .description one must be renamed
        print('Renaming the description file...',end=' ')
        os.rename('description.txt.description','description.txt')
        print('OK')

        #get today's time
        print('Checking the clock...',end=' ')

        date_of_visit=datetime.now(timezone('Europe/Moscow')).strftime('%Y.%m.%d')
        print('OK')

        #write metadata into toml file
        #current info.toml version is 0.1 (last revision on 2025.01.29)

        print('Creating info.toml...',end=' ')
        info_dict_head={
            'info_ver':0.1,
            'video_link':url,
        }
        info_dict_details={
            'video_title':title,
            'views':info_json['view_count'],
            'likes': like_count if like_count else 0,
            'dislikes':dislikes_number,
            'date_of_upload':str(date),
            #'sponsor_present':sponsor_present,
            #'force_keyframes':force_keyframes
        }
        info_dict_visit={
            'date_of_visit':date_of_visit
        }
        if is_patreon_exclusive:
            info_dict_patreon={
                'is_patreon_exclusive':is_patreon_exclusive,
                'patreon-post-link':patreon_post_link
            }
        else:
            info_dict_patreon={}
        info_dicts=[info_dict_head,info_dict_details,info_dict_visit,info_dict_patreon]
        with open('info.toml','w+',encoding="utf-8") as f:
            for i in info_dicts:
                f.write(toml.dumps(i))
                f.write("\n")
        print('OK')

        #if flagged, move a resulting directory to a network share
        if move_to_share:
            print('Sending files to a home server...',end=' ')
            shared_folder_path=dump_path+channel_info_json['channel']+'/'+dir_name
            os.chdir(os.pardir)
            #import shutil
            while True:
                try:
                    dest = shutil.move(dir_name,shared_folder_path)
                    break
                except shutil.Error:
                    print('Failed to move files, waiting 15 seconds and trying again')
                    time.sleep(15)
                    print('Removing previously generated files...')
                    if os.path.exists(shared_folder_path) and os.path.isdir(shared_folder_path):
                        shutil.rmtree(shared_folder_path)
                    time.sleep(5)
            print('OK')
    except Exception as e:
        print('THE SCRIPT HAS CRASHED!!!!!!!!!')
        print(url,'could not be downloaded. Verifying the cause of a crash...')
        if handle_crashes:
            #clean up
            #check if the folder has been created via verifying the existence of dir_name
            
            try:
                shutil.rmtree('./'+dir_name)
                #print(dir_name,'needs to be deleted, seems like we run out of space!')
            except (NameError,FileNotFoundError) as e: #NameError - dir_name not defined, FileNotFoundError - dir not created
                #dir_name does not exist, the error is of unknown origin
                print('The error is of unknown origin, check yt-dlp error output. The exception type is:',e)
            if log_url:
                print('Logging the download URL...',end=' ')
                while True:
                    try:
                        with open(dump_path+channel_info_json['channel']+'_errored_urls.txt','a') as f:
                            f.write(url+'\n')
                        print('OK')
                        break
                    except OSError:
                        print('Unable to log the url, retrying in 10 seconds...',end=' ')
                        time.sleep(10)
                        continue
        else:
            raise
    if rate_limiter:
        print('Waiting before the next video...',end=' ')
        random_wait(210,300)
    print('OK')

print('All done!')
