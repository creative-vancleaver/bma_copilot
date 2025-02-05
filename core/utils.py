import re

def sanitize_name(name):

    return re.sub(r'\W+', '_', name).strip('_') # REPLACE NON-ALPHANUMERIC CHARS WITH '_'
