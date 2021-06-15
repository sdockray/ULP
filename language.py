import spacy
from spacy.tokens import Doc
from spacy.training import Alignment
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.util import filter_spans


def label_noun_phrase(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    match_type = doc.vocab.strings[match_id]
    span = doc[start:end]
    if match_type == "SimpleNoun":
        span._.root = span[0].text
    elif match_type == "SimpleNounPhrase":
        span._.root = span[1].text
        span._.branch = span[0].text
    elif match_type == "CompoundNoun":
        span._.root = "%s %s" % (span[0].text, span[1].text)  
    elif match_type == "CompoundNounPhrase":
        span._.root = "%s %s" % (span[1].text, span[2].text)
        span._.branch = span[0].text


def setup_noun_phrase_matcher(nlp):
    Span.set_extension("root", default=None)
    Span.set_extension("branch", default="-")
    matcher = Matcher(nlp.vocab)
    matcher.add("SimpleNoun", [[{'POS': 'NOUN'}]], on_match=label_noun_phrase)
    matcher.add("SimpleNounPhrase", [[{'POS': 'ADJ'}, {'POS': 'NOUN'}]], on_match=label_noun_phrase)
    matcher.add("CompoundNoun", [[{'POS': 'NOUN', 'DEP': 'compound'}, {'POS': 'NOUN'}]], on_match=label_noun_phrase)
    matcher.add("CompoundNounPhrase", [[{'POS': 'ADJ'}, {'POS': 'NOUN', 'DEP': 'compound'}, {'POS': 'NOUN'}]], on_match=label_noun_phrase)
    return matcher


def label_noun_verb(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    match_type = doc.vocab.strings[match_id]
    span = doc[start:end]
    if match_type == "SimpleNounVerbPhrase":
        span._.root = "%s %s" % (span[0].text, span[1].text) 


def setup_noun_verb_matcher(nlp):
    Span.set_extension("root", default=None)
    Span.set_extension("branch", default="-")
    matcher = Matcher(nlp.vocab)
    matcher.add("SimpleNounVerbPhrase", [[{'POS': 'NOUN'}, {'POS': 'VERB'}]], on_match=label_noun_verb)
    return matcher


def get_nlp_phrases(nlp, doc, align, parts, matcher):
    matches = matcher(doc)
    filtered_spans = filter_spans([doc[start:end] for _, start, end in matches])
    noun_phrases = []
    for _, start, end in matches:
        if doc[start:end] in filtered_spans:
            # print(doc[start:end], start, end, parts[align.y2x.dataXd[start]][2]['word'])
            noun_phrases.append([align.y2x.dataXd[start], align.y2x.dataXd[end] - align.y2x.dataXd[start]])
    return noun_phrases


def do_nlp(parts, do_noun_phrases=False, do_noun_verb_phrases=False, do_entities=False):
    nlp = spacy.load("en_core_web_sm")
    words = [p[2]['word'] for p in parts]  
    content = ''.join(words)
    doc = nlp(content)
    spacy_words = [token.text for token in doc]
    align = Alignment.from_strings(words, spacy_words)
    
    for i, idx in enumerate(align.y2x.dataXd):
        if 'nlp_pos' not in parts[idx][2]:
            parts[idx][2]['nlp_pos'] = doc[i].pos_
            parts[idx][2]['nlp_lemma'] = doc[i].lemma_
            parts[idx][2]['nlp_tag'] = doc[i].tag_
    
    noun_phrases = []
    noun_verb_phrases = []
    entities = []
    if do_noun_phrases:
        matcher = setup_noun_phrase_matcher(nlp)
        noun_phrases = get_nlp_phrases(nlp, doc, align, parts, matcher)
    elif do_noun_verb_phrases:
        matcher = setup_noun_verb_matcher(nlp)
        noun_verb_phrases = get_nlp_phrases(nlp, doc, align, parts, matcher)
    elif do_entities:
        good_ents = ["ORG", "PERSON", "LAW", "NORP", "FAC", "GPE", "LOC", "PRODUCT"]
        for ent in doc.ents:
            if ent.label_ in good_ents:
                entities.append([align.y2x.dataXd[ent.start], align.y2x.dataXd[ent.end] - align.y2x.dataXd[ent.start]])
    
    return noun_phrases, noun_verb_phrases, entities