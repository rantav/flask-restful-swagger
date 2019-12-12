from flask_restful_swagger import swagger


def test_make_class_with_input_class():
    class TestClass:
        pass

    assert swagger.make_class(TestClass) == TestClass


def test_make_class_with_input_instance():
    class TestClass:
        pass

    test_class = TestClass()

    assert swagger.make_class(test_class) == TestClass


def test_make_class_with_none():
    assert isinstance(None, swagger.make_class(None))
