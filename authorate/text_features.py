import re, numpy, nltk
from nltk.probability import FreqDist


def text_to_vector(text):
    extr = TextFeatures()
    extr.add_text(text)
    return extr.to_vector()


class TextFeatures:

    def __init__(self):
        self.tokens = []
        self.text = ""
        self.fdist = FreqDist()

    def __sentence_lengths(self):
        sentences = res.split('\.|\?|\!', self.text)
        sentences = filter(None, sentences)
        return [len(sen.split()) for sen in sentences]

    def _word_freq_to_vector(self):
        dist = self.word_freq()
        most_common_words = ["the", "of", "to", "and", "a",
                             "in", "is", "it", "you", "at"]
        return [dist.freq(word) for word in most_common_words]

    def _punctuation_freq_vector(self):
        dist = self.word_freq()
        punctuation = [".", ",", "!", "?", ";", ":"]
        return [dist.freq(mark) for mark in punctuation]

    def _word_length_freq_to_vector(self):
        dist = self.word_length_freq()
        return [dist.freq(length) for length in range(1, 12)]

    def _POS_freq_to_vector(self):
        dist = self.POS_freq()
        parts_of_speech = ["NN", "NNS", "NNP", "NNPS", "DT", "RB", "IN", "PRP",
                           "CC", "CD", "VB", "VBD", "VBN", "JJ", "EX", "FW"]
        return [dist.freq(pos) for pos in parts_of_speech]

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
                 self.unique_word_freq()] +
                self._word_freq_to_vector() +
                self._punctuation_freq_vector() +
                self._word_length_freq_to_vector() +
                self._POS_freq_to_vector())

    def word_freq(self):
        return self.fdist

    def word_length_freq(self):
        return FreqDist(len(word) for word in self.tokens)

    def POS_freq(self):
        #nltk.download('maxent_treebank_pos_tagger')
        tagged = nltk.pos_tag(self.tokens)
        pos_dist = FreqDist()
        for pos_pair in tagged:
            pos_dist.inc(pos_pair[1])
        return pos_dist

    def avg_word_length(self):
        return sum([len(word) for word in self.tokens]) / float(self.fdist.N())

    def std_dev_word_length(self):
        avg = self.avg_word_length()
        sqr_sum = sum([(len(word) - avg) ** 2 for word in self.tokens])
        return (sqr_sum / self.fdist.N()) ** 0.5

    def max_word_length(self):
        return max([len(word) for word in self.tokens])

    def unique_word_freq(self):
        return float(self.fdist.B()) / self.fdist.N()

    def max_sentence_length(self):
        return max(self.__sentence_lengths())

    def min_sentence_length(self):
        return min(self.__sentence_lengths())


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
