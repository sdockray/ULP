import os
import sys
import json
import requests
import curlify

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from settings import config


request_headers = {
    'Accept': '*/*',
    'User-Agent': config['USER_AGENT'],
    'X-Using-Reduct-Fetch': 'true',
}
cookies_jar = requests.cookies.RequestsCookieJar()
cookies_jar.set('token', config['TOKEN'])


def setup_retry():
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=4
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    return http


def add_sample(spec, tid, mid, curT, start, end):
    duration = round(end - start, 3)
    spec.append({
        'dbpath': ['doc', tid, 'media', mid, 'blob_name'], 
        'start': curT, 
        'duration': duration, 
        'source_start': start, 
        'type': 'video', 
        'opacity': [[0,1]]
    })
    spec.append({
        'dbpath': ['doc', tid, 'media', mid, 'blob_name'], 
        'start': curT, 
        'duration': duration, 
        'source_start': start, 
        'type': 'audio', 
        'volume': [[0,1]]
    })
    return curT + duration


def create_seq(parts):
    samples = []
    curT = 0
    for part in parts:
        curT = add_sample(samples, part[0], part[1], curT, part[3], part[4])
    return samples, curT


def get_single_audio(part, name=None):
    samples, duration = create_seq([part,])
    # print(samples)
    fn = name if name else str(part[3]) 
    if part[5]: 
        fn += "X"
    return download_audio(samples, duration, fn, transcript_id=part[0]) # now use start time for filename


def get_audio(parts, combine=False, name=None):
    if combine and name:
        print("Creating combined file with",len(parts),"parts")
        samples, duration = create_seq(parts)
        download_audio(samples, duration, name)
    else:
        print("Creating",len(parts),"audio files")
        for part in parts:
            get_single_audio(part, name=name)


def download_audio(samples, duration, filename, transcript_id=None):
    if transcript_id:
        if not os.path.exists(os.path.join(config['CACHE_DIR'], config['AUDIO_DIR'], transcript_id)):
            os.makedirs(os.path.join(config['CACHE_DIR'], config['AUDIO_DIR'], transcript_id))
        audio_loc = os.path.join(config['CACHE_DIR'], config['AUDIO_DIR'], transcript_id, filename + ".mp4")
    else:
        audio_loc = os.path.join(config['CACHE_DIR'], config['AUDIO_DIR'], filename + ".mp4")
    if os.path.exists(audio_loc):
        print("File already exists in cache:", audio_loc)
        # return True
    url = config['DEFAULT_PROD'] + "/render"
    # print(samples)
    response = requestsX.post(
        url,
        json={
            'org': config['ORG_ID'], 
            'seq': samples,
            'duration': duration,
            'size': 480,
            'ext': 'mp4'
        },
        headers=request_headers,
        cookies=cookies_jar
    )
    if response.status_code == 200:
        print('Writing audio file to:', audio_loc)
        with open(audio_loc, 'wb') as f:
            totalbits = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    totalbits += 1024
                    # print("Downloaded",totalbits*1025,"KB...")
                    f.write(chunk)
        return audio_loc
    else:
        print()
        print("Failed to get audio:", response.status_code)
        print(response.reason)
        print(" - ", audio_loc)
        print(curlify.to_curl(response.request))

        return None


def load_transcript(docId):
    transcript_loc = os.path.join(config['CACHE_DIR'], config['TRANSCRIPTS_DIR'], docId + ".json")
    if os.path.exists(transcript_loc):
        with open(transcript_loc, 'r') as f:
            return json.load(f)
    else:
        return {}


def get_transcript(docId, ignore_cache=False):
    transcript_loc = os.path.join(config['CACHE_DIR'], config['TRANSCRIPTS_DIR'], docId + ".json")
    if not ignore_cache and os.path.exists(transcript_loc):
        print("Transcript already exists in cache")
        return load_transcript(docId)
    url = config['DEFAULT_PROD'] + "/diarized_transcript.json"
    response = requestsX.get(
        url,
        params={'doc': docId, 'phonemes': '1'},
        headers=request_headers,
        cookies=cookies_jar
    )
    print("Loading transcript from:", url)
    if response.status_code == 200:
        with open(transcript_loc, 'w') as f:
            f.write(response.text)
            return json.loads(response.text)
    else:
        print("Failed to get transcript:", response.status_code)
        return {}


def get_transcript_list():
    # @TODO: This doesn't work, so figure it out
    url = config['DEFAULT_PROD'] + "/"
    response = requestsX.get(
        url,
        headers=request_headers,
        cookies=cookies_jar
    )
    print("Loading transcript list from:", url)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to get transcript list:", response.status_code)
        return {}


def get_audio_for_transcript(transcript_id):
    transcript = get_transcript(transcript_id)
    last_end = 0
    parts = []
    for segment in transcript['segments']:
        for i, wd in enumerate(segment['wdlist']):
            # Get the pause if there is one
            if i>0:
                if wd['start'] > last_end:
                    # print("< pause > ", last_end, wd['start'])
                    parts.append((transcript_id, segment['media_id'], segment['tx_id']+'--'+str(i), last_end, wd['start'], True))
                    pass
            # print( wd['word'], wd['start'], wd['end'] )
            parts.append((transcript_id, segment['media_id'], segment['tx_id']+'-'+str(i), wd['start'], wd['end'], False))
            last_end = wd['end']
            # get_audio(transcript_id, segment['media_id'], segment['tx_id']+'-'+str(i), wd)
    get_audio(parts, combine=False)


def get_transcript_info(transcript_id):
    transcript = get_transcript(transcript_id)
    num_segments = len(transcript['segments'])
    speakers = [s['speaker_name'] for s in transcript['segments']]
    speakers = list(set(speakers))
    return {
        'num_segments': num_segments,
        'speaker_ids': speakers
    }


def load_words(transcript_id, segment_idx=None, speaker_id=None):
    transcript = get_transcript(transcript_id)
    parts = []
    for i, s in enumerate(transcript['segments']):
        include_segment = False
        if speaker_id and s['speaker_name']==speaker_id:
            print("Including segment with speaker:", speaker_id)
            include_segment = True
        elif isinstance(segment_idx, list) and i in segment_idx:
            print("Including segment id:", i)
            include_segment = True
        elif i==segment_idx:
            print("Including segment id:", i)
            include_segment = True
        elif segment_idx == "all":
            include_segment = True
        if include_segment:
            # parts.extend([(j, s['tx_id'], wd) for j, wd in enumerate(s['wdlist'])])
            parts.extend([(j, (transcript_id, s['tx_id'], s['media_id']), wd) for j, wd in enumerate(s['wdlist'])])
    print("Getting segments has retrieved", len(parts), "samples")
    return parts


print("Setting up the requestsX variable for making Reduct calls")
requestsX = setup_retry()


if __name__=="__main__":
    print("Reduct ingester starting up")
    if not os.path.exists(config['CACHE_DIR']):
        print("Creating cache directories")
        os.makedirs( os.path.join(config['CACHE_DIR'], config['TRANSCRIPTS_DIR']) )
        os.makedirs( os.path.join(config['CACHE_DIR'], config['AUDIO_DIR']) )
        os.makedirs( os.path.join(config['CACHE_DIR'], config['MISC_DIR']) )
    
    # get_audio_for_transcript('31166f35aa') # Halcyon
    # get_audio_for_transcript('01effe63e9') # Thomas
    # get_audio_for_transcript('ecbf8fb7bf') # Lauren Lee Mccarty
    get_audio_for_transcript('8491888ee4') # Burroughs
    # print(get_transcript_list())