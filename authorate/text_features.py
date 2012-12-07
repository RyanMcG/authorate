import numpy, nltk
from sqlalchemy import Column, Integer, String
from nltk.probability import FreqDist, ConditionalFreqDist
from itertools import tee, izip
from authorate.model import WordCount


def text_to_vector(text, session):
    extr = TextFeatures(text, session)
    return extr.to_vector()

# From itertools recipes
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

class TextFeatures:
    
    parts_of_speech = ["NN", "NNS", "NNP", "NNPS", "DT", "RB", "IN", "PRP",
                       "CC", "CD", "VB", "VBD", "VBN", "VBG", "JJ", "EX", "FW"]
    most_common_words = ["the", "of", "to", "and", "a", "for", "on"
                         "in", "is", "it", "you", "at"]
    punctuation = [".", ",", "!", "?", ";", ":"]

    def __init__(self, text, session):
        self.session = session
        self.tokens = nltk.word_tokenize(text)
        self.text = text
        self.fdist = FreqDist()
        for token in self.tokens:
            self.fdist.inc(token.lower())
        self.tagged = nltk.pos_tag(self.tokens)
        self.counts = self.__get_word_commonality_counts(self.text.split())
        self.word_lengths = [len(word) for word in self.tokens]
        self.sentences = nltk.sent_tokenize(self.text)
        self.sentence_lengths = [len(sen.split()) for sen in self.sentences]

    def __get_word_commonality_counts(self, words):
        results = [self.session.query(WordCount).filter_by(word=w).first() for w in words]
        results = [w.count for w in results if w is not None]
        if len(results) == 0:
            return [0]
        return results

    def _word_freq_to_vector(self):
        dist = self.word_freq()
        return [dist.freq(word) for word in TextFeatures.most_common_words]

    def _punctuation_freq_vector(self):
        dist = self.word_freq()
        return [dist.freq(mark) for mark in TextFeatures.punctuation]

    def _word_length_freq_to_vector(self):
        dist = self.word_length_freq()
        return [dist.freq(length) for length in range(1, 12)]

    def _POS_freq_to_vector(self):
        dist = self.POS_freq()
        return [dist.freq(pos) for pos in TextFeatures.parts_of_speech]

    def _POS_cond_freq_to_vector(self):
        dist = self.POS_cond_freq()
        freq_vector = []
        for pos0 in TextFeatures.parts_of_speech:
            for pos1 in TextFeatures.parts_of_speech:
                freq_vector.append(dist[pos0].freq(pos1))
        return freq_vector

    def _word_rarity_freq_to_vector(self):
        dist = self.word_rarity_freq()
        return [dist.freq(i) for i in range(13)]

    def to_vector(self):
        return ([self.avg_word_length(),
                 self.std_dev_word_length(),
                 float(self.max_word_length()),
                 float(self.max_sentence_length()),
                 float(self.min_sentence_length()),
                 self.avg_sentence_length(),
                 self.std_sentence_length(),
                 float(self.avg_word_commonality()),
                 float(self.std_word_commonality()),
                 self.unique_word_freq()] +
                self._word_rarity_freq_to_vector() +
                self._word_freq_to_vector() +
                self._punctuation_freq_vector() +
                self._word_length_freq_to_vector() +
                self._POS_freq_to_vector()
                #self._POS_cond_freq_to_vector()
                )

    def word_freq(self):
        return self.fdist

    def word_length_freq(self):
        return FreqDist(len(word) for word in self.tokens)

    def POS_freq(self):
        "Returns the frequency distribution of parts of speech"
        pos_dist = FreqDist()
        for pos_pair in self.tagged:
            pos_dist.inc(pos_pair[1])
        return pos_dist

    def POS_cond_freq(self):
        "Returns the conditional frequency distribution of parts of speech"
        cond_dist = ConditionalFreqDist()
        pos = [word_pos[1] for word_pos in self.tagged]
        [cond_dist[pair[0]].inc(pair[1]) for pair in pairwise(pos)]
        return cond_dist

    def word_rarity_freq(self):
        "Returns the frequency distribution of groups of word rarities"
        rarity_dist = FreqDist()
        for common in self.counts:
            if common > 500000000:
                rarity_dist.inc(0)
            elif common > 450000000:
                rarity_dist.inc(1)
            elif common > 400000000:
                rarity_dist.inc(2)
            elif common > 350000000:
                rarity_dist.inc(3)
            elif common > 300000000:
                rarity_dist.inc(4)
            elif common > 250000000:
                rarity_dist.inc(5)
            elif common > 200000000:
                rarity_dist.inc(6)
            elif common > 100000000:
                rarity_dist.inc(7)
            elif common > 50000000:
                rarity_dist.inc(8)
            elif common > 5000000:
                rarity_dist.inc(9)
            elif common > 2000000:
                rarity_dist.inc(10)
            elif common > 500000:
                rarity_dist.inc(11)
            else:
                rarity_dist.inc(12)
        return rarity_dist

    def avg_word_length(self):
        return numpy.average(self.word_lengths)

    def std_dev_word_length(self):
        return numpy.std(self.word_lengths)

    def max_word_length(self):
        return max(self.word_lengths)

    def unique_word_freq(self):
        return float(self.fdist.B()) / self.fdist.N()

    def max_sentence_length(self):
        return max(self.sentence_lengths)

    def min_sentence_length(self):
        return min(self.sentence_lengths)

    def avg_sentence_length(self):
        return numpy.average(self.sentence_lengths)

    def std_sentence_length(self):
        return numpy.std(self.sentence_lengths)

    def avg_word_commonality(self):
        if numpy.isnan(numpy.min(self.counts)):
            print "FOUND ONE"
        return numpy.average(self.counts)

    def std_word_commonality(self):
        return numpy.std(self.counts)