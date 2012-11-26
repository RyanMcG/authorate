import nltk
from nltk.probability import FreqDist

class text_feature_extractor:

    def __init__(self, tokens):
        self.tokens = tokens
        self.count = len(tokens)
        self.uniq_count = len(set(tokens))

    def _normalize_dist(self, fdist):
    	dist = dict()
    	for token_freq in fdist.iteritems():
    		dist[token_freq[0]] = float(token_freq[1]) / fdist.N()
    	return dist

    def word_freq(self):
    	fdist = FreqDist(word.lower() for word in self.tokens)
    	return self._normalize_dist(fdist)

    def avg_word_length(self):
    	return sum([len(word) for word in self.tokens]) / float(self.count)

    def max_word_length(self):
    	return max([len(word) for word in self.tokens])

    def unique_word_freq(self):
    	return float(self.uniq_count) / self.count

if __name__ == "__main__":
    text = """Call me Ishmael. Some years ago-never mind how long
    		  precisely-having little or no money in my purse, and
    		  nothing particular to interest me on shore, I thought
    		  I would sail about a little and see the watery part
    		  of the world."""
    tokens = nltk.word_tokenize(text)
    extr = text_feature_extractor(tokens)
    print(extr.word_freq())
    print(extr.avg_word_length())
    print(extr.max_word_length())
    print(extr.unique_word_freq())