from enum import Enum


class ExtractionSchemeValues(Enum):
    COLUMNNAME = 0
    DATATYPE = 1
    ISNULL = 2


class ExtractionSchemeNames(Enum):
    COLUMNNAME = 'Column name'
    DATATYPE = 'Data type'
    ISNULL = 'Is null'


class MonitorStatus(Enum):
    SUCCEEDED = 'SUCCEEDED'
    SUCCEEDED_ISSUE = 'SUCCEEDED_ISSUE'
    FAILED = 'FAILED'

    @classmethod
    def format(cls, value):
        if cls.SUCCEEDED.value == value:
            return 'Succeeded'
        elif cls.SUCCEEDED_ISSUE.value == value:
            return 'Succeeded with issue'
        elif cls.FAILED.value == value:
            return 'Failed'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SessionStatus(Enum):
    START = 'START'
    END = 'END'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SessionProgress(Enum):
    PREPROCESSING = 'PREPROCESSING'
    START = 'START'
    COMPLETE = 'COMPLETE'
    INPROGRESS = 'INPROGRESS'
    ERROR = 'ERROR'
    OTHER = 'OTHER'
    POSTROCESSING = 'POSTROCESSING'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class DatasetType(Enum):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    INTERMEDIATE = 'INTERMEDIATE'
    TEMPORARY = 'TEMPORARY'
    OTHER = 'OTHER'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class DatasetAccess(Enum):
    TABLE = 'TABLE'
    SQL = 'SQL'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ConnectionType(Enum):
    POSTGRES = 'PostgreSQL'
    AZURE = 'Azure SQL'
    AZURE_BLOB_STORAGE = 'Azure Blob Storage'
