import cadquery as cq
from cadquery import exporters
import pandas as pd
import os

# === GRIDFINITY CONSTANTS ===
GRID_UNIT = 42.0          # 42mm standard grid
HEIGHT_UNIT = 7.0         # 7mm per vertical unit
WALL_THICKNESS = 2.4
FLOOR_THICKNESS = 2.0
FILLET_RADIUS = 3.0

OUTPUT_FOLDER = "generated_boxes"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def create_gridfinity_box(x_units, y_units, z_units):
    width = x_units * GRID_UNIT
    depth = y_units * GRID_UNIT
    height = z_units * HEIGHT_UNIT

    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
        .edges("|Z")
        .fillet(FILLET_RADIUS)
    )

    inner = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_THICKNESS)
        .rect(width - 2 * WALL_THICKNESS,
              depth - 2 * WALL_THICKNESS)
        .extrude(height)
    )

    box = outer.cut(inner)

    return box


def add_label(box, label, width, depth, height):
    text = (
        cq.Workplane("XY")
        .workplane(offset=height - 1.0)
        .text(label,
              fontsize=min(width, depth) / 6,
              distance=1.0,
              cut=True)
    )
    return box.union(text)


def main(csv_file):
    df = pd.read_csv(csv_file)

    combined = None

    for _, row in df.iterrows():
        label = str(row["label"])
        x_units = int(row["x_units"])
        y_units = int(row["y_units"])
        z_units = int(row["z_units"])

        box = create_gridfinity_box(x_units, y_units, z_units)

        width = x_units * GRID_UNIT
        depth = y_units * GRID_UNIT
        height = z_units * HEIGHT_UNIT

        box = add_label(box, label, width, depth, height)

        filename = f"{label}_{x_units}x{y_units}x{z_units}.stl"
        filepath = os.path.join(OUTPUT_FOLDER, filename)

        exporters.export(box, filepath)
        print(f"Exported: {filepath}")

        if combined is None:
            combined = box
        else:
            combined = combined.translate((width + 5, 0, 0)).union(box)

    if combined:
        exporters.export(combined, os.path.join(OUTPUT_FOLDER, "all_boxes.stl"))
        print("Exported combined STL")


if __name__ == "__main__":
    main("boxes.csv")
