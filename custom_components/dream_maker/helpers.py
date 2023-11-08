

def try_read_as_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value == 'true'
    
    if isinstance(value, int):
        if value == 1:
            return True
        elif value == 0:
            return False

    raise ValueError('[{}]无法被转为bool'.format(value))
