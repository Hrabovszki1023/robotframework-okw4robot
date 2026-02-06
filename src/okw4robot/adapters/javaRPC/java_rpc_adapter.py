# src/okw4robot/adapters/javaRPC/JavaRpcAdapter.py

import json
import requests
from okw4robot.utils.logging_mixin import LoggingMixin

class JavaRpcAdapter(LoggingMixin):
    def __init__(self, host="localhost", port=8080, **kwargs):
        self.host = host
        self.port = port
        self.endpoint = f"http://{host}:{port}/jsonrpc"
        self.session = requests.Session()
        self.log_info(f"Verbinde zu JSON-RPC Endpoint: {self.endpoint}")


    def _rpc_call(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        response = self.session.post(self.endpoint, json=payload)
        if not response.ok:
            raise RuntimeError(f"RPC Error: {response.status_code} {response.text}")
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"RPC Error: {data['error']}")
        return data.get("result")

    def maximize_window(self):
        self.log_info("Maximiere Fenster")
        self._rpc_call("maximizeWindow")

    def input_text(self, locator, value):
        self.log_info(f"Text eingeben in {locator}: {value}")
        self._rpc_call("inputText", {"locator": locator, "value": value})

    def click(self, locator):
        self.log_info(f"Klicke auf {locator}")
        self._rpc_call("click", {"locator": locator})

    def get_text(self, locator):
        self.log_info(f"Hole Text von {locator}")
        return self._rpc_call("getText", {"locator": locator})

    def element_exists(self, locator):
        self.log_info(f"Prüfe Existenz von {locator}")
        return self._rpc_call("elementExists", {"locator": locator})

    def list_actions(self, node_id):
        """
        Holt die verfügbaren Actions für eine Node-ID vom JSON-RPC-Server (proxyt Agent /actions).
        """
        self.log_info(f"Liste Actions für Node {node_id}")
        return self._rpc_call("listActions", {"id": node_id})

    def call_action(self, node_id, action, args=None):
        """
        Führt eine Action für eine Node-ID aus (proxyt Agent /action).
        """
        self.log_info(f"Rufe Action {action} auf Node {node_id} mit args={args}")
        return self._rpc_call("callAction", {"id": node_id, "action": action, "args": args or []})

    def get_object_tree(self) -> dict:
        """
        Fragt die GUI-Objektstruktur vom Java-RPC-Server ab
        und gibt sie als Python-Dictionary zurück.
        """
        self.log_info("Frage Objektstruktur vom Java-RPC-Server ab...")

        payload = {
            "jsonrpc": "2.0",
            "method": "getObjectTree",
            "id": 1
        }

        try:
            response = self.session.post(
                self.endpoint,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            self.log_error(f"Fehler beim RPC-Request: {e}")
            raise

        try:
            outer = response.json()
            raw_result = outer.get("result", "{}")
            result = json.loads(raw_result)
            self.log_info("Objektstruktur erfolgreich empfangen.")
            return result
        except Exception as e:
            self.log_error(f"Fehler beim Parsen der Antwort: {e}")
            raise
