import sys
import os

sys.path.insert(0, os.path.abspath('..'))

from clint.textui import prompt, puts, colored, validators
from playlist import write_to_playlist
from reducting import load_words, get_transcript_info, get_transcript_list
from language import do_nlp
from filters import filter_duration, filter_speed, filter_length, filter_letters, filter_phonemes, filter_words, filter_pos, specific_words, make_phrases
from sorters import alphabetize, by_length, by_speed, by_sound, by_depth_in_sentence




def apply_transcript(tid):
    info = get_transcript_info(tid)
    options = [{'selector': i+1, 'prompt': k, 'return': k} for i, k in enumerate(info['speaker_ids'])]
    options.append({'selector': 'g', 'prompt': 'Get a specific segment', 'return': '_index'})
    options.append({'selector': 'a', 'prompt': 'All of it', 'return': '_all'})
    o = prompt.options("What part of the transcript should I load?", options)
    if o == "_all":
        return load_words(tid, segment_idx='all')
    elif o == "_index":
        val = prompt.query("Enter a number between 0 and {0}".format(info['num_segments']))
        val = [int(v) for v in val.split(',')]
        return load_words(tid, segment_idx=val)
    else:
        return load_words(tid, speaker_id=o)


def apply_filter(name, words):
    if name=="min_duration":
        val = float(prompt.query("Minimum duration of a word?"))
        puts(colored.yellow("Filtering out words that are shorter than {0} seconds".format(str(val))))
        return filter_duration(words, val, is_min=True)
    elif name=="max_duration":
        val = float(prompt.query("Maximum duration of a word?"))
        puts(colored.yellow("Filtering out words that are longer than {0} seconds".format(str(val))))
        return filter_duration(words, val, is_min=False)
    elif name=="min_length":
        val = int(prompt.query("Minimum number of letters in the word?"))
        puts(colored.yellow("Filtering out words that are less than {0} letters".format(str(val))))
        return filter_length(words, min_length=val)
    elif name=="max_length":
        val = int(prompt.query("Maximum number of letters in the word?"))
        puts(colored.yellow("Filtering out words that are more than {0} letters".format(str(val))))
        return filter_length(words, max_length=val)
    elif name=="filter_letter_out":
        val = prompt.query("Words with this letter will be removed:")
        puts(colored.yellow("Filtering out words that contain '{0}'".format(val)))
        return filter_letters(words, letters=val.split(','))
    elif name=="filter_letter_in":
        val = prompt.query("Words without this letter will be removed:")
        puts(colored.yellow("Filtering out words that contain '{0}'".format(val)))
        return filter_letters(words, letters=val.split(','), keep=True)
    elif name=="phonemes":
        val = prompt.query("Phonemes you're interested in (comma separated):")
        phones = val.split(',')
        options = [
            {'selector': 1, 'prompt': 'Sequence at the start of words', 'return': 'start'},
            {'selector': 2, 'prompt': 'Sequence at the end of words', 'return': 'end'},
            {'selector': 3, 'prompt': 'Sequence anywhere in the words', 'return': 'anywhere'},
            {'selector': 4, 'prompt': 'Any phoneme anywhere in the words', 'return': 'somewhere'},
        ]
        o = prompt.options("Where are you interested in finding the phonemes?", options)
        puts(colored.yellow("Filtering out words without phonemes '{0}'".format(val)))
        return filter_phonemes(words, phones, location=o)
    elif name=="pos":
        val = prompt.query("Part of speech:")
        puts(colored.yellow("Keeping only: {0}".format(val)))
        do_nlp(words)
        return filter_pos(words, val, keep=True)
    elif name=="pos_remove":
        val = prompt.query("Part of speech:")
        puts(colored.yellow("Removing all: {0}".format(val)))
        do_nlp(words)
        return filter_pos(words, val, keep=False)
    elif name=="noun_phrases":
        nps, _, _ = do_nlp(words, do_noun_phrases=True)
        return make_phrases(words, nps)
    elif name=="noun_verb_phrases":
        _, nps, _ = do_nlp(words, do_noun_verb_phrases=True)
        return make_phrases(words, nps)
    elif name=="entities":
        _, _, ents = do_nlp(words, do_entities=True)
        return make_phrases(words, ents)
    elif name=="min_speed":
        val = float(prompt.query("Minimum speed of a word (phonemes per second)?"))
        puts(colored.yellow("Filtering out words that are slower than {0} phonemes per second".format(str(val))))
        return filter_speed(words, val, is_min=True)
    elif name=="max_speed":
        val = float(prompt.query("Maximum speed of a word (phonemes per second)?"))
        puts(colored.yellow("Filtering out words that are faster than {0} phonemes per second".format(str(val))))
        return filter_speed(words, val, is_min=False)
    elif name=="words":
        val = prompt.query("These words will be kept:")
        puts(colored.yellow("Filtering out words that aren't '{0}'".format(val)))
        return filter_words(words, letters=val.replace(' ','').split(','))
    elif name=="words_remove":
        val = prompt.query("These words will be removed:")
        puts(colored.yellow("Filtering out these words: '{0}'".format(val)))
        return filter_words(words, letters=val.replace(' ','').split(','), keep=False)
    elif name=="make_phrase":
        script = prompt.query("Write a few words, a phrase, a sentence:")
        return specific_words(words, script)
    else:
        puts(colored.red("This isn't a valid filter: {0}".format(name)))
        return words


