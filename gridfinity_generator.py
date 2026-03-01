def create_gridfinity_box(x_units, y_units, z_units, label=None, 
                          label_depth=0.6,
                          embossed=False):

    width = x_units * GRID_UNIT
    depth = y_units * GRID_UNIT
    height = z_units * HEIGHT_UNIT

    # === Outer Body ===
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
        .edges("|Z")
        .fillet(FILLET_RADIUS)
    )

    # === Hollow Interior ===
    inner = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_THICKNESS)
        .rect(width - 2 * WALL_THICKNESS,
              depth - 2 * WALL_THICKNESS)
        .extrude(height)
    )

    box = outer.cut(inner)

    # ==========================
    # Label Panel (Front Face)
    # ==========================
    if label:

        panel_width = width * 0.8
        panel_height = 8
        panel_offset_from_top = 4

        # Create shallow recessed panel
        box = (
            box.faces(">Y")
            .workplane(centerOption="CenterOfBoundBox")
            .transformed(offset=(0, 0, -panel_offset_from_top))
            .rect(panel_width, panel_height)
            .cutBlind(-1.0)
        )

        # Add text
        text_size = panel_width / max(len(label) * 0.6, 6)

        text_wp = (
            box.faces(">Y")
            .workplane(centerOption="CenterOfBoundBox")
            .transformed(offset=(0, 0, -panel_offset_from_top))
            .text(label,
                  fontsize=text_size,
                  distance=label_depth,
                  cut=not embossed)
        )

        if embossed:
            box = box.union(text_wp)
        else:
            box = text_wp

    return box
