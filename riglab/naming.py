TOKENS = dict()


def get_tokens():
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
