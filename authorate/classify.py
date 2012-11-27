import os
from sklearn.externals import joblib
from authorate.model import get_session, Path
import textwrap


class Classifier(object):
    def classify(self, snippet):
        """Return the author_id of the author that writes most like the given
        snippet."""
        return 1

    def save(self, filename):
        joblib.dump(self, filename)

    @classmethod
    def load(cls, filepath):
        return joblib.load(filepath)

    def __str__(self):
        return "<({cls_name})>".format(cls_name=self.__class__.__name__)


class NaiveBayes(Classifier):
    def classify(self, snippet):
        return 1

classifier_types = [NaiveBayes]
CLASSIFIERS_DIR = 'classifiers'


def classifer_path(cls_type):
    return os.path.join(CLASSIFIERS_DIR, cls_type.__name__ + '.model')


def create_classifier_dir():
    if not os.path.exists(CLASSIFIERS_DIR):
        os.mkdir(CLASSIFIERS_DIR)


def classify_all(engine, snippet):
    session = get_session(engine)
    formated_snippet = textwrap.fill(snippet, initial_indent=">   ")
    print("Classifying snippet: \n\n{snippet}\n".format(
        snippet=formated_snippet))
    for classifier_type in classifier_types:
        #classifier = classifier_type.load(classifier_path(cls_type))
        #author_id = classifier.classify(snippet)
        classifier = NaiveBayes()
        print("Classifier: {classifier}".format(classifier=classifier))
        print("    Answer: {author}\n".format(author="Derp"))
