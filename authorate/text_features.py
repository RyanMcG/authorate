import numpy, nltk
from nltk.probability import FreqDist, ConditionalFreqDist
from itertools import tee, izip


def text_to_vector(text):
    extr = TextFeatures()
    extr.add_text(text)
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

    def __init__(self):
        self.tokens = []
        self.text = ""
        self.fdist = FreqDist()

    def __sentence_lengths(self):
        "Return a list of the lengths of sentences"
        # Split into sentences
        sentences = nltk.sent_tokenize(self.text)
        return [len(sen.split()) for sen in sentences]

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

    def add_text(self, text):
        self.text += " " + text
        tokens = nltk.word_tokenize(text)
        self.tokens += tokens
        for token in tokens:
            self.fdist.inc(token.lower())

    def to_vector(self):
        return ([self.avg_word_length(),
                 self.std_dev_word_length(),
                 float(self.max_word_length()),
                 float(self.max_sentence_length()),
                 float(self.min_sentence_length()),
                 self.avg_sentence_length(),
                 self.std_sentence_length(),
                 self.unique_word_freq()] +
                self._word_freq_to_vector() +
                self._punctuation_freq_vector() +
                self._word_length_freq_to_vector() +
                #self._POS_freq_to_vector() +
                self._POS_cond_freq_to_vector())

    def word_freq(self):
        return self.fdist

    def word_length_freq(self):
        return FreqDist(len(word) for word in self.tokens)

    def POS_freq(self):
        "Returns the frequency distribution of parts of speech"
        tagged = nltk.pos_tag(self.tokens)
        pos_dist = FreqDist()
        for pos_pair in tagged:
            pos_dist.inc(pos_pair[1])
        return pos_dist

    def POS_cond_freq(self):
        "Returns the conditional frequency distribution of parts of speech"
        tagged = nltk.pos_tag(self.tokens)
        cond_dist = ConditionalFreqDist()
        pos = [word_pos[1] for word_pos in tagged]
        [cond_dist[pair[0]].inc(pair[1]) for pair in pairwise(pos)]
        return cond_dist

    def avg_word_length(self):
        return numpy.average([len(word) for word in self.tokens])

    def std_dev_word_length(self):
        return numpy.std([len(word) for word in self.tokens])

    def max_word_length(self):
        return max([len(word) for word in self.tokens])

    def unique_word_freq(self):
        return float(self.fdist.B()) / self.fdist.N()

    def max_sentence_length(self):
        return max(self.__sentence_lengths())

    def min_sentence_length(self):
        return min(self.__sentence_lengths())

    def avg_sentence_length(self):
        return numpy.average(self.__sentence_lengths())

    def std_sentence_length(self):
        return numpy.std(self.__sentence_lengths())


if __name__ == "__main__":
    text1 = """Call me Ishmael."""
    text2 = """Some years ago, never mind how long precisely,
               having little or no money in my purse, and nothing
               particular to interest me on shore, I thought I
               would sail about a little and see the watery part
               of the world."""
    extr = TextFeatures()
    extr.add_text(text1)
    extr.add_text(text2)
    print(extr.to_vector())
    print(extr._POS_cond_freq_to_vector())
