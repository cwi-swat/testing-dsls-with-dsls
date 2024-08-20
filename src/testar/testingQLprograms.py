from miniTESTAR import testar
import os
import importlib.util
import sys
import inspect

def import_oracle_module(url, name):
    # The python file where the oracles are is in the same dir as the html
    path = url.replace("html", "py")
        
    # Load the module from the file path
    spec = importlib.util.spec_from_file_location(name, path)
    oracle_file = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle_file)
    
    return oracle_file
    
def testar_QL_webApp(url):
    
    # Get the name of the QL app and import the generated oracle file
    name = os.path.splitext(os.path.basename(url))[0]
    oracle_file = import_oracle_module(url, name)
    
    # Get all functions defined in the oracle file
    oracles = [func for name, func in inspect.getmembers(oracle_file, inspect.isfunction)]
     
    # Call testar
    testar('file://' + url, 2, 10, [], [], oracles, 60)

if __name__ == "__main__":
    testar_QL_webApp(sys.argv[1])