def apply_sort(name, words):
    if name=="alpha":
        puts(colored.yellow("Sorting {0} samples".format(str(len(words)))))
        return alphabetize(words, reverse=False)
    elif name=="reverse_alpha":
        puts(colored.yellow("Sorting {0} samples reverse alphabetically".format(str(len(words)))))
        return alphabetize(words, reverse=True)
    elif name=="duration":
        puts(colored.yellow("Sorting {0} samples by shortest to longest duration word".format(str(len(words)))))
        return by_length(words)
    elif name=="reverse_duration":
        puts(colored.yellow("Sorting {0} samples by longest to shortest duration word".format(str(len(words)))))
        return by_length(words, reverse=True)
    elif name=="speed":
        puts(colored.yellow("Sorting {0} samples by fastest to slowest speed".format(str(len(words)))))
        return by_speed(words)
    elif name=="reverse_speed":
        puts(colored.yellow("Sorting {0} samples by slowest to fastest speed".format(str(len(words)))))
        return by_speed(words, reverse=True)
    elif name=="sound":
        puts(colored.yellow("Sorting {0} samples by the beginning sound".format(str(len(words)))))
        return by_sound(words)
    elif name=="reverse_sound":
        puts(colored.yellow("Sorting {0} samples by the beginning sound, but in reverse".format(str(len(words)))))
        return by_sound(words, reverse=True)
    elif name=="sentence_depth":
        puts(colored.yellow("Sorting {0} samples by how close they are to the start of the sentence".format(str(len(words)))))
        return by_depth_in_sentence(words)
    elif name=="reverse_sentence_depth":
        puts(colored.yellow("Sorting {0} samples by far they are from the start of the setence".format(str(len(words)))))
        return by_depth_in_sentence(words, reverse=True)
    

