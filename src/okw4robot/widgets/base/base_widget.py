import inspect
from okw4robot.utils.logging_mixin import LoggingMixin
from robot.libraries.BuiltIn import BuiltIn

class BaseWidget(LoggingMixin):
    def __init__(self, adapter, locator, **options):
        self.adapter = adapter
        self.locator = locator
        self.options = options or {}

    def okw_click(self): raise NotImplementedError()
    def okw_double_click(self): raise NotImplementedError()
    def okw_set_value(self, value): raise NotImplementedError()
    def okw_select(self, value): raise NotImplementedError()
    def okw_type_key(self, key): raise NotImplementedError()
    def okw_verify_value(self, expected): raise NotImplementedError()
    def okw_verify_value_wcm(self, expected): raise NotImplementedError()
    def okw_verify_value_regex(self, expected): raise NotImplementedError()

    def okw_verify_exist(self):
        self.log_current_method()
        return self.adapter.element_exists(self.locator)

    def okw_log_value(self): raise NotImplementedError()
    def okw_has_value(self): raise NotImplementedError()
    def okw_memorize_value(self): raise NotImplementedError()

    # === List-like counts (to be implemented by list-like widgets) ===
    def okw_get_list_count(self) -> int:
        raise NotImplementedError()

    def okw_get_selected_count(self) -> int:
        raise NotImplementedError()

    # === Sync helpers ===
    def _get_global_sync(self, intent: str) -> dict:
        bi = BuiltIn()
        timeout = bi.get_variable_value('${OKW_SYNC_TIMEOUT_WRITE}' if intent=='write' else '${OKW_SYNC_TIMEOUT_READ}', default=10)
        poll = bi.get_variable_value('${OKW_SYNC_POLL}', default=0.1)
        scroll_def = bi.get_variable_value('${OKW_SYNC_SCROLL_INTO_VIEW}', default='YES')
        editable_def = bi.get_variable_value('${OKW_SYNC_CHECK_EDITABLE}', default='YES')
        busy = bi.get_variable_value('${OKW_BUSY_SELECTORS_WRITE}' if intent=='write' else '${OKW_BUSY_SELECTORS_READ}', default=None)
        busy_list = []
        if busy:
            if isinstance(busy, (list, tuple)):
                busy_list = list(busy)
            else:
                busy_list = [v.strip() for v in str(busy).split(',') if v.strip()]
        return {
            'timeout': float(timeout) if isinstance(timeout,(int,float)) else bi.convert_time(str(timeout)),
            'poll': float(poll) if isinstance(poll,(int,float)) else bi.convert_time(str(poll)),
            'exists': True,
            'visible': True,
            'enabled': True,
            # Require 'editable' only for true text inputs; native selects (ComboBox) sind nicht 'editable' im Sinne von tippen
            'editable': (self.__class__.__name__ in ('TextField','MultilineField')) and str(editable_def).strip().upper() in ('YES','TRUE','1') if intent=='write' else False,
            'scroll_into_view': str(scroll_def).strip().upper() in ('YES','TRUE','1') if intent=='write' else False,
            'until_not_visible': busy_list,
        }

    def _merge_wait(self, intent: str) -> dict:
        cfg = self._get_global_sync(intent)
        # Instance overrides from YAML extras
        inst = (self.options.get('wait') or {}).get(intent, {})
        for k,v in inst.items():
            cfg[k] = v
        return cfg

    def _wait_before(self, intent: str):
        cfg = self._merge_wait(intent)
        timeout = float(cfg.get('timeout', 10))
        poll = float(cfg.get('poll', 0.1))
        import time
        end = time.time() + timeout
        has_locator = bool(self.locator)

        if has_locator:
            # 1) exists
            if cfg.get('exists', True):
                ok = False
                while time.time() < end:
                    if self.adapter.element_exists(self.locator):
                        ok = True; break
                    time.sleep(poll)
                if not ok:
                    raise AssertionError('[Sync] Element does not exist')

            # 2) scroll into view
            if cfg.get('scroll_into_view', False):
                try:
                    self.adapter.scroll_into_view(self.locator)
                except Exception:
                    pass

            # 3) visible
            if cfg.get('visible', True):
                try:
                    self.adapter.wait_until_visible(self.locator, timeout=timeout)
                except Exception:
                    raise AssertionError('[Sync] Element not visible')

            # 4) enabled
            if cfg.get('enabled', True):
                ok = False
                while time.time() < end:
                    if getattr(self.adapter,'is_enabled',None) and self.adapter.is_enabled(self.locator):
                        ok = True; break
                    time.sleep(poll)
                if not ok:
                    raise AssertionError('[Sync] Element not enabled')

            # 5) editable
            if cfg.get('editable', False):
                ok = False
                while time.time() < end:
                    if getattr(self.adapter,'is_editable',None) and self.adapter.is_editable(self.locator):
                        ok = True; break
                    time.sleep(poll)
                if not ok:
                    raise AssertionError('[Sync] Element not editable')

        # 6) project waits (until_not_visible)
        for sel in cfg.get('until_not_visible', []) or []:
            try:
                # Accept raw locator string (css:...), dict, or css selector
                loc = sel if isinstance(sel,(str,dict)) else str(sel)
                if isinstance(loc,str) and ':' not in loc:
                    loc = {'css': loc}
                self.adapter.wait_until_not_visible(loc, timeout=timeout)
            except Exception:
                # if not found; treat as passed
                pass
