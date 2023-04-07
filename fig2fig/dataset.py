import json
import click
import sqlite3
from pathlib import Path
import torch
from torch.utils.data import Dataset
import numpy as np


target_features = [
    'type', # one-hot
    'depth', # int
    'n_children', # int
    "x", # float
    "y", # float
    "width", # float
    "height", # float
    'rotation', # float
    'opacity', # float (0-1)
    'color', # hex8 -> 4 floats (0-1)
    'background_color', # hex8 -> 4 floats (0-1)
    'background_image', # bool
    'n_characters', # int
    'font_family', # one-hot
    'font_weight', # one-hot
    'font_size', # float
    'font_style', # one-hot
    'text_decoration', # one-hot
    'text_align', # one-hot
    'text_align_vertical', # one-hot
    'text_auto_resize', # one-hot
    'letter_spacing', # float

    'stroke_linecap', # one-hot
    'border_alignment', # one-hot
    'border_width', # float
    'border_color', # hex8 -> 4 floats (0-1)
    'border_radius', # float

    'box_shadow_offset_x', # float
    'box_shadow_offset_y', # float
    'box_shadow_blur', # float
    'box_shadow_spread', # float

    'padding_top', # float
    'padding_left', # float
    'padding_right', # float
    'padding_bottom', # float

    'constraint_vertical', # one-hot
    'constraint_horizontal', # one-hot

    'layout_align', # one-hot
    'layout_mode', # one-hot
    'layout_positioning', # one-hot
    'layout_grow', # one-hot
    'primary_axis_sizing_mode', # one-hot
    'counter_axis_sizing_mode', # one-hot
    'primary_axis_align_items', # one-hot
    'counter_axis_align_items', # one-hot
    'gap', # float
    'reverse', # one-hot

    'is_mask', # one-hot
    'export_settings', # one-hot
    'mix_blend_mode', # one-hot
    'aspect_ratio', # float
    # ...
]

class NodesDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.column_names = self.get_column_names()

    def get_column_names(self):
        self.cursor.execute("PRAGMA table_info(nodes)")
        return [column_info[1] for column_info in self.cursor.fetchall()]

    def get_sample_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM nodes")
        return self.cursor.fetchone()[0]

    def get_sample(self, idx):
        self.cursor.execute(f"SELECT * FROM nodes WHERE rowid={idx + 1}")
        row = self.cursor.fetchone()
        if row:
            return dict(zip(self.column_names, row))
        return None


class FigmaNodesDataset(Dataset):
    def __init__(self, db, max):
        self.nodes_db = NodesDB(db)

        self.num_samples = self.nodes_db.get_sample_count()
        print(f"Loaded {self.num_samples} samples")

    def __len__(self):
        return self.num_samples
    
    def extract_features_recursive(self, node: dict):
        dimension_features = (
            node["x"], node["y"],
            node["width"], node["height"],
            node["depth"],
            node['n_children'],
            node.get("rotation"),
        )

        container_features = (
            node["opacity"],
            is_not_empty(node.get("background_image")),
            (
              *decode_hex8(node["border_color"]),
            )
        )

        text_features = (
            node.get("opacity"),
            node.get("n_characters"),
            node.get("font_size"),
            node.get("font_weight"),
            node.get("text_align"),
            node.get("text_align_vertical"),
            node.get("font_family"),
            node.get("font_style"),
            node.get("text_decoration"),
            node.get("letter_spacing"),
            node.get("text_auto_resize"),
            (
              *decode_hex8(node.get("color")),
            )
        )

        layout_constraint_features = (
            node.get("constraint_vertical"),
            node.get("constraint_horizontal"),
        )

        layout_flex_features = (
            node.get("layout_align"),
            node.get("layout_mode"),
            node.get("layout_positioning"),
            node.get("layout_grow"),
            node.get("primary_axis_sizing_mode"),
            node.get("counter_axis_sizing_mode"),
            node.get("primary_axis_align_items"),
            node.get("counter_axis_align_items"),
            node.get("reverse"),
        )

        layout_padding_features = (
            node.get("padding_top"),
            node.get("padding_left"),
            node.get("padding_right"),
            node.get("padding_bottom"),
        )

        layout_gap_features = (
            node.get("gap"),
        )

        border_features = (
            node.get("border_alignment"),
            node.get("border_width"),
            node.get("border_radius"),
            (
              *decode_hex8(node.get("border_color")),
            )
        )

        box_shadow_features = (
            node.get("box_shadow_offset_x"),
            node.get("box_shadow_offset_y"),
            node.get("box_shadow_blur"),
            node.get("box_shadow_spread"),
        )

        _aspect_ratio = (
            node.get("aspect_ratio"),
        )

        _is_mask = (
            is_not_empty(node.get("is_mask")),
        )

        _export_settings = (
            # TODO: use one-hot encoding (BITMAP / VECTOR)
            is_not_empty(node.get("export_settings")),
        )

        # Encode one-hot features
        type_encoded = encode_type(normalize_type(node["type"]))

        # TODO: Encode other one-hot features and add them to their corresponding channels

        features = [
            type_encoded,
            dimension_features,
            container_features,
            border_features,
            text_features,
            layout_constraint_features,
            layout_flex_features,
            layout_padding_features,
            layout_gap_features,
            box_shadow_features,
            _aspect_ratio,
            _is_mask,
            _export_settings,
        ]

        # Recurse through children
        children = json.loads(node["children"])
        for child_id in children:
            child_row = self.nodes_db.get_sample(child_id)
            features.extend(self.extract_features_recursive(child_row))

        return features


    def __getitem__(self, idx):
        # Get data from the table
        row = self.nodes_db.get_sample(idx)
        if row is None:
            raise IndexError(f"Index {idx} out of range")

        # Extract features and children
        features = self.extract_features_recursive(row)
        children = json.loads(row["children"])

        num_channels = len(features)
        num_features = max(len(channel) for channel in features)

        tensor_features = torch.zeros((num_channels, num_features), dtype=torch.float32)

        for i, channel in enumerate(features):
            tensor_features[i, :len(channel)] = torch.tensor(channel, dtype=torch.float32)

        return tensor_features, children

    def get_input_dim(self):
        sample, _ = self[0]  # Get a sample from the dataset
        input_dim = sample.numel()  # Calculate the number of elements in the flattened tensor
        return input_dim

def normalize_type(_type):
    """
    Normalize the type of a node
    """
    # TODO: support image
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

@click.command()
@click.argument("db", type=click.Path(exists=True, file_okay=True, dir_okay=False), required=True)
@click.option("--checkpoint", type=click.Path(file_okay=False), required=False, default='.checkpoints/')
@click.option("--max", type=int, required=False, default=None)
@click.option("--shuffle", type=bool, required=False, default=False)
def main(db, checkpoint):
    db = Path(db)
    checkpoint = Path(checkpoint)
    dataset = FigmaNodesDataset(db)
    features, children = dataset[0]

    print(features)
    print(children)

    file = checkpoint / f"{db.stem}.pth"

    torch.save(dataset, file)


if __name__ == "__main__":
    main()
