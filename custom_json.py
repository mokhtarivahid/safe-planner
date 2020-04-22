# majority of code thanks to: https://stackoverflow.com/questions/13249415/how-to-implement-custom-indentation-when-pretty-printing-with-the-json-module#answer-13252112
import _ctypes
import json
import re
from collections import OrderedDict

class NoIndent(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        if not isinstance(self.value, list):
            return repr(self.value)
        else:  # Sort the representation of any dicts in the list.
            reps = ('{{{}}}'.format(', '.join(
                        ('{!r}:{}'.format(k, v) for k, v in sorted(v.items()))
                    )) if isinstance(v, dict)
                        else
                    repr(v) for v in self.value)
            return '[' + ', '.join(reps) + ']'

def di(obj_id):
    """ Reverse of id() function. """
    # from https://stackoverflow.com/a/15012814/355230
    return _ctypes.PyObj_FromPtr(obj_id)

def check_objs(obj):
    # base case
    if len(str(obj)) < 80:
        return NoIndent(obj)
    # recursive step
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = check_objs(v)
    elif isinstance(obj, list):
        for i,l in enumerate(obj):
            obj[i] = check_objs(l)
    # return changed object
    return obj

class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = "@@{}@@"
    regex = re.compile(FORMAT_SPEC.format(r"(\d+)"))

    def default(self, obj):
        return (self.FORMAT_SPEC.format(id(obj)) if isinstance(obj, NoIndent)
                else super(MyEncoder, self).default(obj))

    def encode(self, obj):
        # recursively check if should convert to NoIndent object
        obj = check_objs(obj)
        
        # start formatting
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(MyEncoder, self).encode(obj)  # Default JSON repr.

        # Replace any marked-up object ids in the JSON repr with the value
        # returned from the repr() of the corresponding Python object.
        for match in self.regex.finditer(json_repr):
            id = int(match.group(1))
            # Replace marked-up id with actual Python object repr().
            json_repr = json_repr.replace(
                       '"{}"'.format(format_spec.format(id)), repr(di(id)))
        json_repr = json_repr.replace("'", '"')
        return json_repr


if __name__ == '__main__':

    # data_structure = {
    #     'layer1': {
    #         'layer2': {
    #             'layer3_1': [{"x":1,"y":7}, {"x":0,"y":4}, {"x":5,"y":3},
    #                                   {"x":6,"y":9}],
    #             'layer3_2': 'string',
    #             'layer3_3': [{"x":2,"y":8,"z":3}, {"x":1,"y":5,"z":4},
    #                                   {"x":6,"y":9,"z":8}],
    #             'layer3_4': list(range(20)),
    #         }
    #     }
    # }

    # print(json.dumps(data_structure, cls=MyEncoder, indent=2))

    with open('domains/mai/glenn/solenoid/nondeterministic/prob0.json') as json_file:
        data = json.load(json_file)

    data_str = json.dumps(data, cls=MyEncoder, sort_keys=True, indent=2)
    print(data_str)

