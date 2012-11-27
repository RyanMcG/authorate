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

CLASSIFIERS_DIR = 'classifiers'


def classifer_path(cls_type):
    return os.path.join(CLASSIFIERS_DIR, cls_type.__name__ + '.pkl')


def create_classifier_dir():
    if not os.path.exists(CLASSIFIERS_DIR):
        os.mkdir(CLASSIFIERS_DIR)


def save_classifier(classifier):
    create_classifier_dir()
    joblib.dump(classifier, classifer_path(classifier.__class__))


def load_classifier(ClsType):
    return joblib.load(classifer_path(ClsType))


classifier_types = [SVC, GaussianNB]


def classify_all(engine, snippet):
    session = get_session(engine)

    indent = '>   '
    formated_snippet = textwrap.fill(snippet, initial_indent=indent,
                                     subsequent_indent=indent)
    print("Classifying snippet: \n\n{snippet}\n".format(
        snippet=formated_snippet))

    for ClsType in classifier_types:
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
    for ClsType in classifier_types:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            classifier = load_classifier(ClsType)

        shuffle_iter = cross_validation.ShuffleSplit(len(data),
                                                     n_iterations=10,
                                                     test_size=0.4)
        cv_result = cross_validation.cross_val_score(classifier, data, targets,
                                                     cv=shuffle_iter)
        answer = "average={0} std={1}".format(numpy.average(cv_result),
                                              numpy.std(cv_result))

        print("Classifier: {classifier}\n".format(classifier=classifier))
        print("==> CV Result: {answer}\n".format(answer=answer))
