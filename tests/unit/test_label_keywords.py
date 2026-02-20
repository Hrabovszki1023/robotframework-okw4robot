"""Tests fuer label_keywords.py mit MockWidget."""

import pytest
from .mock_widget import MockWidget
from .conftest import register_widget


class TestVerifyLabel:
    def test_ok(self):
        w = MockWidget(label="Username")
        register_widget("Input", w)
        from okw4robot.keywords.label_keywords import LabelKeywords
        kw = LabelKeywords()
        kw.verify_label("Input", "Username")

    def test_fail(self):
        w = MockWidget(label="Password")
        register_widget("Input", w)
        from okw4robot.keywords.label_keywords import LabelKeywords
        kw = LabelKeywords()
        with pytest.raises(AssertionError):
            kw.verify_label("Input", "Username")

    def test_ignore(self):
        from okw4robot.keywords.label_keywords import LabelKeywords
        kw = LabelKeywords()
        kw.verify_label("Input", "$IGNORE")


class TestVerifyLabelWCM:
    def test_wcm(self):
        w = MockWidget(label="User Name Field")
        register_widget("Input", w)
        from okw4robot.keywords.label_keywords import LabelKeywords
        kw = LabelKeywords()
        kw.verify_label_wcm("Input", "User*")


class TestVerifyLabelREGX:
    def test_regx(self):
        w = MockWidget(label="Field #42")
        register_widget("Input", w)
        from okw4robot.keywords.label_keywords import LabelKeywords
        kw = LabelKeywords()
        kw.verify_label_regx("Input", r"Field\s+#\d+")
