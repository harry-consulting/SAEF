from __future__ import absolute_import, unicode_literals
import abc
class Analyzer:
    """
        The super class for all Analyzers,
        such as ColumnAnalyzer, DatasetAnalyzer
        JobAnalyzer, ApplicationAnalyzer
        Sub class must extend the abstract methods to implement the analyzer detail. 
        0. validate input
        1. start and stop session
        2. execution session

        The method execute is controlling the usage of the four abstract method
        Only override execute() if you want to modify the behavior of a specific analyzer
    """

    def __init__(self):
        self._result = [("analyzer", __name__)]

    @abc.abstractmethod
    def _execute_session(self):
        pass

    def execute(self):
        return self._execute_session()
