"""Tests fuer widget_keywords.py mit MockWidget.

Prueft dass Keywords korrekt an okw_* Methoden delegieren.
"""

import pytest
from .mock_widget import MockWidget
from .conftest import register_widget


class TestClickOn:
    def test_click_delegates(self):
        w = MockWidget()
        register_widget("Btn", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.click_on("Btn")
        assert ("okw_click",) == w.calls[0][:1]


class TestDoubleClickOn:
    def test_double_click_delegates(self):
        w = MockWidget()
        register_widget("Btn", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.double_click_on("Btn")
        assert ("okw_double_click",) == w.calls[0][:1]


class TestSetValue:
    def test_set_value_delegates(self):
        w = MockWidget()
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.set_value("Input", "Hello")
        assert ("okw_set_value", ("Hello",)) == w.calls[0]

    def test_set_value_ignore(self):
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.set_value("Input", "$IGNORE")  # should not raise

    def test_set_value_empty_token(self):
        w = MockWidget()
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.set_value("Input", "$EMPTY")
        assert ("okw_set_value", ("",)) == w.calls[0]

    def test_set_value_delete_passes_through(self):
        """SetValue hat kein $DELETE-Handling -- wird als normaler Wert durchgereicht."""
        w = MockWidget()
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.set_value("Input", "$DELETE")
        # $DELETE wird als normaler Wert an okw_set_value durchgereicht
        assert ("okw_set_value", ("$DELETE",)) == w.calls[0]


class TestSelect:
    def test_select_delegates(self):
        w = MockWidget()
        register_widget("Combo", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.select("Combo", "Option1")
        assert ("okw_select", ("Option1",)) == w.calls[0]


class TestTypeKey:
    def test_type_key_delegates(self):
        w = MockWidget()
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.type_key("Input", "TAB")
        assert ("okw_type_key", ("TAB",)) == w.calls[0]

    def test_type_key_delete(self):
        w = MockWidget(value="old")
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.type_key("Input", "$DELETE")
        assert ("okw_delete",) == w.calls[0][:1]


class TestVerifyValue:
    def test_verify_value_ok(self):
        w = MockWidget(value="Hello")
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_value("Input", "Hello")  # should not raise

    def test_verify_value_fail(self):
        w = MockWidget(value="Wrong")
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        with pytest.raises(AssertionError):
            kw.verify_value("Input", "Expected")

    def test_verify_value_ignore(self):
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_value("Input", "$IGNORE")  # should not raise


class TestVerifyExist:
    def test_verify_exist_yes(self):
        w = MockWidget(exists=True)
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_exist("Elem", "YES")  # should not raise

    def test_verify_exist_no(self):
        w = MockWidget(exists=False)
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_exist("Elem", "NO")  # should not raise

    def test_verify_exist_fail(self):
        w = MockWidget(exists=False)
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        with pytest.raises(AssertionError):
            kw.verify_exist("Elem", "YES")


class TestSetFocus:
    def test_set_focus_delegates(self):
        w = MockWidget()
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.set_focus("Input")
        assert ("okw_set_focus",) == w.calls[0][:1]


class TestVerifyHasFocus:
    def test_has_focus_yes(self):
        w = MockWidget(has_focus=True)
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_has_focus("Input", "YES")

    def test_has_focus_fail(self):
        w = MockWidget(has_focus=False)
        register_widget("Input", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        with pytest.raises(AssertionError):
            kw.verify_has_focus("Input", "YES")


class TestVerifyVisible:
    def test_visible_yes(self):
        w = MockWidget(visible=True)
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_visible("Elem", "YES")

    def test_visible_no(self):
        w = MockWidget(visible=False)
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_visible("Elem", "NO")


class TestVerifyEnabled:
    def test_enabled_yes(self):
        w = MockWidget(enabled=True)
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.verify_enabled("Elem", "YES")

    def test_enabled_fail(self):
        w = MockWidget(enabled=False)
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        with pytest.raises(AssertionError):
            kw.verify_enabled("Elem", "YES")


class TestLogValue:
    def test_log_value_delegates(self):
        w = MockWidget(value="TestVal")
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.log_value("Elem")
        assert any(c[0] == "okw_get_value" for c in w.calls)


class TestMemorizeValue:
    def test_memorize_value(self):
        w = MockWidget(value="stored")
        register_widget("Elem", w)
        from okw4robot.keywords.widget_keywords import WidgetKeywords
        kw = WidgetKeywords()
        kw.memorize_value("Elem", "myVar")
        assert any(c[0] == "okw_get_value" for c in w.calls)
