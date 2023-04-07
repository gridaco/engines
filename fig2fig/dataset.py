import json
import click
import sqlite3
from pathlib import Path
import torch
from tqdm import tqdm
from torch.utils.data import Dataset
from data_processing.encoders import encode_border_alignment, encode_constraint_horizontal, encode_constraint_vertical, encode_counter_axis_align_items, encode_counter_axis_sizing_mode, encode_export_settings, encode_font_family, encode_font_style, encode_font_weight, encode_layout_align, encode_layout_grow, encode_layout_mode, encode_layout_positioning, encode_primary_axis_align_items, encode_primary_axis_sizing_mode, encode_text_align, encode_text_align_vertical, encode_text_auto_resize, encode_text_decoration, encode_type, decode_hex8, encode_tobinary, encode_is_boolean, encode_r

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

    # 'stroke_linecap', # one-hot (not used)
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
    # 'mix_blend_mode', # one-hot (not used)
    'aspect_ratio', # float
    # ...
]

class NodesDB:
    def __init__(self, db_path, max, max_depth):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.column_names = self.get_column_names()
        self.max = max
        self.max_depth = max_depth

    def get_column_names(self):
        self.cursor.execute("PRAGMA table_info(nodes)")
        return [column_info[1] for column_info in self.cursor.fetchall()]

    def get_sample_count(self):
        if self.max_depth is None:
            self.cursor.execute("SELECT COUNT(*) FROM nodes")
        else:
            self.cursor.execute(f"SELECT COUNT(*) FROM nodes WHERE depth <= {self.max_depth}")
        count = self.cursor.fetchone()[0]
        return min(count, self.max) if self.max else count

    def get_sample(self, idx):
        self.cursor.execute(f"SELECT * FROM nodes WHERE depth <= {self.max_depth} LIMIT 1 OFFSET {idx}")
        row = self.cursor.fetchone()
        if row:
            return dict(zip(self.column_names, row))
        return None
    
    def get_sample_by_node_id(self, node_id, parent_id):
        self.cursor.execute(f"SELECT * FROM nodes WHERE node_id='{node_id}' AND parent_id='{parent_id}'")
        row = self.cursor.fetchone()
        if row:
            return dict(zip(self.column_names, row))
        return None