if __name__ == '__main__':
    # Include transcripts
    if '--reload' in sys.argv[1:]:
        transcripts = get_transcript_list(ignore_cache=True)
    else:
        transcripts = get_transcript_list()    
    done_transcripts = False
    words = []
    while not done_transcripts:
        inst_options = [{'selector': i+1, 'prompt': transcripts[k], 'return': k} for i, k in enumerate(transcripts)]
        inst_options.append({'selector': 'n', 'prompt': 'NO MORE!', 'return': None})
        inst = prompt.options("\nWhich transcript to include?", inst_options)
        if inst:
            puts(colored.yellow("Including: {0}".format(transcripts[inst])))
            words.extend(apply_transcript(inst))
        if not inst:
            done_transcripts = True

    # Apply filters
    done_filtering = False
    if not done_filtering:
        filter_options = [
            {'selector': 1, 'prompt': 'Minimum duration', 'return': 'min_duration'},
            {'selector': 2, 'prompt': 'Maximum duration', 'return': 'max_duration'},
            {'selector': 3, 'prompt': 'Minimum letters in word', 'return': 'min_length'},
            {'selector': 4, 'prompt': 'Maximum letters in word', 'return': 'min_length'},
            {'selector': 5, 'prompt': 'Remove words with a certain letter', 'return': 'filter_letter_out'},
            {'selector': 6, 'prompt': 'Only keep words with a certain letter', 'return': 'filter_letter_in'},
            {'selector': 7, 'prompt': 'Filter by phonemes', 'return': 'phonemes'},
            {'selector': 8, 'prompt': 'Keep part of speech', 'return': 'pos'},
            {'selector': 9, 'prompt': 'Remove part of speech', 'return': 'pos_remove'},
            {'selector': 10, 'prompt': 'Noun phrases', 'return': 'noun_phrases'},
            {'selector': 11, 'prompt': 'Noun verb phrases', 'return': 'noun_verb_phrases'},
            {'selector': 12, 'prompt': 'Entities', 'return': 'entities'},
            {'selector': 13, 'prompt': 'Minimum speed', 'return': 'min_velocity'},
            {'selector': 14, 'prompt': 'Maximum speed', 'return': 'max_velocity'},
            {'selector': 15, 'prompt': 'Keep words', 'return': 'words'},
            {'selector': 16, 'prompt': 'Remove words', 'return': 'words_remove'},
            {'selector': 17, 'prompt': 'Make a phrase', 'return': 'make_phrase'},
            # Add more filters here
            {'selector': 'n', 'prompt': 'No more filters', 'return': None},
        ]
        chosen_filter = prompt.options("\nWhich filter do you want to apply?", filter_options)
        if not chosen_filter:
            done_filtering = True
        else:
            before = len(words)
            words = apply_filter(chosen_filter, words)
            after = len(words)
            puts(colored.yellow("{0} words have been removed".format(before-after)))
    
    # Apply sorting
    sort_options = [
        {'selector': 1, 'prompt': 'Alphabetical', 'return': 'alpha'},
        {'selector': 2, 'prompt': 'Reverse alphabetical', 'return': 'reverse_alpha'},
        {'selector': 3, 'prompt': 'By sound at beginning of word', 'return': 'sound'},
        {'selector': 4, 'prompt': 'By sound at beginning of word in reverse', 'return': 'reverse_sound'},
        {'selector': 5, 'prompt': 'Short to long duration words', 'return': 'duration'},
        {'selector': 6, 'prompt': 'Long to short duration words', 'return': 'reverse_duration'},
        {'selector': 7, 'prompt': 'Fast to slow words', 'return': 'speed'},
        {'selector': 8, 'prompt': 'Slow to fast words', 'return': 'reverse_speed'},
        {'selector': 9, 'prompt': 'By closeness to start of sentence', 'return': 'sentence_depth'},
        {'selector': 10, 'prompt': 'By distance from start of sentence', 'return': 'reverse_sentence_depth'},
        # Add more sorts here
        {'selector': 'n', 'prompt': 'No sorting', 'return': None},
    ]
    chosen_sort = prompt.options("\nHow do you want to sort the sounds?", sort_options)
    if chosen_sort:
        words = apply_sort(chosen_sort, words)
    
    # Write playlist
    filename = prompt.query('Output name (no extension)', default='output')
    crossfade = prompt.query('Crossfade? (enter a number or just press ENTER for none)', default=None)
    if crossfade:
        crossfade = float(crossfade)

    if filename.startswith("test-"):
        write_to_playlist(words[0:80], filename, include_pauses=False, log=True, crossfade=crossfade)
    else:
        write_to_playlist(words, filename, include_pauses=False, log=True, crossfade=crossfade)
    