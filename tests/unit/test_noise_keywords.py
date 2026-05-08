"""Tests fuer OnFailNOISE Keyword.

Prueft die NOISE-Klassifizierung bei Fehlern in Vorbereitungsphasen.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def builtin_mock():
    """Patcht BuiltIn() in noise_keywords, so dass kein RF-Server noetig ist."""
    mock = MagicMock()
    with patch("okw4robot.keywords.noise_keywords.BuiltIn", return_value=mock):
        yield mock


@pytest.fixture
def kw(builtin_mock):
    from okw4robot.keywords.noise_keywords import NoiseKeywords
    return NoiseKeywords()


class TestOnFailNoiseKlassifizierung:

    def test_fehler_wird_als_noise_klassifiziert(self, kw, builtin_mock):
        builtin_mock.run_keyword.side_effect = AssertionError("Fenster nicht gefunden")

        with pytest.raises(AssertionError, match=r"^\[N\]"):
            kw.on_fail_noise("SelectWindow", "Hauptfenster")

    def test_originale_fehlermeldung_bleibt_erhalten(self, kw, builtin_mock):
        builtin_mock.run_keyword.side_effect = AssertionError("Fenster 'Hauptfenster' nicht gefunden")

        with pytest.raises(AssertionError, match=r"\[N\] Fenster 'Hauptfenster' nicht gefunden"):
            kw.on_fail_noise("SelectWindow", "Hauptfenster")

    def test_noise_tag_wird_gesetzt(self, kw, builtin_mock):
        builtin_mock.run_keyword.side_effect = AssertionError("Fehler")

        with pytest.raises(AssertionError):
            kw.on_fail_noise("SelectWindow", "Hauptfenster")

        builtin_mock.set_tags.assert_called_once_with("NOISE")

    def test_runtime_error_wird_auch_als_noise_klassifiziert(self, kw, builtin_mock):
        builtin_mock.run_keyword.side_effect = RuntimeError("Adapter nicht verfuegbar")

        with pytest.raises(AssertionError, match=r"^\[N\] Adapter nicht verfuegbar"):
            kw.on_fail_noise("StartApp", "MeineApp")


class TestOnFailNoiseErfolgsfall:

    def test_kein_effekt_bei_erfolgreichem_keyword(self, kw, builtin_mock):
        kw.on_fail_noise("Log", "Alles OK")

        builtin_mock.run_keyword.assert_called_once_with("Log", "Alles OK")
        builtin_mock.set_tags.assert_not_called()


class TestOnFailNoiseParameterweitergabe:

    def test_keyword_ohne_parameter(self, kw, builtin_mock):
        kw.on_fail_noise("ResetApp")
        builtin_mock.run_keyword.assert_called_once_with("ResetApp")

    def test_keyword_mit_einem_parameter(self, kw, builtin_mock):
        kw.on_fail_noise("SelectWindow", "Hauptfenster")
        builtin_mock.run_keyword.assert_called_once_with("SelectWindow", "Hauptfenster")

    def test_keyword_mit_mehreren_parametern(self, kw, builtin_mock):
        kw.on_fail_noise("SetValue", "Benutzer", "admin")
        builtin_mock.run_keyword.assert_called_once_with("SetValue", "Benutzer", "admin")
