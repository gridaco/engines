import click
import sqlite3
from pathlib import Path
import torch
from torch.utils.data import Dataset


class FigmaNodesDataset(Dataset):
    def __init__(self, db, max):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT COUNT(*) FROM nodes")
        self.num_samples = self.cursor.fetchone()[0]
        print(f"Loaded {self.num_samples} samples")
        
    def __len__(self):
        return self.num_samples

    def extract_features_recursive(self, node):
        features = []

        # Extract features from the current node
        width = node.get("width", 0)
        height = node.get("height", 0)
        x = node.get("x", 0)
        y = node.get("y", 0)
        constraints = node.get("constraints", {"horizontal": "none", "vertical": "none"})
        color = node.get("color", [0, 0, 0, 1])  # RGBA format
        characters = len(node["characters"]) if "characters" in node else 0

        horizontal_constraint_value = 1 if constraints["horizontal"] == "stretch" else 0
        vertical_constraint_value = 1 if constraints["vertical"] == "stretch" else 0

        current_features = [width, height, x, y, horizontal_constraint_value, vertical_constraint_value, *color, characters]
        features.extend(current_features)

        # Recurse through children
        if "children" in node:
            for child in node["children"]:
                features.extend(self.extract_features_recursive(child))

        return features

    def __getitem__(self, idx):
        # Get data from the table
        self.cursor.execute(f"SELECT * FROM nodes WHERE id={idx + 1}")
        row = self.cursor.fetchone()
        if row is None:
            raise IndexError(f"Index {idx} out of range")
        
        # Extract features and children
        features = self.extract_features_recursive(row[1:61])  # assuming the features are stored as a JSON string
        children = [int(child_id) for child_id in row[61].split(',') if child_id]

        return torch.tensor(features, dtype=torch.float32), children

@click.command()
@click.argument("db", type=click.Path(exists=True, file_okay=True, dir_okay=False), required=True)
@click.option("--checkpoint", type=click.Path(file_okay=True, exists=False), required=False, deafult='checkpoints/nodes-seq.pth')
@click.option("--max", type=int, required=False, default=None)
@click.option("--shuffle", type=bool, required=False, default=False)
def main(db, checkpoint):
    db = Path(db)
    checkpoint = Path(checkpoint)
    dataset = FigmaNodesDataset(db)
    features, children = dataset[0]

    print(features)
    print(children)

    torch.save(dataset, checkpoint)


if __name__ == "__main__":
    main()