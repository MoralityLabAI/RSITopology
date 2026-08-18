(function () {
  "use strict";

  const LEVELS = ["engineering_evidence", "lineage_certified", "holonomy_clean"];

  function finite(value, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? number : fallback;
  }

  function text(value, fallback) {
    return typeof value === "string" && value.trim() ? value.trim() : fallback;
  }

  function stableHash(value) {
    let hash = 2166136261;
    const input = String(value);
    for (let i = 0; i < input.length; i += 1) {
      hash ^= input.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function parseNodeId(nodeId) {
    const raw = text(nodeId, "unknown");
    const parts = raw.split("/").filter(Boolean);
    const stateToken = (parts[0] || "unknown").toLowerCase();
    const state = stateToken === "base" || stateToken === "insecure" ? stateToken : stateToken || "unknown";
    let layer = null;
    let layerIndex = -1;

    for (let i = 0; i < parts.length; i += 1) {
      const match = /^L(?:ayer)?[-_ ]?(\d+)$/i.exec(parts[i]);
      if (match) {
        layer = Number(match[1]);
        layerIndex = i;
        break;
      }
    }

    if (layer === null) {
      const match = /(?:^|[/_-])L(?:ayer)?[-_ ]?(\d+)(?:$|[/_-])/i.exec(raw);
      if (match) layer = Number(match[1]);
    }

    let family = "unknown";
    if (layerIndex >= 0 && parts[layerIndex + 1]) family = parts[layerIndex + 1];
    else if (parts.length > 1) family = parts[parts.length - 1];

    const shard = parts.find((part) => /^shard-\d+$/i.test(part)) || null;
    const rankPart = parts.find((part) => /^rank-\d+$/i.test(part));
    const rank = rankPart ? Number(rankPart.split("-")[1]) : null;
    return { id: raw, state, layer, family, context_shard: shard, rank };
  }

  function normalizeEdge(raw, line) {
    const edgeId = text(raw.edge_id, null);
    const source = text(raw.source_node, null);
    const target = text(raw.target_node, null);
    if (!edgeId || !source || !target) throw new Error(`Edge row ${line} is missing edge_id/source_node/target_node.`);
    return {
      edge_id: edgeId,
      source_node: source,
      target_node: target,
      mean_chordal_lineage: finite(raw.mean_chordal_lineage, 0),
      worst_direction_retention: finite(raw.worst_direction_retention ?? raw.minimum_edge_worst_direction_retention, 0),
      rank: Math.max(1, Math.round(finite(raw.rank, 1))),
      transport_hash: text(raw.transport_hash ?? raw.transport_sha256, "unavailable"),
      is_sae_path: Boolean(raw.is_sae_path),
      path_id: raw.path_id ? String(raw.path_id) : null,
      raw
    };
  }

  function normalizeLoop(raw, line) {
    const loopId = text(raw.loop_id, null);
    const edgeOrder = Array.isArray(raw.edge_order) ? raw.edge_order.map(String) : Array.isArray(raw.edge_ids) ? raw.edge_ids.map(String) : null;
    if (!loopId || !edgeOrder || edgeOrder.length < 2) throw new Error(`Loop row ${line} is missing loop_id or edge_order.`);
    const detH = finite(raw.det_h ?? raw.determinant, 1);
    const reversal = detH < 0 || Boolean(raw.orientation_flag ?? raw.det_h_flag);
    const angles = reversal || !Array.isArray(raw.canonical_angles_degrees)
      ? null
      : raw.canonical_angles_degrees.map((value) => finite(value, 0)).sort((a, b) => a - b);
    return {
      loop_id: loopId,
      root_node: text(raw.root_node, "unknown"),
      edge_order: edgeOrder,
      det_h: detH,
      canonical_angles_degrees: angles,
      identity_loss: finite(raw.identity_loss, 0),
      orientation_flag: reversal,
      basis_hashes: Array.isArray(raw.basis_hashes) ? raw.basis_hashes.map(String) : raw.basis_hashes ? [String(raw.basis_hashes)] : [],
      max_angle: angles && angles.length ? Math.max(...angles) : null,
      is_sae_path: Boolean(raw.is_sae_path),
      model_state: raw.model_state ? String(raw.model_state) : null,
      node_order: Array.isArray(raw.node_order) ? raw.node_order.map(String) : null,
      behavioral_hard_failure: Boolean(raw.behavioral_hard_failure),
      raw
    };
  }

  function normalizeCertificate(raw, line) {
    const siteId = text(raw.site_id, null);
    if (!siteId) throw new Error(`Certificate row ${line} is missing site_id.`);
    const proposed = text(raw.attained_level ?? raw.certification_level, "engineering_evidence");
    return {
      site_id: siteId,
      attained_level: LEVELS.includes(proposed) ? proposed : "engineering_evidence",
      margins: raw.margins && typeof raw.margins === "object" ? raw.margins : {},
      raw
    };
  }

  function parseJsonLines(content, normalizer, filename) {
    const rows = [];
    const errors = [];
    content.split(/\r?\n/).forEach((line, index) => {
      if (!line.trim()) return;
      try {
        const parsed = JSON.parse(line);
        rows.push(normalizer(parsed, index + 1));
      } catch (error) {
        errors.push(`${filename}:${index + 1}: ${error.message}`);
      }
    });
    if (errors.length) throw new Error(errors.slice(0, 5).join("\n"));
    return rows;
  }

  function classifyFile(name, firstObject) {
    const lower = name.toLowerCase();
    if (lower.includes("calibration")) return "calibration";
    if (lower.includes("edge")) return "edges";
    if (lower.includes("loop")) return "loops";
    if (lower.includes("anchor")) return "anchors";
    if (lower.includes("certificate")) return "certificates";
    if (firstObject && firstObject.edge_id && firstObject.source_node) return "edges";
    if (firstObject && firstObject.loop_id && (firstObject.edge_order || firstObject.edge_ids)) return "loops";
    if (firstObject && firstObject.site_id) return firstObject.attained_level || firstObject.certification_level ? "certificates" : "anchors";
    return "unknown";
  }

  function normalizeSaeBundle(raw, filename) {
    if (!raw || raw.schema_version !== "godel_sae_path_bundle_v1") {
      throw new Error(`${filename}: unsupported SAE path bundle schema.`);
    }
    const dimensions = Array.isArray(raw.dimensions) ? raw.dimensions : [];
    if (dimensions.length < 5 || dimensions.length > 15) {
      throw new Error(`${filename}: SAE path bundle requires 5-15 dimensions.`);
    }
    const dimensionIds = dimensions.map((row) => text(row.dimension_id, null));
    if (dimensionIds.some((value) => !value) || new Set(dimensionIds).size !== dimensionIds.length) {
      throw new Error(`${filename}: dimension ids must be non-empty and unique.`);
    }
    const rawNodes = Array.isArray(raw.nodes) ? raw.nodes : [];
    const rawPaths = Array.isArray(raw.paths) ? raw.paths : [];
    if (!rawNodes.length || !rawPaths.length) {
      throw new Error(`${filename}: SAE path bundle has no nodes or paths.`);
    }
    const nodeMetadata = new Map();
    rawNodes.forEach((node, index) => {
      const nodeId = text(node.node_id, null);
      const coordinates = Array.isArray(node.coordinates) ? node.coordinates.map((value) => finite(value, 0)) : [];
      if (!nodeId || coordinates.length !== dimensionIds.length) {
        throw new Error(`${filename}: SAE node ${index + 1} has an invalid id or coordinate vector.`);
      }
      if (nodeMetadata.has(nodeId)) throw new Error(`${filename}: duplicate SAE node ${nodeId}.`);
      nodeMetadata.set(nodeId, {
        state: text(node.model_state, "unknown"),
        layer: finite(node.layer, null),
        family: `${text(node.actor_id, "unknown")}--${text(node.route_id, "unknown")}`,
        sae_coordinates: coordinates,
        selected_action_alias: node.selected_action_alias ?? null,
        behavioral_hard_failure: Boolean(node.behavioral_hard_failure),
        causal_effect: node.causal_effect ?? null,
        activation_sha256: text(node.activation_sha256, "unavailable"),
        sae_sha256: text(node.sae_sha256, "unavailable"),
        variant: text(node.variant, "unknown"),
        item_id: text(node.item_id, "unknown"),
        path_id: text(node.path_id, "unknown"),
        raw: node
      });
    });

    const edges = [];
    const loops = [];
    rawPaths.forEach((path, pathIndex) => {
      const pathId = text(path.path_id, null);
      const nodeOrder = Array.isArray(path.node_order) ? path.node_order.map(String) : [];
      if (!pathId || nodeOrder.length < 2 || nodeOrder.some((id) => !nodeMetadata.has(id))) {
        throw new Error(`${filename}: SAE path ${pathIndex + 1} has invalid node_order.`);
      }
      const edgeOrder = [];
      for (let index = 0; index < nodeOrder.length - 1; index += 1) {
        const edgeId = `${pathId}::step-${index + 1}`;
        edgeOrder.push(edgeId);
        edges.push({
          edge_id: edgeId,
          source_node: nodeOrder[index],
          target_node: nodeOrder[index + 1],
          mean_chordal_lineage: 0.5,
          worst_direction_retention: 1,
          rank: 1,
          transport_hash: text(nodeMetadata.get(nodeOrder[index + 1]).activation_sha256, "unavailable"),
          is_sae_path: true,
          path_id: pathId,
          raw: {
            edge_id: edgeId,
            source_node: nodeOrder[index],
            target_node: nodeOrder[index + 1],
            mean_chordal_lineage: 0.5,
            worst_direction_retention: 1,
            rank: 1,
            transport_hash: text(nodeMetadata.get(nodeOrder[index + 1]).activation_sha256, "unavailable"),
            is_sae_path: true,
            path_id: pathId
          }
        });
      }
      const rootMetadata = nodeMetadata.get(nodeOrder[0]);
      loops.push({
        loop_id: pathId,
        root_node: nodeOrder[0],
        edge_order: edgeOrder,
        det_h: 1,
        canonical_angles_degrees: [],
        identity_loss: 0,
        orientation_flag: false,
        basis_hashes: nodeOrder.map((id) => nodeMetadata.get(id).sae_sha256),
        is_sae_path: true,
        model_state: text(path.model_state, rootMetadata.state),
        node_order: nodeOrder,
        behavioral_hard_failure: Boolean(path.behavioral_hard_failure),
        raw: {
          ...path,
          loop_id: pathId,
          root_node: nodeOrder[0],
          edge_order: edgeOrder,
          det_h: 1,
          canonical_angles_degrees: [],
          identity_loss: 0,
          orientation_flag: false,
          basis_hashes: nodeOrder.map((id) => nodeMetadata.get(id).sae_sha256),
          is_sae_path: true,
          model_state: text(path.model_state, rootMetadata.state),
          node_order: nodeOrder,
          behavioral_hard_failure: Boolean(path.behavioral_hard_failure)
        }
      });
    });
    const compiled = compile({
      name: text(raw.name, "SAE path bundle"),
      filenames: [filename],
      edges,
      loops,
      anchors: [],
      certificates: [],
      calibration: raw.calibration || {}
    });
    compiled.mode = "sae_paths";
    compiled.dimensions = dimensions;
    compiled.dimensionIds = dimensionIds;
    const proposedAxes = Array.isArray(raw.default_axes) ? raw.default_axes.map(String) : [];
    compiled.defaultAxes = proposedAxes.length === 3 && proposedAxes.every((id) => dimensionIds.includes(id))
      ? proposedAxes
      : dimensionIds.slice(0, 3);
    compiled.modelStates = Array.isArray(raw.model_states) ? raw.model_states.map(String) : [];
    compiled.paths = compiled.loops;
    compiled.source = raw.source || {};
    for (const node of compiled.nodes) Object.assign(node, nodeMetadata.get(node.id) || {});
    for (const path of compiled.paths) path.is_sae_path = true;
    return compiled;
  }

  async function readFiles(files) {
    const result = { name: "Loaded receipt bundle", edges: [], loops: [], anchors: [], certificates: [], calibration: {}, filenames: [] };
    for (const file of Array.from(files)) {
      const content = await file.text();
      let whole = null;
      try {
        whole = JSON.parse(content);
      } catch (_) {
        whole = null;
      }
      if (whole?.schema_version === "godel_sae_path_bundle_v1") {
        if (files.length !== 1) throw new Error("Load an SAE path bundle by itself.");
        return normalizeSaeBundle(whole, file.name);
      }
      let sample = null;
      try {
        sample = JSON.parse(content.trim().split(/\r?\n/)[0]);
      } catch (_) {
        sample = null;
      }
      const kind = classifyFile(file.name, sample);
      if (kind === "unknown") continue;
      result.filenames.push(file.name);
      if (kind === "calibration") {
        const parsed = JSON.parse(content);
        result.calibration.bias_floor_degrees = Math.max(0, finite(parsed.bias_floor_degrees, 0));
      } else if (kind === "edges") {
        result.edges.push(...parseJsonLines(content, normalizeEdge, file.name));
      } else if (kind === "loops") {
        result.loops.push(...parseJsonLines(content, normalizeLoop, file.name));
      } else {
        const normalized = parseJsonLines(content, normalizeCertificate, file.name);
        result[kind].push(...normalized);
      }
    }
    if (!result.edges.length) throw new Error("No edge receipts were found in the selected files.");
    if (!result.loops.length) throw new Error("No loop receipts were found in the selected files.");
    return compile(result);
  }

  function compile(input) {
    const edgeMap = new Map();
    const loopMap = new Map();
    const certificationMap = new Map();
    const warnings = [];

    const edges = input.edges.map((row, index) => row.raw ? row : normalizeEdge(row, index + 1));
    const loops = input.loops.map((row, index) => row.raw ? row : normalizeLoop(row, index + 1));
    const certRows = [...(input.anchors || []), ...(input.certificates || [])].map((row, index) => row.raw ? row : normalizeCertificate(row, index + 1));

    for (const edge of edges) {
      if (edgeMap.has(edge.edge_id)) warnings.push(`Duplicate edge_id ${edge.edge_id}; the first receipt is used.`);
      else edgeMap.set(edge.edge_id, edge);
    }
    for (const loop of loops) {
      if (loopMap.has(loop.loop_id)) warnings.push(`Duplicate loop_id ${loop.loop_id}; the first receipt is used.`);
      else loopMap.set(loop.loop_id, loop);
    }
    for (const cert of certRows) {
      const previous = certificationMap.get(cert.site_id);
      if (!previous || LEVELS.indexOf(cert.attained_level) > LEVELS.indexOf(previous.attained_level)) certificationMap.set(cert.site_id, cert);
    }

    const nodeMap = new Map();
    function addNode(id) {
      if (!nodeMap.has(id)) {
        const parsed = parseNodeId(id);
        const cert = certificationMap.get(id) || { attained_level: "engineering_evidence", margins: {} };
        nodeMap.set(id, { ...parsed, certification: cert.attained_level, margins: cert.margins, stable_hash: stableHash(id) });
      }
    }
    for (const edge of edgeMap.values()) {
      addNode(edge.source_node);
      addNode(edge.target_node);
    }
    for (const siteId of certificationMap.keys()) addNode(siteId);

    const validLoops = [];
    for (const loop of loopMap.values()) {
      const missing = loop.edge_order.filter((id) => !edgeMap.has(id));
      if (missing.length) {
        warnings.push(`Loop ${loop.loop_id} references missing edges: ${missing.join(", ")}.`);
        loop.invalid = true;
      }
      const root = nodeMap.get(loop.root_node);
      loop.family = root ? root.family : inferLoopFamily(loop, edgeMap, nodeMap);
      loop.states = inferLoopStates(loop, edgeMap, nodeMap);
      loop.ranks = Array.from(new Set(loop.edge_order.map((id) => edgeMap.get(id)?.rank).filter(Number.isFinite)));
      loop.rank = loop.ranks.length === 1 ? loop.ranks[0] : null;
      validLoops.push(loop);
    }

    const edgeValues = Array.from(edgeMap.values()).map((edge) => edge.mean_chordal_lineage);
    const lineageMin = edgeValues.length ? Math.min(...edgeValues) : 0;
    const lineageMax = edgeValues.length ? Math.max(...edgeValues) : 1;

    return {
      mode: "holonomy",
      name: input.name || "Receipt bundle",
      filenames: input.filenames || [],
      edges: Array.from(edgeMap.values()),
      loops: validLoops,
      nodes: Array.from(nodeMap.values()),
      edgeMap,
      nodeMap,
      calibration: input.calibration || {},
      warnings,
      ranges: { lineageMin, lineageMax }
    };
  }

  function inferLoopFamily(loop, edgeMap, nodeMap) {
    for (const edgeId of loop.edge_order) {
      const edge = edgeMap.get(edgeId);
      if (edge) return nodeMap.get(edge.source_node)?.family || "unknown";
    }
    return "unknown";
  }

  function inferLoopStates(loop, edgeMap, nodeMap) {
    const states = new Set();
    for (const edgeId of loop.edge_order) {
      const edge = edgeMap.get(edgeId);
      if (!edge) continue;
      states.add(nodeMap.get(edge.source_node)?.state || "unknown");
      states.add(nodeMap.get(edge.target_node)?.state || "unknown");
    }
    return Array.from(states);
  }

  window.GodelData = { compile, normalizeSaeBundle, readFiles, parseNodeId, stableHash, LEVELS };
}());
