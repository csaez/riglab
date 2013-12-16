import os
import json


class TokenInterface(object):
    TOKEN_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"),
                                              "riglab", "naming", "tokens"))

    def __init__(self, name):
        super(TokenInterface, self).__init__()
        self.name = name

    @property
    def default(self):
        if hasattr(self, "_default"):
            value = self.get(self._default)
            if value:
                return value
        return None

    @default.setter
    def default(self, value):
        self._default = value

    def get(self, value):
        return value

    def isvalid(self, value):
        return True

    def save(self):
        # collect data
        data = dict()
        for k, v in self.__dict__.iteritems():
            if not k.startswith("_"):
                data[k] = v
        data["default"] = self.default
        data["classname"] = self.__class__.__name__
        # serialization
        if not os.path.exists(self.TOKEN_DIR):
            os.makedirs(self.TOKEN_DIR)
        fp = os.path.join(self.TOKEN_DIR, "{}.json".format(self.name))
        with open(fp, "w") as f:
            json.dump(data, f, indent=4)

    def destroy(self):
        os.remove(os.path.join(self.TOKEN_DIR, "{}.json".format(self.name)))


class DictToken(TokenInterface):

    def __init__(self, *args, **kwds):
        super(DictToken, self).__init__(*args, **kwds)
        self.values = dict()

    def get(self, value):
        if not self.isvalid(value):
            return None
        value_lower = value.lower()
        for k, v in self.values.iteritems():
            if k.lower() == value_lower or v.lower() == value_lower:
                return v
        return None

    def isvalid(self, value):
        if isinstance(value, basestring) and all([ch.isalpha() for ch in str(value)]):
            return True
        return False


class StringToken(TokenInterface):

    def get(self, value):
        if not self.isvalid(value):
            return None
        return value

    def isvalid(self, value):
        return any([ch.isalpha() for ch in str(value)])


class NumberToken(TokenInterface):

    def __init__(self, *args, **kwds):
        super(NumberToken, self).__init__(*args, **kwds)
        self.padding = 3

    def get(self, value):
        if not self.isvalid(value):
            return None
        return str(int(value)).zfill(self.padding)

    def isvalid(self, value):
        try:
            int(value)
            return True
        except:
            return False

__all__ = ["TokenInterface", "DictToken", "StringToken", "NumberToken"]
