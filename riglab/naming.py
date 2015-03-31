PROFILES = {"current": ""}
TOKENS = dict()


class Profile(object):

    def __init__(self, name):
        self.name = name
        self.fields = list()
        self.separator = "_"


class Field(object):

    def __init__(self, name):
        self.name = name
        self._value = ""
        self.tokens = list()
        self.default = None

    def append_token(self, token, default=False):
        self.tokens.append(token)
        if default:
            self.default = token


def list_tokens():
    return TOKENS.keys()


def get_token(name):
    return TOKENS.get(name)


def new_token(name, value):
    if not get_token(name):
        TOKENS[name] = value
        return True
    return False


def delete_token(name):
    if get_token(name):
        del TOKENS[name]
        return True
    return False


def clear_tokens():
    TOKENS.clear()


def list_profiles():
    return [x for x in PROFILES.keys() if x != "current"]


def new_profile(name):
    if PROFILES.get(name):
        return None
    PROFILES[name] = Profile(name)
    return PROFILES[name]


def get_profile(name):
    p = PROFILES.get(name)
    if p and name == "current":
        return PROFILES.get(p)
    return p


def set_profile(name):
    if PROFILES.get(name):
        PROFILES["current"] = name
        return True
    return False


def current_profile():
    name = PROFILES["current"]
    p = PROFILES.get(name)
    if p:
        return p
    PROFILES["current"] = ""
    return None


def delete_profile(name):
    if name == "current":
        name = PROFILES[name]
    if PROFILES.get(name):
        del PROFILES[name]
        ps = list_profiles()
        if len(ps):
            set_profile(ps[0])
        else:
            PROFILES["current"] = ""
