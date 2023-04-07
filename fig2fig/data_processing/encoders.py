import numpy as np

def normalize_type(_type):
    """
    Normalize the type of a node
    """

    map = {
        'FRAME': 'CONTAINER',
        'GROUP': 'CONTAINER',
        'INSTANCE': 'CONTAINER',
        'COMPONENT': 'CONTAINER',
        'RECTANGLE': 'SHAPE',
        'ELLIPSE': 'SHAPE',
        'POLYGON': 'SHAPE',
        'LINE': 'SHAPE',
        'VECTOR': 'SHAPE',
        'STAR': 'SHAPE',
        'TEXT': 'TEXT',
        'BOOLEAN_OPERATION': 'SHAPE',
    }

    return map.get(_type, _type)

def encode_type(_type):
    """
    Encode a type into a one-hot vector
    """
    categories = ['CONTAINER', 'SHAPE', 'TEXT']
    
    one_hot_vector = np.zeros(len(categories), dtype=int)
    index = categories.index(_type) if _type in categories else -1
    if index != -1:
        one_hot_vector[index] = 1

    return one_hot_vector

def decode_hex8(hex8):
    """
    Decode a hex8 color into RGBA, in 0-1 range
    """
    r = int(hex8[0:2], 16) / 255
    g = int(hex8[2:4], 16) / 255
    b = int(hex8[4:6], 16) / 255
    a = int(hex8[6:8], 16) / 255

    return r, g, b, a
    
def is_not_empty(s: str):
    return s and s.strip()