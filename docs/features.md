Features - v0.1.3

Winding Diagrams

- Two Layer and Single Layer windings
- Three coil patterns: Lap, Triangle, Concentric
- Chained <-> Concentric conversion preserves first and second arms
- Coils are cut at x = 0.5 and x = all_slots + 0.5
- Grid range is 0.5 .. all_slots + 0.5
- Independent Chained / Concentric groups
- Two independent coil spans
- Automatic span recomputation
- Automatic speed calculation (6000 / Poles = RPM)
- 90-degree diagram rotation
- Edit Diagram mode (main and phase shift)
- Diamonds at x = -1 for shift control

Connection Mode

- Full modular connection package
- 3-button conflict dialog
- Golden rule: no point on a line without a junction
- Junction auto-cleanup
- Hollow junction and wire point squares
- Phase endpoints (R and U) with labels
- Box Select
- Drag and Drop for junctions
- Pencil mode with auto-attach
- Hand / Select toggle
- Undo / Redo / Reset (30 levels)
- Wire points stored without shift (shift applied at draw time)

Zoom and Pan

- Pinch zoom (2 fingers)
- Pan with single finger
- Zoom bounds: auto-fit to 100x
- Anchored zoom
- Zoom box: toggle, unlimited use
- Zoom history: 4 levels
- Floating collapsible zoom panel

Export

- 6 formats: SVG, PDF, PNG, JPG, EPS, DXF
- 300 DPI
- Full page layout (no zoom)
- Line width and font size scale independent of page
- zarin.png logo in both left and right of info table
- Table text sizes by row type (header / body / comment)

UI

- Full Icon System: every button shows a PNG icon
- IconTextButton: icon + text with whole-row click
- Icons in all dialogs, menus, notifications, and panels
- Automatic text fallback when icon is missing
- Dropdown main menu (Windows File-menu style)
- Version suffix on all titles
- App Info with 6 category buttons (docs-driven)
- Unified notifications with type icons
- Centralized theme

Table

- Table inside info_area (with 2mm margin)
- Two logos in info_area (left, right)
- 7 rows x 6 cols
- Row types: header / body / comment
- Header rows: bold text, blue background
- Body rows: normal text, white background
- Comment row: gray background
- Font size / color per row type (display + export)

Project Management

- JSON storage
- Open / Save with file browser
- Auto-draw on load
- Comments field
- Coils per pole manual distribution
- Diagram shift (main + phase) per group

Offline

- Completely offline
