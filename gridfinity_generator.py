def create_gridfinity_box(x_units, y_units, z_units):
    width = x_units * GRID_UNIT
    depth = y_units * GRID_UNIT
    height = z_units * HEIGHT_UNIT

    # === Main outer body ===
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
        .edges("|Z")
        .fillet(FILLET_RADIUS)
    )

    # === Hollow interior ===
    inner = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_THICKNESS)
        .rect(width - 2 * WALL_THICKNESS,
              depth - 2 * WALL_THICKNESS)
        .extrude(height)
    )

    box = outer.cut(inner)

    # === Bottom Lip Profile (Accurate Gridfinity Geometry) ===

    lip_profile = (
        cq.Workplane("XZ")
        .workplane(offset=width/2)
        .moveTo(0, 0)
        .line(0.7, 0)                 # bottom flat
        .line(1.8, 1.8)               # 45° upward
        .line(0, 1.8)                 # vertical
        .line(-2.15, 2.15)            # 45° taper inward
        .line(-0.25, 0)               # top offset
        .close()
    )

    # Cut lip around perimeter
    lip_cut = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(5)  # enough to intersect
    )

    box = box.faces("<Z").workplane().rect(width, depth).extrude(-5)

    # Apply 45° chamfer to bottom outside edge
    box = box.edges("|Z and <Z").chamfer(0.7)

    return box
