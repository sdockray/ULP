import os
import pyperclip

from settings import config
from reducting import get_single_audio


def check_audio_file(audio_dir, tx_id, transcript_id, media_id, start, end, is_pause=False, override_filename=None):
    if override_filename:
        file_location = os.path.join(audio_dir, tx_id, override_filename + ".mp4") 
    elif is_pause:
        file_location = os.path.join(audio_dir, tx_id, str(end) + "X.mp4") 
    else: 
        file_location = os.path.join(audio_dir, tx_id, str(start) + ".mp4")
    if os.path.exists(file_location):
        return file_location
    return get_single_audio((tx_id, media_id, "", start, end, False), name=override_filename)


def write_phrases_to_playlist(phrases, audio_dir, include_pauses=True, include_words=True):
    content = ""
    log_content = ""
    files = []
    for i, segment_info, wd, words in phrases:
        tx_id, transcript_id, media_id = segment_info
        audio_location = check_audio_file(audio_dir, tx_id, transcript_id, media_id, wd['start'], wd['end'], override_filename=str(wd['start'])+'-'+wd['word'])
        if include_words and audio_location:
            rel_audio_location = audio_location.replace(audio_dir + '/', '')
            the_file = rel_audio_location.replace(' ', '\ ')
            files.append(the_file.strip())
            content += "file  " + the_file + "\n"
            log_content += wd['word'] + " => " + rel_audio_location + "'\n"
    return content, log_content, files


def write_words_to_playlist(words, audio_dir, include_pauses=True, include_words=True):
    content = ""
    log_content = ""
    files = []
    for i, segment_info, wd in words:
        tx_id, transcript_id, media_id = segment_info
        audio_location = check_audio_file(audio_dir, tx_id, transcript_id, media_id, wd['start'], wd['end'])
        if include_words and audio_location:
            rel_audio_location = audio_location.replace(audio_dir + '/', '')
            the_file = rel_audio_location.replace(' ', '\ ')
            files.append(the_file.strip())
            content += "file '" + the_file + "'\n"
            log_content += wd['word'] + " => " + rel_audio_location + "'\n"
        #TODO: Deal with pauses, which are not working
        """
        if include_pauses and os.path.exists(os.path.join(audio_dir, tx_id, str(wd['end']) + "X.mp4")):
            # f.write("file '" + tx_id +"--"+str(i+1) + ".mp4'\n")
            content += "file '" + os.path.join(tx_id, str(wd['end']) + "X.mp4") + "'\n"
            log_content += "<    > => " + os.path.join(tx_id, str(wd['end']) + "X.mp4") + "'\n"
        """
    return content, log_content, files


def crossfade_cmd(crossfade, files, audio_dir, playlist_filename):
    print("To generate a version with crossfade, execute the command that is now on your clipboard!")
    cmd = "cd " + audio_dir + " && ffmpeg -i " + ' -i '.join(files) + ' -filter_complex "'
    cf_parts = []
    padded_idx = None
    last_padded_idx = None
    for i, _ in enumerate(files):
        last_padded_idx = padded_idx
        padded_idx = f'{i:04}'
        if not last_padded_idx:
            continue
        if i == len(files) - 1:
            cf_cmd = "acrossfade=d=" + str(crossfade) + ":o=1:c1=tri:c2=tri"
        else:
            cf_cmd = "acrossfade=d=" + str(crossfade) + ":o=1:c1=tri:c2=tri[" + padded_idx + "];"
        if i==1:
            cf_cmd = "[0][1]" + cf_cmd
        else:
            cf_cmd = "[" + last_padded_idx + "][" + str(i) + "]" + cf_cmd
        cf_parts.append(cf_cmd)
    cmd += ' '.join(cf_parts)
    cmd += '" ' + playlist_filename + '.mp4 && cd ../../'
    # print(cmd)
    pyperclip.copy(cmd)


def pad_cmd(crossfade, files, audio_dir, playlist_filename):
    print("I can't do this yet!")
    


def write_to_playlist(parts, playlist_filename, include_pauses=True, include_words=True, log=False, crossfade=None):
    # print([(w[2]['word'],w[0])  for w in words])
    audio_dir = os.path.join(config['CACHE_DIR'], config['AUDIO_DIR'])
    playlist_loc = os.path.join(audio_dir, playlist_filename)
    #print("This playlist will have", len(words), "words")
    print("writing playlist for ffmpeg... do the following to build the file:")
    print("cd " + audio_dir + " && ffmpeg -f concat -safe 0 -i " + playlist_filename + " -c copy " + playlist_filename + ".mp4 && cd ../../")
    playlist_content = ""
    log_content = ""
    files = []
    if len(parts)>0 and len(parts[0])==4: # phrases
        """
        for a, b, c, words in parts:
            plc_add, lc_add = write_words_to_playlist(words, audio_dir, include_pauses=include_pauses, include_words=include_words)
            playlist_content += plc_add
            log_content += lc_add
        """
        plc_add, lc_add, pl_files = write_phrases_to_playlist(parts, audio_dir, include_pauses=include_pauses, include_words=include_words)
        playlist_content += plc_add
        log_content += lc_add
        files.extend(pl_files)
    else: # words
        plc_add, lc_add, pl_files = write_words_to_playlist(parts, audio_dir, include_pauses=include_pauses, include_words=include_words)
        playlist_content += plc_add
        log_content += lc_add
        files.extend(pl_files)
    with open(playlist_loc, 'w') as f:
        f.write(playlist_content)
    if log:
        with open(playlist_loc + ".log", 'w') as f:
            f.write(log_content)
    # Construct a crossfade command
    if crossfade and crossfade>0:
        crossfade_cmd(crossfade, files, audio_dir, playlist_filename)
    elif crossfade and crossfade<0:
        pad_cmd(-1*crossfade, files, audio_dir, playlist_filename)


if __name__=="__main__":
    print("Playlist.py")