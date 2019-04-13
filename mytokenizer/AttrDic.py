import json

class AttributeDict(object):
    def __init__(self, obj):
        self.obj = obj

    def __getstate__(self):
        return self.obj.items()

    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    def __getattr__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    def fields(self):
        return self.obj

    def keys(self):
        return self.obj.keys()

if __name__ == "__main__":
    attribute_json = json.loads('{"v1":"xxxx", "v2":"vvvv"}', object_hook=AttributeDict)
    print("attribute_json.v1 = {0}".format(attribute_json.v1))

    json_with_array = json.loads('{"arr":[{"v":"xxxx"}, {"v":"vvvv"}]}', object_hook=AttributeDict)
    print("json_with_array[0].v = {0}".format(json_with_array.arr[0].v))