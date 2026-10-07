# Preset catalog

One preset is one row `{dot, frame, ball}`. No mixing of parts across presets.

| Preset | Dots | Eye frame | Eye ball |
|---|---|---|---|
| Square (default) | square | square | square |
| Circle | circular | circular | circular |
| Rounded | rounded, not merged | rounded | rounded |
| Horizontal | horizontal pills | rounded | horizontal pill stack |
| Vertical | vertical pills | rounded | vertical pill stack |
| Bubble | small gapped circles | rounded | multi-dot grid |
| Fluid | merged blobs, rounded convex and concave corners | rounded square (not a full circle) | rounded blob |

## Rules

- Frame echoes the dot END treatment; ball echoes dot DIRECTION or form.
- Frames keep 1:1 aspect.
- Fluid: modules merge per connected group; outer corners round where no neighbor; concave joins smoothed; no square edges.
- Thumbnails: static upper-left crop of a demo QR (one eye plus some dots), in the currently chosen color/gradient.
- Adding a preset = adding a row; the scan test grades it automatically.
