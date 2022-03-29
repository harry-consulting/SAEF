from __future__ import absolute_import, unicode_literals
import abc


class Analyzer:
    def __init__(self):
        self._result = [("analyzer", __name__)]

    @abc.abstractmethod
    def _execute_session(self):
        pass

    def execute(self):
        return self._execute_session()
