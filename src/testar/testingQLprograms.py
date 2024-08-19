from miniTESTAR import testar
import os
import importlib.util
import sys
import inspect

def get_oracles(name):
    # Create the full path to the file where the oracles are
    path = os.path.abspath(os.getcwd() + '/../../examples/' + name + ".py")
        
    # Load the module from the file path
    spec = importlib.util.spec_from_file_location(name, path)
    oracle_file = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle_file)
    
    # Get all functions defined in the oracle file
    oracles = [func for name, func in inspect.getmembers(oracle_file, inspect.isfunction)]
    
    return oracles


def test_QL_program(name):
    path = 'file://' + os.path.abspath(os.getcwd() + '/../../examples/' + name + ".html")
    
    testar(path, 2, 50, [], [], get_oracles(name))
