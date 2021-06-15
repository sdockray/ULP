def alphabetize(words, reverse=False):
    return sorted(words, key = lambda w: w[2]['word'].lower(), reverse=reverse)


def by_length(words, reverse=False):
    return sorted(words, key = lambda w: w[2]['end']-w[2]['start'], reverse=reverse)


def by_speed(words, reverse=False):
    #return sorted(words, key = lambda w: -1*len(w[2]['word'])/(w[2]['end']-w[2]['start']))
    return sorted(words, key = lambda w: -1*len(w[2]['phones'])/(w[2]['end']-w[2]['start']), reverse=reverse)


def by_sound(words, reverse=False):
    return sorted(words, key = lambda w: '-'.join([p[0] for p in w[2]['phones']]), reverse=reverse)


# How far along is this word into the sentence
def by_depth_in_sentence(words, reverse=False):
    return sorted(words, key = lambda w: w[0], reverse=reverse)