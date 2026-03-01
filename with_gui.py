import cadquery as cq
from cadquery import exporters
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# =============================
# Gridfinity Constants
# =============================
GRID_UNIT = 42.0
HEIGHT_UNIT = 7.0
WALL_THICKNESS = 2.4
FLOOR_THICKNESS = 2.0
FILLET_RADIUS = 3.0

# =============================
# Gridfinity Box Generator
# =============================
def create_gridfinity_box(x_units, y_units, z_units, label=None, embossed=False):
    width = x_units * GRID_UNIT
    depth = y_units * GRID_UNIT
    height = z_units * HEIGHT_UNIT

    # Outer shell
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
        .edges("|Z")
        .fillet(FILLET_RADIUS)
    )

    # Hollow interior
    inner = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_THICKNESS)
        .rect(width - 2 * WALL_THICKNESS,
              depth - 2 * WALL_THICKNESS)
        .extrude(height)
    )

    box = outer.cut(inner)

    # Label Panel
    if label:
        panel_width = width * 0.8
        panel_height = 8
        panel_offset_from_top = 4

        box = (
            box.faces(">Y")
            .workplane(centerOption="CenterOfBoundBox")
            .transformed(offset=(0, 0, -panel_offset_from_top))
            .rect(panel_width, panel_height)
            .cutBlind(-1.0)
        )

        text_size = max(panel_width / (len(label) * 0.6), 4)

        text = (
            box.faces(">Y")
            .workplane(centerOption="CenterOfBoundBox")
            .transformed(offset=(0, 0, -panel_offset_from_top))
            .text(label,
                  fontsize=text_size,
                  distance=0.6,
                  cut=not embossed)
        )

        if embossed:
            box = box.union(text)
        else:
            box = text

    return box


# =============================
# GUI Logic
# =============================
def select_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    csv_entry.delete(0, tk.END)
    csv_entry.insert(0, file_path)


def select_output():
    folder_path = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, folder_path)


def generate_boxes():
    csv_path = csv_entry.get()
    output_path = output_entry.get()
    embossed = embossed_var.get()

    if not csv_path or not output_path:
        messagebox.showerror("Error", "Please select CSV and Output folder.")
        return

    try:
        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            label = str(row["label"])
            x_units = int(row["x_units"])
            y_units = int(row["y_units"])
            z_units = int(row["z_units"])

            box = create_gridfinity_box(
                x_units,
                y_units,
                z_units,
                label=label,
                embossed=embossed
            )

            filename = f"{label}_{x_units}x{y_units}x{z_units}.stl"
            filepath = os.path.join(output_path, filename)

            exporters.export(box, filepath)

        messagebox.showinfo("Success", "STL files generated successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# =============================
# Build GUI
# =============================
root = tk.Tk()
root.title("Gridfinity Box Generator")
root.geometry("500x250")

# CSV Selector
tk.Label(root, text="CSV File:").pack(pady=5)
csv_entry = tk.Entry(root, width=60)
csv_entry.pack()
tk.Button(root, text="Browse", command=select_csv).pack(pady=5)

# Output Folder
tk.Label(root, text="Output Folder:").pack(pady=5)
output_entry = tk.Entry(root, width=60)
output_entry.pack()
tk.Button(root, text="Browse", command=select_output).pack(pady=5)

# Embossed Option
embossed_var = tk.BooleanVar()
tk.Checkbutton(root, text="Emboss Label (Raised Text)", variable=embossed_var).pack(pady=5)

# Generate Button
tk.Button(root, text="Generate STL Files", command=generate_boxes, bg="green", fg="white").pack(pady=15)

root.mainloop()
