from enum import Enum

class Column(Enum):
    TYPE = 0
    NULLABLE = 1
    ORDER = 2
    

class AnalyzerTask(Enum):
    ANALYZE_DATASET = 'ANALYZE DATASET'
    ANALYZE_JOB = 'ANALYZE JOB'
    ANALYZE_APPLICATION = 'ANALYZE APPLICATION'
    ANALYZE_DATASET_HISTORY = 'ANALYZE DATASET HISTORY'
    ANALYZE_JOB_HISTORY = 'ANALYZE JOB HISTORY'
    ANALYZE_APPLICATION_HISTORY = 'ANALYZE APPLICATION HISTORY'
    EXTERNAL = 'EXTERNAL'
    
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
