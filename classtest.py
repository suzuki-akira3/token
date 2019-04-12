class Prop:
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        print('get')
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        print('set')
        obj.__dict__[self.name] = value

class Obj:
    """
    >>> obj = Obj()
    >>> obj.prop = 123
    set
    >>> print(obj.prop)
    get
    123
    >>> print(obj.__dict__['prop'])
    123
    >>> obj.prop = 456
    set
    """
    prop = Prop('prop')

obj = Obj()
obj.prop = 123
print(obj.prop)
print(obj.__dict__['prop'])
obj.prop = 456