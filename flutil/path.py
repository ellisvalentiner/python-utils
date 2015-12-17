import os

def data_root():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'data')
