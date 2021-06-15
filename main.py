import re
import os
import sys
import json
from random import sample 


from reducting import get_transcript
from settings import config
from playlist import write_to_playlist


# TODO: librosa for caching pitch, volume, etc. information in sound.py
# TODO: noun phrases and running sequences of words
# TODO: get_missing_audio() in playlist.py


if __name__=="__main__":
    print("Instrument starting up")
    
    # make a chain of filters

    
    words = get_segments('01effe63e9', speaker_id="speaker-1")
    _, noun_phrases = do_nlp(words, do_noun_verb_phrases=True)
    long_noun_phrases = filter(lambda w: w[1]>1, noun_phrases)
    phrases = []
    for np in long_noun_phrases:
        phrases.append(make_phrase(words, np[0], np[1]))
    # print(phrases)
    # phrases = alphabetize_words(phrases)
    write_to_playlist(phrases, 'nounverb-phrase-thomas.txt', include_pauses=False, log=True, crossfade=.1)
    

    """
    words = get_segments('31166f35aa', segment_idx=0)
    phrase = make_phrase(words, 1, 3)
    phrases = [phrase,]
    write_to_playlist(phrases, 'phrase-test.txt', include_pauses=False, log=True)
    """

    
    #words = get_segments('31166f35aa', segment_idx=2)
    # words = get_segments('31166f35aa', segment_idx="all")
    # words = get_segments('31166f35aa', speaker_id="Halcyon Lawrence")
    # words = get_segments('01effe63e9', segment_idx="all")
    # words = random_words(words, 3)
    # words = filter_phonemes(words, ["ih", "ng"], location="anywhere")
    # words = filter_phonemes(words, ["ih", "ng"], location="anywhere")
    # words = filter_phonemes(words, ["f", "ah"], location="anywhere") # iy, ao
    # words = filter_phonemes(words[0:200], ["iy", "ao"], location="somewhere")
    # words = alphabetize_words(words[0:25])
    
    # words = specific_words(words, "your words and my voice do not belong together")
    # write_to_playlist(words, 'AAA1.txt', include_pauses=False, log=True, crossfade=.05)
    # words.extend(get_segments('01effe63e9', segment_idx="all"))
    #do_nlp(words)
    #words = filter_pos(words, 'NOUN')
    # words = alphabetize_words(words)
    #words = by_speed(words)
    # words = filter_length(words, min_length=3)
    #write_words_to_playlist(words, 'halcyon-speed-nouns.txt', include_pauses=False, log=True)

    #write_words_to_playlist(short_to_long_words(filter_duration(words, min_duration=.25)), 'lengths-01effe63e9-0.txt', include_pauses=False)

    #write_words_to_playlist(short_to_long_words(filter_duration(words, min_duration=.4)), 'lengths-31166f35aa-2b.txt', include_pauses=False)
    #write_words_to_playlist(words, 'speaker-0-pauses.txt', include_pauses=True, include_words=False)
    """
    """