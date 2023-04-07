import json
import os
from pathlib import Path
import numpy as np

# current directory
__dir__ = os.path.dirname(os.path.abspath(__file__))
# font-fallbacks-map.json
font_fallbacks_map: dict = json.load(Path(__dir__ / 'font-fallbacks-map.json').open())

def encode_type(_type):
    """
    Encode a type into a one-hot vector
    """
    mapping = {
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
        'BOOLEAN_OPERATION': 'SHAPE',
        'TEXT': 'TEXT',
    }
    # changing the order of the categories will break the model
    categories = ['OTHER', 'CONTAINER', 'SHAPE', 'TEXT']
    return encode_onehot(mapping.get(_type, 'OTHER'), categories)


def encode_export_settings(export_settings):
    """
    Encode export settings into a one-hot vector
    """
    mapping = {
        "PNG": "BITMAP",
        "JPG": "BITMAP",
        "SVG": "VECTOR",
        "PDF": "VECTOR",
    }

    # changing the order of the categories will break the model
    categories = [None, 'BITMAP', 'VECTOR']

    return encode_onehot(mapping.get(export_settings), categories)


def encode_font_weight(font_weight):
    """
    Encode font weight into a one-hot vector
    """

    # sometimes the font weight is 950, which is not in the list, so we need to round it.
    font_weight = str(round(int(font_weight) / 100) * 100)

    # changing the order of the categories will break the model
    categories = [None, '100', '200', '300', '400', '500', '600', '700', '800', '900']
    return encode_onehot(font_weight, categories)


def encode_font_family(font_family):
    """
    Encode font family into a one-hot vector
    This only supports google fonts
    """

    # fallback to sans-serif if font family is not found (in google fonts)
    generic = font_fallbacks_map.get(font_family, "sans-serif")

    # changing the order of the categories will break the model
    categories = [
        None,
        "serif",
        "sans-serif",
        "monospace",
        "cursive",
        "fantasy",
        "system-ui",
        "ui-serif",
        "ui-sans-serif",
        "ui-monospace",
        "ui-rounded",
        "emoji",
        "math",
        "fangsong",
    ]
    
    return encode_onehot(generic, categories)


def encode_font_style(font_style):
    # changing the order of the categories will break the model
    categories = [None, 'normal', 'italic']
    return encode_onehot(font_style, categories)
    ...

def encode_text_align(text_align):
    # changing the order of the categories will break the model
    categories = [None, 'LEFT', 'RIGHT', 'CENTER', 'JUSTIFIED']
    return encode_onehot(text_align, categories)

def encode_text_align_vertical(text_align_vertical):
    # changing the order of the categories will break the model
    categories = [None, 'TOP', 'CENTER', 'BOTTOM']
    return encode_onehot(text_align_vertical, categories)

def encode_text_decoration(text_decoration):
    # changing the order of the categories will break the model
    categories = [None, 'UNDERLINE', 'STRIKETHROUGH']
    return encode_onehot(text_decoration, categories)

def encode_text_auto_resize(text_auto_resize):
    # changing the order of the categories will break the model
    categories = [None, 'HEIGHT', 'WIDTH_AND_HEIGHT', 'TRUNCATE']
    return encode_onehot(text_auto_resize, categories)


def encode_border_alignment(border_alignment):
    # strokeAlign
    # changing the order of the categories will break the model
    categories = [None, 'INSIDE', 'CENTER', 'OUTSIDE']
    return encode_onehot(border_alignment, categories)


def encode_constraint_vertical(constraint_vertical):
    # https://www.figma.com/developers/api#layoutconstraint-type
    # changing the order of the categories will break the model
    categories = [None, 'TOP', 'BOTTOM', 'CENTER', 'TOP_BOTTOM', 'SCALE']
    return encode_onehot(constraint_vertical, categories)

def encode_constraint_horizontal(constraint_horizontal):
    # https://www.figma.com/developers/api#layoutconstraint-type
    # changing the order of the categories will break the model
    categories = [None, 'LEFT', 'RIGHT', 'CENTER', 'LEFT_RIGHT', 'SCALE']
    return encode_onehot(constraint_horizontal, categories)

def encode_layout_align(layout_align):
    # changing the order of the categories will break the model
    categories = [
        None, 
        # current
        'INHERIT', 'STRETCH',
        # legacy
        'MIN', 'MAX', 'CENTER', 'STRETCH'
    ]
    return encode_onehot(layout_align, categories)

def encode_layout_mode(layout_mode):
    # changing the order of the categories will break the model
    categories = [None, 'NONE', 'HORIZONTAL', 'VERTICAL']
    return encode_onehot(layout_mode, categories)

def encode_layout_positioning(layout_positioning):
    # changing the order of the categories will break the model
    categories = [None, 'AUTO', 'ABSOLUTE']
    return encode_onehot(layout_positioning, categories)

def encode_layout_grow(layout_grow):
    # changing the order of the categories will break the model
    categories = [None, 0, 1]
    return encode_onehot(layout_grow, categories)

def encode_primary_axis_sizing_mode(primary_axis_sizing_mode):
    # changing the order of the categories will break the model
    categories = [None, 'FIXED', 'AUTO']
    return encode_onehot(primary_axis_sizing_mode, categories)

def encode_counter_axis_sizing_mode(counter_axis_sizing_mode):
    # changing the order of the categories will break the model
    categories = [None, 'FIXED', 'AUTO']
    return encode_onehot(counter_axis_sizing_mode, categories)

def encode_primary_axis_align_items(primary_axis_align_items):
    # changing the order of the categories will break the model
    categories = [None, 'MIN', 'CENTER', 'MAX', 'SPACE_BETWEEN']
    return encode_onehot(primary_axis_align_items, categories)

def encode_counter_axis_align_items(counter_axis_align_items):
    # changing the order of the categories will break the model
    categories = [None, 'MIN', 'CENTER', 'MAX', 'BASELINE']
    return encode_onehot(counter_axis_align_items, categories)


def encode_onehot(value, categories):
    """
    Encode a value into a one-hot vector
    """
    one_hot_vector = np.zeros(len(categories), dtype=int)
    index = categories.index(value) if value in categories else -1
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


def encode_is_boolean(_is):
    return encode_tobinary(_is, null=0)

def encode_tobinary(value, null=0):
    if value is None:
        return null
    
    if type(value) == bool:
        return int(value)
    
    if type(value) == str:
        if value == '1':
            return 1
        elif value == '0':
            return 0
        else:
          if is_not_empty(value):
              return 1
          else:
              return 0
    
    if type(value) == int:
        if value == 1:
            return 1
        elif value == 0:
            return 0
        else:
            return 0
    
    return null

def is_not_empty(s: str):
    return s and s.strip()