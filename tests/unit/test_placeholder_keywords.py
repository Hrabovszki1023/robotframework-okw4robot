"""Tests fuer placeholder_keywords.py mit MockWidget."""

import pytest
from .mock_widget import MockWidget
from .conftest import register_widget


class TestVerifyPlaceholder:
    def test_ok(self):
        w = MockWidget(placeholder="Enter name...")
        register_widget("Input", w)
        from okw4robot.keywords.placeholder_keywords import PlaceholderKeywords
        kw = PlaceholderKeywords()
        kw.verify_placeholder("Input", "Enter name...")

    def test_fail(self):
        w = MockWidget(placeholder="Wrong")
        register_widget("Input", w)
        from okw4robot.keywords.placeholder_keywords import PlaceholderKeywords
        kw = PlaceholderKeywords()
        with pytest.raises(AssertionError):
            kw.verify_placeholder("Input", "Expected")

    def test_ignore(self):
        from okw4robot.keywords.placeholder_keywords import PlaceholderKeywords
        kw = PlaceholderKeywords()
        kw.verify_placeholder("Input", "$IGNORE")


class TestVerifyPlaceholderWCM:
    def test_wcm(self):
        w = MockWidget(placeholder="Search products...")
        register_widget("Search", w)
        from okw4robot.keywords.placeholder_keywords import PlaceholderKeywords
        kw = PlaceholderKeywords()
        kw.verify_placeholder_wcm("Search", "*products*")


class TestVerifyPlaceholderREGX:
    def test_regx(self):
        w = MockWidget(placeholder="Enter value (0-100)")
        register_widget("Input", w)
        from okw4robot.keywords.placeholder_keywords import PlaceholderKeywords
        kw = PlaceholderKeywords()
        kw.verify_placeholder_regx("Input", r"\d+-\d+")
