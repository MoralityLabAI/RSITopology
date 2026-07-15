(function () {
  "use strict";

  const states = ["base", "insecure"];
  const layers = [40, 46, 52, 57, 62];
  const families = ["graph_reachability", "symbol_transport"];
  const edges = [];

  const short = { graph_reachability: "g", symbol_transport: "s" };
  const node = (state, layer, family) => `${state}/L${layer}/${family}`;

  for (const family of families) {
    const prefix = short[family];
    for (const state of states) {
      for (let i = 0; i < layers.length - 1; i += 1) {
        const lineage = state === "base" ? 0.982 - i * 0.006 : 0.956 - i * 0.009;
        edges.push({
          edge_id: `${prefix}-${state}-${layers[i]}-${layers[i + 1]}`,
          source_node: node(state, layers[i], family),
          target_node: node(state, layers[i + 1], family),
          mean_chordal_lineage: lineage,
          worst_direction_retention: Math.max(0.7, lineage - 0.045),
          rank: family === "graph_reachability" ? 6 : 4,
          transport_hash: `${prefix}${state[0]}${layers[i]}${layers[i + 1]}`.padEnd(64, "a")
        });
      }
    }
    for (const layer of layers) {
      const lineage = 0.93 + ((layer * 7 + prefix.charCodeAt(0)) % 6) * 0.009;
      edges.push({
        edge_id: `${prefix}-cross-${layer}`,
        source_node: node("base", layer, family),
        target_node: node("insecure", layer, family),
        mean_chordal_lineage: lineage,
        worst_direction_retention: lineage - 0.06,
        rank: family === "graph_reachability" ? 6 : 4,
        transport_hash: `${prefix}x${layer}`.padEnd(64, "b")
      });
    }
  }

  function loop(family, a, b, angle, loss, options) {
    const prefix = short[family];
    const opts = options || {};
    return {
      loop_id: `${prefix}-plaquette-${a}-${b}`,
      root_node: node("base", a, family),
      edge_order: [
        `${prefix}-base-${a}-${b}`,
        `${prefix}-cross-${b}`,
        `${prefix}-insecure-${a}-${b}`,
        `${prefix}-cross-${a}`
      ],
      det_h: opts.reversal ? -1 : 1,
      canonical_angles_degrees: opts.reversal ? null : opts.spectrum || [angle],
      identity_loss: loss,
      orientation_flag: Boolean(opts.reversal),
      basis_hashes: [
        `${prefix}${a}root`.padEnd(64, "c"),
        `${prefix}${b}far`.padEnd(64, "d")
      ]
    };
  }

  const loops = [
    loop("graph_reachability", 40, 46, 2.4, 0.008, { spectrum: [0.8, 2.4] }),
    loop("graph_reachability", 46, 52, 14.7, 0.066, { spectrum: [3.2, 8.9, 14.7] }),
    loop("graph_reachability", 52, 57, 58.2, 0.401, { spectrum: [10.3, 31.6, 58.2] }),
    loop("graph_reachability", 57, 62, 0, 0.92, { reversal: true }),
    loop("symbol_transport", 40, 46, 21.1, 0.143, { spectrum: [6.4, 21.1] }),
    loop("symbol_transport", 52, 57, 32.4, 0.238, { spectrum: [11.8, 32.4] })
  ];

  const certificates = [];
  for (const family of families) {
    for (const state of states) {
      for (const layer of layers) {
        const insecureLate = state === "insecure" && layer >= 57;
        const attained = insecureLate ? "engineering_evidence" : state === "insecure" ? "lineage_certified" : "holonomy_clean";
        certificates.push({
          site_id: node(state, layer, family),
          attained_level: attained,
          margins: {
            lineage: state === "base" ? 0.034 + (62 - layer) * 0.0004 : 0.006 - (layer - 40) * 0.0005,
            holonomy_budget_degrees: insecureLate ? -8.7 : state === "base" ? 9.5 : -1.8
          }
        });
      }
    }
  }

  window.GodelDemoData = {
    name: "Synthetic mixed-curvature demo",
    edges,
    loops,
    certificates,
    anchors: [],
    calibration: { bias_floor_degrees: 5 }
  };
}());
