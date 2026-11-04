import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

function readJsonl(name) {
  return fs.readFileSync(path.join(root, "fixtures", name), "utf8")
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));
}

const context = vm.createContext({ window: {} });
vm.runInContext(fs.readFileSync(path.join(root, "js", "data-loader.js"), "utf8"), context);

const edges = readJsonl("demo_edge_receipts.jsonl");
const loops = readJsonl("demo_loop_receipts.jsonl");
const certificates = readJsonl("demo_lineage_certificates.jsonl");
const calibration = JSON.parse(fs.readFileSync(path.join(root, "fixtures", "demo_calibration.json"), "utf8"));

const extended = context.window.GodelData.parseNodeId(
  "full_float32/L22/graph_reachability/shard-03/rank-2"
);
assert.equal(extended.state, "full_float32");
assert.equal(extended.layer, 22);
assert.equal(extended.family, "graph_reachability");
assert.equal(extended.context_shard, "shard-03");
assert.equal(extended.rank, 2);

const data = context.window.GodelData.compile({
  name: "fixture-validation",
  edges,
  loops,
  certificates,
  anchors: [],
  calibration
});

assert.equal(data.nodes.length, 20, "fixture must contain exactly 20 nodes");
assert.equal(data.edges.length, 26, "fixture must contain exactly 26 edges");
assert.equal(data.loops.length, 6, "fixture must contain exactly 6 loops");
assert.equal(data.warnings.length, 0, "fixture must compile without warnings");

const reversal = data.loops.filter((loop) => loop.det_h < 0);
assert.equal(reversal.length, 1, "fixture must contain one orientation reversal");
assert.equal(reversal[0].canonical_angles_degrees, null, "orientation reversal must suppress canonical angles");

const belowFloor = data.loops.filter((loop) => loop.max_angle !== null && loop.max_angle < calibration.bias_floor_degrees);
assert.equal(belowFloor.length, 1, "fixture must contain one below-floor loop");

for (const loop of data.loops) {
  for (const edgeId of loop.edge_order) assert.ok(data.edgeMap.has(edgeId), `${loop.loop_id} references missing edge ${edgeId}`);
  if (loop.canonical_angles_degrees) {
    const sorted = [...loop.canonical_angles_degrees].sort((a, b) => a - b);
    assert.deepEqual(loop.canonical_angles_degrees, sorted, `${loop.loop_id} angles are not sorted`);
  }
}

const saeRaw = JSON.parse(fs.readFileSync(path.join(root, "fixtures", "demo_sae_path_bundle.json"), "utf8"));
const sae = context.window.GodelData.normalizeSaeBundle(saeRaw, "demo_sae_path_bundle.json");
assert.equal(sae.mode, "sae_paths");
assert.equal(sae.dimensions.length, 5);
assert.deepEqual(Array.from(sae.defaultAxes), ["feature_01", "feature_02", "feature_03"]);
assert.equal(sae.nodes.length, 6);
assert.equal(sae.edges.length, 3);
assert.equal(sae.paths.length, 3);
assert.deepEqual(Array.from(new Set(sae.nodes.map((node) => node.state))).sort(), ["base", "beast", "jinn"]);
assert.ok(sae.edges.every((edge) => edge.is_sae_path));
assert.ok(sae.paths.every((path) => path.is_sae_path && path.node_order.length === 2));
assert.equal(sae.nodeMap.get("beast/L31/civic_pluralist--srt/demo/control").behavioral_hard_failure, true);

assert.throws(
  () => context.window.GodelData.normalizeSaeBundle({ ...saeRaw, dimensions: saeRaw.dimensions.slice(0, 4) }, "bad.json"),
  /requires 5-15 dimensions/
);

console.log("Gödel globe fixtures valid: holonomy receipts plus 5D base/Jinn/Beast SAE paths.");
