from flask_restful_swagger import swagger


class MockBasicObject:
    pass


def test_parse_doc_no_object_is_none():
    assert swagger._parse_doc(None) == (None, None)


def test_parse_doc_no_docs_is_none():
    assert swagger._parse_doc(MockBasicObject()) == (None, None)


def test_parse_doc_one_line_doc():
    test_one_line_doc = MockBasicObject()
    test_one_line_doc.__doc__ = "Some Text Goes Here"
    assert swagger._parse_doc(test_one_line_doc) == (
        "Some Text Goes Here",
        None,
    )


def test_parse_doc_multi_line_doc():
    test_multi_line_doc = MockBasicObject()
    test_multi_line_doc.__doc__ = (
        "Some Text Goes Here \n this is the extra text\n"
        "and this is the third line."
    )
    extracted = swagger._parse_doc(test_multi_line_doc)
    assert extracted[0] == "Some Text Goes Here "
    assert (
        extracted[1]
        == " this is the extra text<br/>and this is the third line."
    )


def test_parse_doc_weird_characters():
    test_weird_characters = MockBasicObject()
    test_weird_characters.__doc__ = (
        "Hi, 297agiu(*#&_$ ! \n Oh, the terrible 2908*&%)(#%#"
    )
    extracted = swagger._parse_doc(test_weird_characters)
    assert extracted[0] == "Hi, 297agiu(*#&_$ ! "
    assert extracted[1] == "Oh, the terrible 2908*&%)(#%#"


def test_parse_doc_ends_with_newline():
    test_ends_newline = MockBasicObject()
    test_ends_newline.__doc__ = "Overview \n Some details \n"
    assert swagger._parse_doc(test_ends_newline)[1] == "Some details "
