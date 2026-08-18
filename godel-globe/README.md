# Gödel globe

The Gödel globe is a static, interactive viewer for edge, loop, anchor, and lineage-certificate receipts emitted by the RSITopology identity-attestation stack. It also accepts compact Temptation Eval SAE path bundles. Holonomy receipts retain the original shell view and measured loop-closure animation; SAE bundles use explicit base, Jinn, and Beast shells with selectable three-axis projections from a 5–15D structure.

For the broader product argument—why mechinterp interfaces should distinguish feature visibility from transportable feature identity—see [MECHINTERP_TOOL_UX_DIRECTION.md](MECHINTERP_TOOL_UX_DIRECTION.md).

## Open it

1. Open `index.html` directly in a current Chrome, Edge, or Firefox browser. No local server or build command is required.
2. Keep an internet connection available for the pinned Three.js modules from jsDelivr. Receipt data never leaves the browser.
3. The synthetic demo appears automatically.
4. To exercise the file loader, choose **Load receipts** and select these four files together:
   - `fixtures/demo_edge_receipts.jsonl`
   - `fixtures/demo_loop_receipts.jsonl`
   - `fixtures/demo_lineage_certificates.jsonl`
   - `fixtures/demo_calibration.json`

The same files can be dragged onto the globe. The picker accepts arbitrary filenames when their first JSON object identifies the receipt type, though descriptive `edge`, `loop`, `anchor`, `certificate`, and `calibration` names are recommended.

To exercise SAE mode, load `fixtures/demo_sae_path_bundle.json` by itself. That
fixture is synthetic UI data, not a model result. SAE paths remain open rather
than being rendered as loops, and the UI labels a path provisional when no
held-out causal-effect receipt is attached.

The local JavaScript is split into small browser scripts rather than local ES-module imports because Chromium blocks local `file://` module graphs. The page uses an inline ES-module bridge for pinned Three.js CDN modules, preserving direct-file operation without a server.

Runtime-state options are populated from loaded node IDs. The real v0.1
identity run uses `full_float32` and `full_bfloat16` shells; the bundled demo
retains the older `base` and `insecure` labels. Node IDs may append context and
rank segments, for example
`full_float32/L22/graph_reachability/shard-03/rank-2`; the family filter uses
the first segment after the layer.

## Receipt contract

Each JSONL file contains one JSON object per nonblank line. Extra fields are ignored.

### Edges

Abbreviated header (the required `nodes` and `paths` arrays follow it):

```json
{"edge_id":"e1","source_node":"base/L40/family","target_node":"base/L46/family","mean_chordal_lineage":0.98,"worst_direction_retention":0.93,"rank":6,"transport_hash":"..."}
```

### Loops

```json
{"loop_id":"p1","root_node":"base/L40/family","edge_order":["e1","e2","e3","e4"],"det_h":1.0,"canonical_angles_degrees":[3.2,14.7],"identity_loss":0.066,"orientation_flag":false,"basis_hashes":["..."]}
```

For `det_h < 0`, canonical angles are suppressed even if a malformed producer supplies them. The loop renders as an orientation reversal and cannot be animated.

### Anchors or certificates

```json
{"site_id":"base/L40/family","attained_level":"holonomy_clean","margins":{"lineage":0.03}}
```

`certification_level` is accepted as an alias for `attained_level`.

### Calibration

```json
{"bias_floor_degrees":5.0}
```

Loops below the optional floor remain inspectable but are faint and receive no animation emphasis.

### Compact SAE path bundle

A whole JSON file with `schema_version: "godel_sae_path_bundle_v1"` is loaded by
itself. It must contain 5–15 unique dimensions, a coordinate vector of the same
length for every node, and paths whose node IDs all exist. The Temptation Eval
exporter supplies base/Jinn/Beast model states, layer order, behavioral hard-fail
flags, artifact hashes, and optional causal-effect receipts. The viewer projects
three user-selected dimensions onto the state shells; projection geometry is
descriptive and never upgrades the evidence claim.

```json
{
  "schema_version": "godel_sae_path_bundle_v1",
  "model_states": ["base", "jinn", "beast"],
  "default_axes": ["L15_F1", "L23_F9", "L31_F4"],
  "dimensions": [
    {"dimension_id": "L15_F1", "label": "L15 F1"},
    {"dimension_id": "L23_F9", "label": "L23 F9"},
    {"dimension_id": "L31_F4", "label": "L31 F4"},
    {"dimension_id": "L27_F2", "label": "L27 F2"},
    {"dimension_id": "L19_F7", "label": "L19 F7"}
  ]
}
```

## Interaction

- Drag to orbit; scroll to zoom. The globe rotates slowly while idle.
- Filter by family, rank, shell, or node-id substring.
- Hover nodes and edges for receipt metrics.
- Select a loop or SAE path in the sidebar or on the globe. An eligible holonomy loop first carries an orthonormal triad around its measured path, then applies the receipt's maximum canonical angle at loop closure. SAE paths do not receive closure animation.
- Use the details panel to inspect the complete sorted angle spectrum, determinant, identity loss, edge order, and copyable receipt hashes.

## Performance model

Nodes use instanced meshes. Edge thickness is quantized into five worst-retention bins rendered with five batched wide-line draw calls. Loops and picking paths use batched segment geometries. Filters rebuild static buffers rather than allocating geometry in the render loop. The design target is approximately 500 nodes, 2,000 edges, and 500 elementary loops on a contemporary integrated or discrete GPU.

## Validate the fixture

From the repository root:

```powershell
node --check godel-globe/js/demo-data.js
node --check godel-globe/js/data-loader.js
node --check godel-globe/js/globe.js
node --check godel-globe/js/app.js
node godel-globe/tests/validate-fixtures.mjs
```

The validator checks receipt counts, exact edge references, determinant/angle suppression, calibration-floor coverage, the expected 20-node holonomy universe, and the synthetic 5D base/Jinn/Beast SAE bundle.
