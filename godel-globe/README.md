# Gödel globe

The Gödel globe is a static, interactive viewer for edge, loop, anchor, and lineage-certificate receipts emitted by the RSITopology identity-attestation stack. It embeds the receipt graph on two stylized spherical shells and animates only the measured loop-closure rotation.

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

The local JavaScript is split into small browser scripts rather than local ES-module imports because Chromium blocks local `file://` module graphs. The page uses an inline ES-module bridge for pinned Three.js CDN modules, preserving direct-file operation without a server.

## Receipt contract

Each JSONL file contains one JSON object per nonblank line. Extra fields are ignored.

### Edges

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

## Interaction

- Drag to orbit; scroll to zoom. The globe rotates slowly while idle.
- Filter by family, rank, shell, or node-id substring.
- Hover nodes and edges for receipt metrics.
- Select a loop in the sidebar or on the globe. An eligible loop first carries an orthonormal triad around its measured path, then applies the receipt's maximum canonical angle at loop closure. No local curvature distribution is inferred.
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

The validator checks receipt counts, exact edge references, determinant/angle suppression, calibration-floor coverage, and the expected 20-node universe.
