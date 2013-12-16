from contextlib import contextmanager
import shutil
import json
import os

from wishlib.utils import JSONDict

from .tokens import *


class Manager(object):
    NAMING_DIR = os.path.join(os.path.expanduser("~"), "riglab", "naming")

    def __init__(self):
        super(Manager, self).__init__()
        if not os.path.exists(self.NAMING_DIR):
            os.makedirs(self.NAMING_DIR)
        self.qn = self.quickname  # alias

    @property
    def rule(self):
        if hasattr(self, "_rule"):
            return self._rule
        return self.rules.keys()[0]

    @rule.setter
    def rule(self, value):
        if value not in self.rules.keys():
            raise KeyError("{0} not in self.rules.keys()".format(value))
        self._rule = value

    @property
    def rules(self):
        if hasattr(self, "_rules"):
            return self._rules
        fp = os.path.join(self.NAMING_DIR, "rules.json")
        if not os.path.exists(fp):
            src = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                "..", "data", "rules.json"))
            shutil.copy(src, self.NAMING_DIR)
        self._rules = JSONDict(fp)
        return self._rules

    @property
    def tokens(self):
        if hasattr(self, "_tokens"):
            return self._tokens
        token_dir = os.path.join(self.NAMING_DIR, "tokens")
        if not os.path.exists(token_dir):
            src = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                "..", "data", "tokens"))
            shutil.copytree(src, os.path.join(self.NAMING_DIR, "tokens"))
        self._tokens = dict()
        for fp in os.listdir(token_dir):
            fp = os.path.join(token_dir, fp)
            if os.path.isdir(fp) or not fp.endswith(".json"):
                continue
            with open(fp) as f:
                data = json.load(f)
            cls = globals().get(data.get("classname"))
            if cls:
                token = cls(data.get("name"))
                if data.get("values"):
                    token.values = data.get("values")
                if data.get("padding"):
                    token.padding = data.get("padding")
                token.default = data.get("default")
                self._tokens[token.name] = token
        return self._tokens

    def new_token(self, name, classname):
        cls = globals().get(classname)
        self.tokens[name] = cls(name)
        self.tokens[name].save()
        return self.tokens[name]

    @contextmanager
    def override(self, **kwds):
        defaults = dict()
        for k, v in kwds.iteritems():
            if k == "rule":
                defaults["rule"] = self.rule
                self.rule = v
                continue
            token = self.tokens.get(k)
            if token:
                defaults[k] = token.default
                token.default = token.get(v)
        yield
        for k, v in defaults.iteritems():
            if k == "rule":
                self.rule = v
                continue
            self.tokens[k].default = v

    def quickname(self, *args, **kwargs):
        _data = dict()
        # get tokens
        # from explicit kwargs
        for key, value in kwargs.iteritems():
            for token_name, token in self.tokens.iteritems():
                if key != token_name:
                    continue
                if token.get(value):
                    _data[token_name] = token.get(value)
        # from implicit args
        for value in args:
            result = list()
            for token_name, token in self.tokens.iteritems():
                if token.get(value):
                    item = (token.name, token.get(value))
                    if isinstance(token, DictToken):
                        result.insert(0, item)
                        continue
                    result.append(item)
            if len(result):
                result = result[0]
                _data[result[0]] = result[1]
        # default values
        for token_name, token in self.tokens.iteritems():
            if token_name not in _data.keys() and token.default:
                _data[token_name] = token.default
        # build name from rule
        rule = self.rule
        for k, v in kwargs.iteritems():
            if k == "rule":
                rule = v
        name = self.rules.get(rule)
        for token_name, token_value in _data.iteritems():
            name = name.replace(token_name, token_value)
        for token_name in self.tokens.keys():
            if token_name in name:
                raise AttributeError("{} not found".format(token_name))
        return name

    def decompose(self, name, rule):
        if not self.rules.get(rule) or "_" not in name:
            return None
        names = name.split("_")
        token_names = self.rules.get(rule).split("_")
        data = dict()
        for i, x in enumerate(token_names):
            token = self.tokens.get(x)
            if not token:
                continue
            if hasattr(token, "values"):
                for k, v in token.values.iteritems():
                    if v == unicode(names[i]):
                        data[x] = k
            else:
                data[x] = token.get(names[i])
        return data
