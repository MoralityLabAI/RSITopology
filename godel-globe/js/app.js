(function () {
  "use strict";

  const elements = {};
  let globe = null;
  let data = null;
  let selectedLoop = null;

  function cacheElements() {
    [
      "load-status", "file-picker", "family-filter", "rank-filter", "state-filter", "node-search",
      "loop-list", "loop-count", "loop-details", "loop-badge", "dataset-name", "dataset-stats",
      "legend-min", "legend-mid", "legend-max", "drop-zone", "tooltip", "about-dialog", "about-button", "about-close"
    ].forEach((id) => { elements[id] = document.getElementById(id); });
  }

  function setStatus(message, error) {
    elements["load-status"].textContent = message;
    elements["load-status"].classList.toggle("error", Boolean(error));
  }

  function loadDataset(nextData) {
    data = nextData.edgeMap && nextData.nodeMap
      ? nextData
      : window.GodelData.compile(nextData.raw || nextData);
    selectedLoop = null;
    populateFilters();
    globe.setData(data);
    updateLegend();
    updateDatasetSummary();
    applyFilters();
    renderLoopDetails(null);
    const warningText = data.warnings.length ? ` · ${data.warnings.length} warning${data.warnings.length === 1 ? "" : "s"}` : "";
    setStatus(`Loaded ${data.nodes.length} nodes · ${data.edges.length} edges · ${data.loops.length} loops${warningText}`, false);
  }

  function populateFilters() {
    const families = Array.from(new Set(data.nodes.map((node) => node.family))).sort();
    const ranks = Array.from(new Set(data.edges.map((edge) => edge.rank))).sort((a, b) => a - b);
    fillSelect(elements["family-filter"], [{ value: "all", label: "All families" }, ...families.map((family) => ({ value: family, label: humanize(family) }))]);
    fillSelect(elements["rank-filter"], [{ value: "all", label: "All ranks" }, ...ranks.map((rank) => ({ value: String(rank), label: `Rank ${rank}` }))]);
  }

  function fillSelect(select, options) {
    const previous = select.value;
    select.replaceChildren(...options.map((option) => {
      const element = document.createElement("option");
      element.value = option.value;
      element.textContent = option.label;
      return element;
    }));
    if (options.some((option) => option.value === previous)) select.value = previous;
  }

  function humanize(value) {
    return String(value).replace(/[_/-]+/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
  }

  function currentFilters() {
    return {
      family: elements["family-filter"].value,
      rank: elements["rank-filter"].value,
      state: elements["state-filter"].value,
      search: elements["node-search"].value.trim()
    };
  }

  function loopVisible(loop, filters) {
    if (loop.invalid) return false;
    if (filters.family !== "all" && loop.family !== filters.family) return false;
    if (filters.rank !== "all" && loop.rank !== Number(filters.rank)) return false;
    if (filters.state !== "both" && !loop.states.every((state) => state === filters.state)) return false;
    if (filters.search) {
      const query = filters.search.toLowerCase();
      return loop.edge_order.some((edgeId) => {
        const edge = data.edgeMap.get(edgeId);
        return edge && (edge.source_node.toLowerCase().includes(query) || edge.target_node.toLowerCase().includes(query));
      });
    }
    return true;
  }

  function applyFilters() {
    if (!data || !globe) return;
    const filters = currentFilters();
    globe.setFilters(filters);
    renderLoopList(filters);
  }

  function renderLoopList(filters) {
    const visible = data.loops.filter((loop) => loopVisible(loop, filters)).sort((a, b) => {
      if (a.max_angle === null && b.max_angle === null) return a.loop_id.localeCompare(b.loop_id);
      if (a.max_angle === null) return 1;
      if (b.max_angle === null) return -1;
      return b.max_angle - a.max_angle || a.loop_id.localeCompare(b.loop_id);
    });
    elements["loop-count"].textContent = String(visible.length);
    const floor = Number(data.calibration.bias_floor_degrees || 0);
    const fragment = document.createDocumentFragment();
    for (const loop of visible) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `loop-item${selectedLoop?.loop_id === loop.loop_id ? " selected" : ""}`;
      button.setAttribute("role", "option");
      button.setAttribute("aria-selected", selectedLoop?.loop_id === loop.loop_id ? "true" : "false");
      button.dataset.loopId = loop.loop_id;
      const label = document.createElement("span");
      label.className = "loop-name";
      label.textContent = loop.loop_id;
      const sub = document.createElement("span");
      sub.className = "loop-sub";
      sub.textContent = `${humanize(loop.family)} · ${loop.rank ? `rank ${loop.rank}` : "mixed rank"}`;
      label.appendChild(sub);
      const angle = document.createElement("span");
      angle.className = "loop-angle";
      if (loop.orientation_flag) {
        angle.classList.add("reversal");
        angle.textContent = "det<0";
      } else if (loop.max_angle < floor) {
        angle.classList.add("flat");
        angle.textContent = `${format(loop.max_angle, 1)}°`;
      } else {
        angle.textContent = `${format(loop.max_angle, 1)}°`;
      }
      button.append(label, angle);
      button.addEventListener("click", () => selectLoop(loop, true));
      fragment.appendChild(button);
    }
    elements["loop-list"].replaceChildren(fragment);
  }

  function selectLoop(loop, play) {
    selectedLoop = loop;
    globe.selectLoop(loop, play);
    renderLoopList(currentFilters());
    renderLoopDetails(loop);
  }

  function renderLoopDetails(loop) {
    const container = elements["loop-details"];
    const badge = elements["loop-badge"];
    if (!loop) {
      badge.className = "badge badge-neutral";
      badge.textContent = "No selection";
      container.className = "details empty-details";
      container.textContent = "Select a measured loop to inspect its closure receipt and play the measured transport.";
      return;
    }

    container.className = "details";
    const floor = Number(data.calibration.bias_floor_degrees || 0);
    const belowFloor = loop.max_angle !== null && loop.max_angle < floor;
    if (loop.orientation_flag) {
      badge.className = "badge badge-danger";
      badge.textContent = "Orientation reversal";
    } else if (belowFloor) {
      badge.className = "badge badge-flat";
      badge.textContent = "Within floor";
    } else {
      badge.className = "badge badge-clean";
      badge.textContent = "Measured rotation";
    }

    const hashes = [];
    loop.basis_hashes.forEach((hash, index) => hashes.push({ label: `Basis ${index + 1}`, hash }));
    loop.edge_order.forEach((edgeId) => {
      const edge = data.edgeMap.get(edgeId);
      if (edge?.transport_hash) hashes.push({ label: edgeId, hash: edge.transport_hash });
    });

    const angleSection = loop.orientation_flag
      ? `<div class="reversal-notice"><strong>Orientation reversal.</strong> Angle data is suppressed by receipt convention and no transport animation is permitted.</div>`
      : `${belowFloor ? `<div class="flat-notice">Flat within the ${format(floor, 2)}° instrument floor. The receipt remains visible, but animation emphasis is suppressed.</div>` : ""}
        <div class="detail-section"><h3>Canonical angle spectrum</h3>${angleChart(loop.canonical_angles_degrees || [])}</div>`;

    container.innerHTML = `
      <div class="detail-title">${escapeHtml(loop.loop_id)}</div>
      <div class="detail-root">Root fiber: ${escapeHtml(loop.root_node)}</div>
      <div class="detail-grid">
        <div class="metric"><span class="metric-label">det(H)</span><span class="metric-value">${format(loop.det_h, 6)}</span></div>
        <div class="metric"><span class="metric-label">Identity loss</span><span class="metric-value">${format(loop.identity_loss, 6)}</span></div>
        <div class="metric"><span class="metric-label">Max angle</span><span class="metric-value">${loop.max_angle === null ? "suppressed" : `${format(loop.max_angle, 3)}°`}</span></div>
        <div class="metric"><span class="metric-label">Rank</span><span class="metric-value">${loop.rank || "mixed"}</span></div>
      </div>
      ${!loop.orientation_flag && !belowFloor ? `<button id="replay-transport" class="button button-primary" type="button">Replay measured transport</button>` : ""}
      ${angleSection}
      <div class="detail-section"><h3>Edge order</h3><ol class="edge-order">${loop.edge_order.map((edgeId) => `<li>${escapeHtml(edgeId)}</li>`).join("")}</ol></div>
      <div class="detail-section"><h3>Receipt hashes</h3><div class="hash-list">${hashes.map((item, index) => hashRow(item, index)).join("") || "<span>No hashes supplied.</span>"}</div></div>
    `;

    const replay = document.getElementById("replay-transport");
    if (replay) replay.addEventListener("click", () => globe.playLoop(loop));
    container.querySelectorAll("[data-copy-hash]").forEach((button) => {
      button.addEventListener("click", async () => {
        const hash = button.dataset.copyHash;
        await copyText(hash);
        button.textContent = "Copied";
        setTimeout(() => { button.textContent = "Copy"; }, 1100);
      });
    });
  }

  function angleChart(angles) {
    if (!angles.length) return "<span>No canonical angles supplied.</span>";
    const max = Math.max(1, ...angles);
    return `<div class="angle-chart">${angles.map((angle, index) => `
      <div class="angle-row">
        <span>θ${index + 1}</span>
        <div class="angle-track"><div class="angle-fill" style="width:${Math.max(1.5, angle / max * 100)}%"></div></div>
        <span class="angle-value">${format(angle, 2)}°</span>
      </div>`).join("")}</div>`;
  }

  function hashRow(item, index) {
    const full = String(item.hash);
    const truncated = full.length > 22 ? `${full.slice(0, 10)}…${full.slice(-10)}` : full;
    return `<div class="hash-row"><code title="${escapeHtml(item.label)}">${escapeHtml(truncated)}</code><button class="button copy-button" type="button" data-copy-hash="${escapeHtml(full)}" aria-label="Copy ${escapeHtml(item.label)} hash">Copy</button></div>`;
  }

  async function copyText(value) {
    try {
      await navigator.clipboard.writeText(value);
    } catch (_) {
      const textarea = document.createElement("textarea");
      textarea.value = value;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
  }

  function updateLegend() {
    const min = data.ranges.lineageMin;
    const max = data.ranges.lineageMax;
    elements["legend-min"].textContent = format(min, 3);
    elements["legend-mid"].textContent = format((min + max) / 2, 3);
    elements["legend-max"].textContent = format(max, 3);
  }

  function updateDatasetSummary() {
    elements["dataset-name"].textContent = data.name;
    const floor = Number(data.calibration.bias_floor_degrees || 0);
    elements["dataset-stats"].textContent = `${data.nodes.length} nodes · ${data.edges.length} edges · ${data.loops.length} loops · floor ${format(floor, 2)}°`;
  }

  function handleHover(kind, value, event) {
    const tooltip = elements.tooltip;
    if (!kind || !value || !event) {
      tooltip.hidden = true;
      return;
    }
    if (kind === "node") {
      const margins = Object.entries(value.margins || {}).map(([key, margin]) => `${escapeHtml(key)}: ${format(Number(margin), 4)}`).join(" · ");
      tooltip.innerHTML = `<strong>${escapeHtml(value.id)}</strong><span>${humanize(value.certification)}</span>${margins ? `<span>${margins}</span>` : ""}`;
    } else if (kind === "edge") {
      tooltip.innerHTML = `<strong>${escapeHtml(value.edge_id)}</strong><span>lineage ${format(value.mean_chordal_lineage, 4)} · worst retention ${format(value.worst_direction_retention, 4)} · rank ${value.rank}</span>`;
    } else {
      tooltip.innerHTML = `<strong>${escapeHtml(value.loop_id)}</strong><span>${value.orientation_flag ? "orientation reversal" : `max angle ${format(value.max_angle, 3)}°`} · identity loss ${format(value.identity_loss, 5)}</span>`;
    }
    tooltip.hidden = false;
    const wrap = elements["drop-zone"].getBoundingClientRect();
    const x = Math.min(wrap.width - 295, Math.max(8, event.clientX - wrap.left + 13));
    const y = Math.min(wrap.height - 90, Math.max(8, event.clientY - wrap.top + 13));
    tooltip.style.left = `${x}px`;
    tooltip.style.top = `${y}px`;
  }

  async function handleFiles(fileList) {
    if (!fileList || !fileList.length) return;
    setStatus("Reading receipt files…", false);
    try {
      const loaded = await window.GodelData.readFiles(fileList);
      loaded.name = loaded.filenames.length ? loaded.filenames.join(" + ") : "Loaded receipt bundle";
      loadDataset(loaded);
    } catch (error) {
      console.error(error);
      setStatus(error.message, true);
    } finally {
      elements["file-picker"].value = "";
    }
  }

  function bindUi() {
    elements["file-picker"].addEventListener("change", (event) => handleFiles(event.target.files));
    ["family-filter", "rank-filter", "state-filter"].forEach((id) => elements[id].addEventListener("change", applyFilters));
    let searchTimer = 0;
    elements["node-search"].addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(applyFilters, 100);
    });

    const dropZone = elements["drop-zone"];
    ["dragenter", "dragover"].forEach((type) => dropZone.addEventListener(type, (event) => {
      event.preventDefault();
      dropZone.classList.add("dragover");
    }));
    ["dragleave", "drop"].forEach((type) => dropZone.addEventListener(type, (event) => {
      event.preventDefault();
      if (type === "drop") handleFiles(event.dataTransfer.files);
      dropZone.classList.remove("dragover");
    }));

    elements["about-button"].addEventListener("click", () => elements["about-dialog"].showModal());
    elements["about-close"].addEventListener("click", () => elements["about-dialog"].close());
    elements["about-dialog"].addEventListener("click", (event) => {
      if (event.target === elements["about-dialog"]) elements["about-dialog"].close();
    });
  }

  function format(value, digits) {
    return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : "—";
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
  }

  function start(deps) {
    cacheElements();
    bindUi();
    try {
      globe = new window.GodelGlobeRenderer.GodelGlobe(document.getElementById("globe-canvas"), deps, {
        onHover: handleHover,
        onLoopSelect: (loop) => selectLoop(loop, true)
      });
      loadDataset(window.GodelDemoData);
    } catch (error) {
      console.error(error);
      setStatus(`Renderer error: ${error.message}`, true);
    }
  }

  window.addEventListener("godel-three-ready", (event) => start(event.detail), { once: true });
}());
