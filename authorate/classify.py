import os
import sys
from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.lda import LDA
from sklearn import cross_validation
from sklearn import preprocessing
from authorate.model import get_session, Path
from authorate.text_features import text_to_vector
from sqlalchemy.exc import InterfaceError
import numpy
import textwrap
import warnings
import re

classifiers_dir = 'classifiers'


def clean_classifier_dir():
    """Clean out the classifiers directory."""
    import shutil
    root, dirs, files = os.walk(classifiers_dir).next()
    for f in files:
        os.remove(os.path.join(root, f))
    for d in dirs:
        shutil.rmtree(os.path.join(root, d))


def classifer_path(classifier):
    """Return a unique filepath to save the given classifier at."""
    return os.path.join(classifiers_dir, classifier.__class__.__name__ + '-' +
                        str(hash(classifier)) + '.pkl')


def create_classifier_dir():
    if not os.path.exists(classifiers_dir):
        os.mkdir(classifiers_dir)


def save_classifier(classifier):
    create_classifier_dir()
    joblib.dump(classifier, classifer_path(classifier))


def create_and_save_scaler(data):
    """Create a scaler for the given data and save it to the disk."""
    scaler = preprocessing.Scaler().fit(data)
    create_classifier_dir()
    joblib.dump(scaler, os.path.join(classifiers_dir,
                                     scaler.__class__.__name__ + '.pkl'))
    return scaler


def load_scaler(root, files):
    """Attempt to load a fitted scaler instance if it exists in files."""
    if 'Scaler.pkl' in files:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            scaler = joblib.load(os.path.join(root, 'Scaler.pkl'))
    else:
        print("ERROR: Scaler class could not be found.")
        sys.exit(9)
    return scaler

# A list of tules where the first element of each tuple is a classifier and the
# second is a map of keyword arguments used to construct that classifier.
classifier_types = [(SVC, {}),
                    (LinearSVC, {}),
                    (GaussianNB, {}),
                    (RandomForestClassifier, {}),
                    (DecisionTreeClassifier, {}),
                    (LDA, {})]


def classify_all(engine, snippet):
    session = get_session(engine)

    indent = '>   '
    formated_snippet = textwrap.fill(snippet, initial_indent=indent,
                                     subsequent_indent=indent)
    print("Classifying snippet: \n\n{snippet}\n".format(
        snippet=formated_snippet))

    root, _, files = os.walk(classifiers_dir).next()
    scaler = load_scaler(root, files)
    files.sort()

    for classifier_path in filter(CLASSIFIER_REGEX.match, files):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            classifier = joblib.load(os.path.join(root, classifier_path))
            prediction = classifier.predict(
                scaler.transform([text_to_vector(snippet)]))
        try:
            path = session.query(Path).filter_by(id=prediction[0]).first()
            answer = path.name
        except InterfaceError:
            pass

        print("Classifier: {classifier}\n".format(classifier=classifier))
        print("--> Answer: {answer}\n".format(answer=answer))


CLASSIFIER_REGEX = re.compile('^.*-\d+\.pkl$')


def test_all(engine, data, targets):
    best_avg = 0.0
    winner = None
    root, _, files = os.walk(classifiers_dir).next()
    scaler = load_scaler(root, files)
    files.sort()
    scaled_data = scaler.transform(data)

    for classifier_path in filter(CLASSIFIER_REGEX.match, files):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            classifier = joblib.load(os.path.join(root, classifier_path))

        shuffle_iter = cross_validation.ShuffleSplit(len(data),
                                                     n_iterations=10,
                                                     test_size=0.4)

        cv_result = cross_validation.cross_val_score(classifier, scaled_data,
                                                     targets, cv=shuffle_iter)
        avg = numpy.average(cv_result)

        if avg >= best_avg:
            best_avg = avg
            winner = classifier

        answer = "average={0} std={1}".format(numpy.average(cv_result),
                                              numpy.std(cv_result))

        print("Classifier: {classifier}\n".format(classifier=classifier))
        print("==> CV Result: {answer}\n\n".format(answer=answer))

    print("*** The best classifier is {classifier} ***".format(classifier=winner))
