import os
import sys
import imp
import hashlib
import inspect

def base_dir(depth=1):
    calling_frame = inspect.stack()[depth]
    calling_file = calling_frame[1]
    return os.path.dirname(os.path.abspath(calling_file))    

def relative_path(*path):
    return os.path.abspath(os.path.join(base_dir(depth=2), *path))

def load_module(module_name, relative_to_caller=True):
    base = base_dir(depth=2)

    path, name = os.path.split(module_name)
    if not path:
        if relative_to_caller:
            paths = [base]
        else:
            paths = None
        found = imp.find_module(name, paths)
        sys.modules.pop(name, None)
        return imp.load_module(name, *found)
    
    if relative_to_caller:
        module_name = os.path.join(base, module_name)
    module_file = open(module_name, "r")
    try:
        name = hashlib.md5(module_name).hexdigest()
        sys.modules.pop(name, None)
        return imp.load_source(name, module_name, module_file)
    finally:
        module_file.close()

def flatten(obj):
    try:
        iterable = iter(obj)
    except TypeError:
        yield obj
        return

    for item in iterable:
        for obj in flatten(item):
            yield obj

def load_configs(module_name, config_func_name="configs"):
    module = load_module(module_name, False)
    config_func = getattr(module, config_func_name, None)

    if not callable(config_func):
        raise ImportError("no callable %r defined" % config_func_name)
    return flatten(config_func())

if __name__ == "__main__":
    import unittest

    class FlattenTests(unittest.TestCase):
        def test_basic(self):
            assert list(flatten([1, 2])) == [1, 2]
            assert list(flatten([[1, [2, 3]], 4])) == [1, 2, 3, 4]

        def test_order(self):
            def iterator(start, end):
                for i in range(start, end):
                    yield i
            assert list(flatten([iterator(1, 3), iterator(3, 5)])) == [1, 2, 3, 4]

    unittest.main()
