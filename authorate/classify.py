import os
from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn import cross_validation
from authorate.model import get_session, Path
from authorate.text_features import text_to_vector
from sqlalchemy.exc import InterfaceError
import numpy
import textwrap
import warnings

classifiers_dir = 'classifiers'


def classifer_path(cls_type):
    return os.path.join(classifiers_dir, cls_type.__name__ + '.pkl')


def create_classifier_dir():
    if not os.path.exists(classifiers_dir):
        os.mkdir(classifiers_dir)


def save_classifier(classifier):
    create_classifier_dir()
    joblib.dump(classifier, classifer_path(classifier.__class__))


def load_classifier(ClsType):
    return joblib.load(classifer_path(ClsType))


# A list of tules where the first element of each tuple is a classifier and the
# second is a map of keyword arguments used to construct that classifier.
classifier_types = [(SVC, {}), (GaussianNB, {})]


def classify_all(engine, snippet):
    session = get_session(engine)

    indent = '>   '
    formated_snippet = textwrap.fill(snippet, initial_indent=indent,
                                     subsequent_indent=indent)
    print("Classifying snippet: \n\n{snippet}\n".format(
        snippet=formated_snippet))

    for (ClsType, kwargs) in classifier_types:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            classifier = load_classifier(ClsType)

        prediction = classifier.predict([text_to_vector(snippet)])
        try:
            path = session.query(Path).filter_by(id=prediction[0]).first()
            answer = path.name
        except InterfaceError:
            pass

        print("Classifier: {classifier}\n".format(classifier=classifier))
        print("--> Answer: {answer}\n".format(answer=answer))


def test_all(engine, data, targets):
    best_avg = 0.0
    winner = None
    for (ClsType, kwargs) in classifier_types:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            classifier = load_classifier(ClsType)

        shuffle_iter = cross_validation.ShuffleSplit(len(data),
                                                     n_iterations=10,
                                                     test_size=0.4)
        cv_result = cross_validation.cross_val_score(classifier, data, targets,
                                                     cv=shuffle_iter)
        avg = numpy.average(cv_result)

        if avg >= best_avg:
            best_avg = avg
            winner = classifier

        answer = "average={0} std={1}".format(numpy.average(cv_result),
                                              numpy.std(cv_result))

        print("Classifier: {classifier}\n".format(classifier=classifier))
        print("==> CV Result: {answer}\n".format(answer=answer))

    print("*** The best classifier is {classifier} ***".format(classifier=winner))
