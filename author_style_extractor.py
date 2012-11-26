import nltk
from nltk.probability import FreqDist

class author_style_extractor:

    def __init__(self):
        self.tokens = []
        self.fdist = FreqDist()

    def add_text(self, text):
        tokens = nltk.word_tokenize(text)
        self.tokens += tokens
        for token in tokens:
            self.fdist.inc(token.lower())

    def word_freq(self):
        return self.fdist

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

if __name__ == "__main__":
    text1 = """Call me Ishmael.""" 
    text2 = """Some years ago, never mind how long precisely,
               having little or no money in my purse, and nothing
               particular to interest me on shore, I thought I
               would sail about a little and see the watery part
               of the world."""
    extr = author_style_extractor()
    extr.add_text(text1)
    extr.add_text(text2)
    print(extr.word_freq())
    print(extr.avg_word_length())
    print(extr.std_dev_word_length())
    print(extr.max_word_length())
    print(extr.unique_word_freq())