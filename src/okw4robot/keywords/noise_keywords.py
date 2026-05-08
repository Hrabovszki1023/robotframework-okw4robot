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
