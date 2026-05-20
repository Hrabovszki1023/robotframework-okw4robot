from __future__ import annotations

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

from ..utils.logging_mixin import LoggingMixin


class NoiseKeywords(LoggingMixin):

    @keyword("OnFailNOISE")
    def on_fail_noise(self, keyword_name: str, *args):
        """Wraps a keyword call — on failure, re-raises with ``[N]`` prefix.

        Use this for preparation phases (Reset, Environment Setup, Navigation).
        Failures in these phases are classified as NOISE, not as SUT defects.

        Arguments:
        - ``keyword_name``: Name of the keyword to execute.
        - ``*args``: Arguments passed through to the wrapped keyword.

        Examples:
        | OnFailNOISE | SelectWindow | Hauptfenster |
        | OnFailNOISE | SetValue     | Benutzer     | admin |
        | OnFailNOISE | ResetApp     |              |       |

        Fail message on error:
        | FAIL: [N] SelectWindow fehlgeschlagen: Fenster 'Hauptfenster' nicht gefunden |
        """
        self.log_info(f"OnFailNOISE: {keyword_name} {' '.join(str(a) for a in args)}")
        try:
            BuiltIn().run_keyword(keyword_name, *args)
        except Exception as e:
            BuiltIn().set_tags("NOISE")
            raise AssertionError(f"[N] {e}")

    @keyword("OnFailIgnoreNOISE")
    def on_fail_ignore_noise(self, keyword_name: str, *args):
        """Wraps a keyword call — on failure, logs the error as NOISE and continues.

        Use this for optional preparation steps (e.g., dismissing a cookie banner)
        that may or may not be needed. If the keyword fails, the failure is logged
        as NOISE but the test continues.

        Arguments:
        - ``keyword_name``: Name of the keyword to execute.
        - ``*args``: Arguments passed through to the wrapped keyword.

        Examples:
        | OnFailIgnoreNOISE | ClickOn | CookieAblehnen |
        | OnFailIgnoreNOISE | ClickOn | WerbungSchliessen |

        On success: keyword executes normally.
        On failure: logs ``[N][IGNORED]`` message, test continues.
        """
        self.log_info(f"OnFailIgnoreNOISE: {keyword_name} {' '.join(str(a) for a in args)}")
        try:
            BuiltIn().run_keyword(keyword_name, *args)
        except Exception as e:
            self.log_info(f"[N][IGNORED] {keyword_name}: {e}")
