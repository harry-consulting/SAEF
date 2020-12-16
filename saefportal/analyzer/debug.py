from __future__ import absolute_import, unicode_literals

from tasks import analyze_dataset

def debug():
    """
        debug the analyze_dataset function
    """
    dataset_key = "04d0e89e-b70d-4689-9d40-f0e8fbc16811"
    application_token = "6d8322d7-b79d-4bb3-a222-7012b22059a1"
    execution_mode = "Development"
    session_key = "session 1"
    
    result = analyze_dataset( \
        dataset_key = dataset_key, \
        application_token=application_token, \
        execution_mode=execution_mode, \
        session_key=session_key\
        )
    print(result)        

if __name__ == 'debug':
    debug()