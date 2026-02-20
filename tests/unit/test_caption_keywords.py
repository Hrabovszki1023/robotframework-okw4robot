"""Tests fuer caption_keywords.py mit MockWidget."""

import pytest
from .mock_widget import MockWidget
from .conftest import register_widget


class TestVerifyCaption:
    def test_ok(self):
        w = MockWidget(text="Submit")
        register_widget("Btn", w)
        from okw4robot.keywords.caption_keywords import CaptionKeywords
        kw = CaptionKeywords()
        kw.verify_caption("Btn", "Submit")

    def test_fail(self):
        w = MockWidget(text="Cancel")
        register_widget("Btn", w)
        from okw4robot.keywords.caption_keywords import CaptionKeywords
        kw = CaptionKeywords()
        with pytest.raises(AssertionError):
            kw.verify_caption("Btn", "Submit")

    def test_ignore(self):
        from okw4robot.keywords.caption_keywords import CaptionKeywords
        kw = CaptionKeywords()
        kw.verify_caption("Btn", "$IGNORE")


class TestVerifyCaptionWCM:
    def test_wcm(self):
        w = MockWidget(text="Hello World!")
        register_widget("Lbl", w)
        from okw4robot.keywords.caption_keywords import CaptionKeywords
        kw = CaptionKeywords()
        kw.verify_caption_wcm("Lbl", "*World*")


class TestVerifyCaptionREGX:
    def test_regx(self):
        w = MockWidget(text="Error: 404")
        register_widget("Msg", w)
        from okw4robot.keywords.caption_keywords import CaptionKeywords
        kw = CaptionKeywords()
        kw.verify_caption_regx("Msg", r"Error:\s+\d+")


class TestLogCaption:
    def test_log(self):
        w = MockWidget(text="Test")
        register_widget("Lbl", w)
        from okw4robot.keywords.caption_keywords import CaptionKeywords
        kw = CaptionKeywords()
        kw.log_caption("Lbl")
        assert any(c[0] == "okw_get_text" for c in w.calls)


class TestMemorizeCaption:
    def test_memorize(self):
        w = MockWidget(text="stored")
        register_widget("Lbl", w)
        from okw4robot.keywords.caption_keywords import CaptionKeywords
        kw = CaptionKeywords()
        kw.memorize_caption("Lbl", "myCaption")
        assert any(c[0] == "okw_get_text" for c in w.calls)
