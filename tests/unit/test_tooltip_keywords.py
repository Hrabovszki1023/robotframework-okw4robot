"""Tests fuer tooltip_keywords.py mit MockWidget."""

import pytest
from .mock_widget import MockWidget
from .conftest import register_widget


class TestVerifyTooltip:
    def test_ok(self):
        w = MockWidget(tooltip="Open settings")
        register_widget("Icon", w)
        from okw4robot.keywords.tooltip_keywords import TooltipKeywords
        kw = TooltipKeywords()
        kw.verify_tooltip("Icon", "Open settings")

    def test_fail(self):
        w = MockWidget(tooltip="Close")
        register_widget("Icon", w)
        from okw4robot.keywords.tooltip_keywords import TooltipKeywords
        kw = TooltipKeywords()
        with pytest.raises(AssertionError):
            kw.verify_tooltip("Icon", "Open")

    def test_ignore(self):
        from okw4robot.keywords.tooltip_keywords import TooltipKeywords
        kw = TooltipKeywords()
        kw.verify_tooltip("Icon", "$IGNORE")


class TestVerifyTooltipWCM:
    def test_wcm(self):
        w = MockWidget(tooltip="Open the settings panel")
        register_widget("Icon", w)
        from okw4robot.keywords.tooltip_keywords import TooltipKeywords
        kw = TooltipKeywords()
        kw.verify_tooltip_wcm("Icon", "*settings*")


class TestVerifyTooltipREGX:
    def test_regx(self):
        w = MockWidget(tooltip="Error code: 500")
        register_widget("Msg", w)
        from okw4robot.keywords.tooltip_keywords import TooltipKeywords
        kw = TooltipKeywords()
        kw.verify_tooltip_regx("Msg", r"code:\s+\d+")
