from flask_restful_swagger import swagger


def test_make_class_with_input_class():
    class A:
        pass

    assert swagger.make_class(A) == A


def test_make_class_with_input_instance():
    class A:
        pass
    a = A()

    assert swagger.make_class(a) == A


def test_make_class_with_None():
    assert isinstance(None, swagger.make_class(None))




