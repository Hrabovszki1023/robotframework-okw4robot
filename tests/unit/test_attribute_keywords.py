"""Tests fuer attribute_keywords.py mit MockWidget."""

import pytest
from .mock_widget import MockWidget
from .conftest import register_widget


class TestVerifyAttribute:
    def test_verify_ok(self):
        w = MockWidget(attributes={"title": "Hello"})
        register_widget("Elem", w)
        from okw4robot.keywords.attribute_keywords import AttributeKeywords
        kw = AttributeKeywords()
        kw.verify_attribute("Elem", "title", "Hello")

    def test_verify_fail(self):
        w = MockWidget(attributes={"title": "Wrong"})
        register_widget("Elem", w)
        from okw4robot.keywords.attribute_keywords import AttributeKeywords
        kw = AttributeKeywords()
        with pytest.raises(AssertionError):
            kw.verify_attribute("Elem", "title", "Expected")

    def test_verify_ignore(self):
        from okw4robot.keywords.attribute_keywords import AttributeKeywords
        kw = AttributeKeywords()
        kw.verify_attribute("Elem", "title", "$IGNORE")


class TestVerifyAttributeWCM:
    def test_wcm_ok(self):
        w = MockWidget(attributes={"href": "https://example.com/page"})
        register_widget("Link", w)
        from okw4robot.keywords.attribute_keywords import AttributeKeywords
        kw = AttributeKeywords()
        kw.verify_attribute_wcm("Link", "href", "*example*")


class TestVerifyAttributeREGX:
    def test_regx_ok(self):
        w = MockWidget(attributes={"class": "btn btn-primary"})
        register_widget("Btn", w)
        from okw4robot.keywords.attribute_keywords import AttributeKeywords
        kw = AttributeKeywords()
        kw.verify_attribute_regx("Btn", "class", r"btn.*primary")


class TestLogAttribute:
    def test_log(self):
        w = MockWidget(attributes={"data-id": "42"})
        register_widget("Elem", w)
        from okw4robot.keywords.attribute_keywords import AttributeKeywords
        kw = AttributeKeywords()
        kw.log_attribute("Elem", "data-id")
        assert any(c[0] == "okw_get_attribute" for c in w.calls)


class TestMemorizeAttribute:
    def test_memorize(self):
        w = MockWidget(attributes={"value": "saved"})
        register_widget("Elem", w)
        from okw4robot.keywords.attribute_keywords import AttributeKeywords
        kw = AttributeKeywords()
        kw.memorize_attribute("Elem", "value", "myAttr")
        assert any(c[0] == "okw_get_attribute" for c in w.calls)