class FigmaNodesDataset(Dataset):
    def __init__(self, db, max, max_depth):
        self.nodes_db = NodesDB(db, max, max_depth)

        self.num_samples = self.nodes_db.get_sample_count()
        print(f"Loaded {self.num_samples} samples")

    def __len__(self):
        return self.num_samples
    
    def extract_features_recursive(self, node: dict):
        dimension_features = (
            node["x"], node["y"],
            node["width"], node["height"],
            node["depth"],
            node['n_children'] or 0,
            node.get("rotation"),
        )

        container_features = (
            node["opacity"],
            encode_tobinary(node.get("background_image")),
        )

        background_color_features = (
            *decode_hex8(node.get("background_color")),
        )

        text_features = (
            encode_r(node.get("opacity", 1)),
            encode_r(node.get("n_characters", 0)),
            encode_font_family(node.get("font_family")),
            encode_font_weight(node.get("font_weight")),
            encode_r(node.get("font_size")),
            encode_font_style(node.get("font_style")),
            encode_text_decoration(node.get("text_decoration")),
            encode_text_align(node.get("text_align")),
            encode_text_align_vertical(node.get("text_align_vertical")),
            encode_text_auto_resize(node.get("text_auto_resize")),
            encode_r(node.get("letter_spacing")),
        )

        text_container_features = (
            *decode_hex8(node.get("color")),
        )

        layout_constraint_features = (
            encode_constraint_vertical(node.get("constraint_vertical")),
            encode_constraint_horizontal(node.get("constraint_horizontal")),
        )

        layout_flex_features = (
            encode_layout_align(node.get("layout_align")),
            encode_layout_mode(node.get("layout_mode")),
            encode_layout_positioning(node.get("layout_positioning")),
            encode_layout_grow(node.get("layout_grow")),
            encode_primary_axis_sizing_mode(node.get("primary_axis_sizing_mode")),
            encode_counter_axis_sizing_mode(node.get("counter_axis_sizing_mode")),
            encode_primary_axis_align_items(node.get("primary_axis_align_items")),
            encode_counter_axis_align_items(node.get("counter_axis_align_items")),
            encode_is_boolean(node.get("reverse")),
        )

        layout_padding_features = (
            encode_r(node.get("padding_top")),
            encode_r(node.get("padding_left")),
            encode_r(node.get("padding_right")),
            encode_r(node.get("padding_bottom")),
        )

        layout_gap_features = (
            encode_r(node.get("gap")),
        )

        border_features = (
            encode_border_alignment(node.get("border_alignment")),
            encode_r(node.get("border_width")),
            encode_r(node.get("border_radius")),
        )

        border_color_features = (
            *decode_hex8(node.get("border_color")),
        )

        box_shadow_features = (
            encode_r(node.get("box_shadow_offset_x")),
            encode_r(node.get("box_shadow_offset_y")),
            encode_r(node.get("box_shadow_blur")),
            encode_r(node.get("box_shadow_spread")),
        )

        _aspect_ratio = (
            encode_r(node.get("aspect_ratio")),
        )

        _is_mask = (
            encode_is_boolean(node.get("is_mask")),
        )

        _export_settings = (
            encode_export_settings(node.get("export_settings")),
        )

        # Encode one-hot features
        type_encoded = encode_type(node["type"])

        features = [
            (type_encoded,),
            dimension_features,
            container_features,
            background_color_features,
            border_features,
            border_color_features,
            text_features,
            text_container_features,
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
        children = safe_loads(node["children"]) if node["children"] else []
        for child_id in children:
            child_row = self.nodes_db.get_sample_by_node_id(node_id=child_id, parent_id=node["node_id"])
            features.extend(self.extract_features_recursive(child_row))

        return features


    def __getitem__(self, idx):
        # Get data from the table
        row = self.nodes_db.get_sample(idx)
        if row is None:
            raise IndexError(f"Index {idx} out of range")

        # input parameters
        root_width = row["width"]
        root_height = row["height"]
        root_type = encode_type(row["type"])


        # Extract features
        features = self.extract_features_recursive(row)

        num_channels = len(features)
        num_features = max(len(channel) for channel in features)

        tensor_features = torch.zeros((num_channels, num_features), dtype=torch.float32)

        for i, channel in enumerate(features):
            tensor_features[i, :len(channel)] = torch.tensor(channel, dtype=torch.float32)

        return tensor_features, (root_type,), (root_width, root_height)

    def get_input_dim(self):
        sample, _ = self[0]  # Get a sample from the dataset
        input_dim = sample.numel()  # Calculate the number of elements in the flattened tensor
        return input_dim
    
    def save_tensors(self, file, max):
        sample_data = []
        for idx in tqdm(range(max) if max else range(self.num_samples)):
            tensor_features, root_type, dimensions = self[idx]
            sample_data.append((tensor_features, root_type, dimensions))
        torch.save(sample_data, file)

def safe_loads(s):
    try:
        return json.loads(s.replace("'", "\""))
    except Exception as e:
        print(f"Failed to parse: {s}")
        raise e


@click.command()
@click.argument("db", type=click.Path(exists=True, file_okay=True, dir_okay=False), required=True)
@click.option("--checkpoint", type=click.Path(file_okay=False), required=False, default='./checkpoints/')
@click.option("--max", type=click.INT, required=False, default=None)
@click.option("--depth", type=click.INT, required=False, default=None)
def main(db, checkpoint, max, depth):
    db = Path(db)
    checkpoint = Path(checkpoint)
    dataset = FigmaNodesDataset(db, max=max, max_depth=depth)

    file = checkpoint / f"{db.stem}.pth"
    dataset.save_tensors(file, max=max)

if __name__ == "__main__":
    main()
