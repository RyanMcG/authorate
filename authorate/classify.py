import os
from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVM
from authorate.model import get_session, Path
from authorate.text_features import text_to_vector
import textwrap


CLASSIFIERS_DIR = 'classifiers'


def classifer_path(cls_type):
    return os.path.join(CLASSIFIERS_DIR, cls_type.__name__ + '.model')


def create_classifier_dir():
    if not os.path.exists(CLASSIFIERS_DIR):
        os.mkdir(CLASSIFIERS_DIR)


def save_classifier(classifier):
    joblib.dump(classifier, classifer_path(classifier.__class__))


def load_classifier(ClsType):
    return joblib.load(classifer_path(ClsType))


classifier_types = [SVM, GaussianNB]


def classify_all(engine, snippet):
    session = get_session(engine)
    formated_snippet = textwrap.fill(snippet, initial_indent=">   ")
    print("Classifying snippet: \n\n{snippet}\n".format(
        snippet=formated_snippet))
    for ClsType in classifier_types:
        prediction = load_classifier(ClsType).predict([text_to_vector(snippet)])
        print(prediction[0])
        print("Classifier: {classifier}".format(classifier=classifier))
        print("    Answer: {author}\n".format(author="Derp"))
