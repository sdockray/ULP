import re
from sorters import by_length


def filter_duration(words, duration=.2, is_min=True):
    if is_min:
        # return filter(lambda w: w[2]['end'] - w[2]['start'] > duration, words)
        return [w for w in words if w[2]['end'] - w[2]['start'] > duration]
    else:
        # return filter(lambda w: w[2]['end'] - w[2]['start'] < duration, words)
        return [w for w in words if w[2]['end'] - w[2]['start'] < duration]


def filter_length(words, min_length=0, max_length=999):
    return filter(lambda w: len(w[2]['word'])>=min_length and len(w[2]['word'])<=max_length, words)


def filter_speed(words, speed=.2, is_min=True):
    if is_min:
        # return filter(lambda w: w[2]['end'] - w[2]['start'] > duration, words)
        return [w for w in words if len(w[2]['phones'])/(w[2]['end']-w[2]['start']) > speed]
    else:
        # return filter(lambda w: w[2]['end'] - w[2]['start'] < duration, words)
        return [w for w in words if len(w[2]['phones'])/(w[2]['end']-w[2]['start']) < speed]


def filter_pos(words, pos, keep=True):
    if keep:
        # return filter(lambda w: w[2]['nlp_pos'] == pos, words)
        return [w for w in words if w[2]['nlp_pos'] == pos]
    else:
        return [w for w in words if not w[2]['nlp_pos'] == pos]


def filter_words(words, allowed_list, keep=True):
    # return filter(lambda w: re.sub('[^A-Za-z0-9\']+', '', w[2]['word']).lower() in allowed_list, words)
    if keep:
        return [w for w in words if re.sub('[^A-Za-z0-9\']+', '', w[2]['word']) in allowed_list]
    else:
        return [w for w in words if not re.sub('[^A-Za-z0-9\']+', '', w[2]['word']) in allowed_list]


def filter_letters(words, letters=[], keep=False):
    if keep:
        return [w for w in words if all(l in w[2]['word'].lower() for l in letters)] 
    else:
        return [w for w in words if not all(l in w[2]['word'].lower() for l in letters)] 


def filter_phonemes(words, phones, location='anywhere'):
    matches = []
    for w in words:
        if len(w[2]['phones']) >= len(phones):
            word_phones = [p[0] for p in w[2]['phones']]
            #print(word_phones[:-1*len(phones)], phones)
            if location == 'end' and phones == word_phones[-1*len(phones):]: 
                matches.append(w)  
            elif location == 'start' and phones == word_phones[0:len(phones)]: 
                matches.append(w)
            elif location == 'anywhere' and all(elem in word_phones for elem in phones):
                matches.append(w)
            elif location == 'somewhere' and any(elem in word_phones for elem in phones):
                matches.append(w)
    return matches  


def random_words(words, num):
    return sample(words,num)


def specific_words(words, script):
    script_list = script.split(' ')
    allowed_words = list(filter_words(words, script_list))
    allowed_words = by_length(allowed_words)
    new_words = []
    for word in script_list:
        # @TODO: Allow it to choose a random instance rather than always the first one it comes across?
        found = False
        for wd in allowed_words:
            if not found and re.sub('[^A-Za-z0-9\']+', '', wd[2]['word']).lower() == word.lower():
                new_words.append(wd)
                found = True
    # print(new_words)
    return new_words


def make_phrase(words, start_idx, length):
    if len(words)>start_idx:
        phrase = (words[start_idx][0], words[start_idx][1], words[start_idx][2], [])
    else:
        return False
    idx = start_idx
    while idx < len(words) and idx < start_idx + length:
        phrase[3].append(words[idx])
        if idx > start_idx:
            phrase[2]['word'] += words[idx][2]['word']
            phrase[2]['phones'].extend(words[idx][2]['phones'])
            phrase[2]['end'] += words[idx][2]['end'] - words[idx][2]['start']
        idx += 1
    # Trying to capture words that end in the space after the end
    if idx == start_idx + length and idx < len(words):
        phrase[2]['end'] = words[idx][2]['start']
    return phrase


def make_phrases(words, phrase_defs):
    return [make_phrase(words, np[0], np[1]) for np in phrase_defs]