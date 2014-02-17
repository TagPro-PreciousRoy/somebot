import json

class NoIndent(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        if not isinstance(self.value, (list, tuple)):
            return repr(self.value)
        else:
            delimiters = '[]' if isinstance(self.value, list) else '()'
            pairs = ('{!r}:{}'.format(*component)
                         for coordinate in self.value
                             for component in sorted(coordinate.items()))
            pairs = ('{{{}, {}}}'.format(*pair)
                         for pair in zip(*[iter(pairs)]*2))
            return delimiters[0] + ', '.join(pairs) + delimiters[1]

class TagProEncoder(json.JSONEncoder):
    def default(self, obj):
        return(repr(obj) if isinstance(obj, NoIndent) else
               json.JSONEncoder.default(self, obj))

