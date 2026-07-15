(function () {
  "use strict";

  class GodelGlobe {
    constructor(canvas, deps, callbacks) {
      this.canvas = canvas;
      this.THREE = deps.THREE;
      this.deps = deps;
      this.callbacks = callbacks || {};
      this.data = null;
      this.filters = { family: "all", rank: "all", state: "both", search: "" };
      this.nodePositions = new Map();
      this.edgePaths = new Map();
      this.loopPaths = new Map();
      this.edgePickMap = [];
      this.loopPickMap = [];
      this.lineMaterials = [];
      this.selectedLoop = null;
      this.hoverRaf = 0;
      this.pendingPointer = null;
      this.animation = null;
      this.lastTime = performance.now();
      this.motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
      this.reducedMotion = this.motionQuery.matches;
      this.motionQuery.addEventListener("change", (event) => { this.reducedMotion = event.matches; });

      const THREE = this.THREE;
      this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
      this.renderer.outputColorSpace = THREE.SRGBColorSpace;
      this.renderer.setClearColor(0x000000, 0);

      this.scene = new THREE.Scene();
      this.scene.fog = new THREE.FogExp2(0x050812, 0.012);
      this.camera = new THREE.PerspectiveCamera(42, 1, 0.1, 120);
      this.camera.position.set(0, 2, 30);

      this.controls = new deps.OrbitControls(this.camera, canvas);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.06;
      this.controls.enablePan = false;
      this.controls.minDistance = 16;
      this.controls.maxDistance = 52;
      this.controlsActive = false;
      this.controls.addEventListener("start", () => { this.controlsActive = true; });
      this.controls.addEventListener("end", () => { this.controlsActive = false; });

      this.root = new THREE.Group();
      this.scene.add(this.root);
      this.graphRoot = new THREE.Group();
      this.root.add(this.graphRoot);

      this.scene.add(new THREE.AmbientLight(0x9ebaff, 0.65));
      const key = new THREE.DirectionalLight(0xc6f4ff, 2.2);
      key.position.set(7, 10, 12);
      this.scene.add(key);
      const rim = new THREE.PointLight(0x7658ff, 26, 55);
      rim.position.set(-12, -5, -10);
      this.scene.add(rim);

      this.raycaster = new THREE.Raycaster();
      this.raycaster.params.Line.threshold = 0.24;
      this.pointer = new THREE.Vector2(2, 2);

      this.scratch = {
        matrix: new THREE.Matrix4(),
        scale: new THREE.Vector3(),
        quat: new THREE.Quaternion(),
        quat2: new THREE.Quaternion(),
        axis: new THREE.Vector3(),
        position: new THREE.Vector3(),
        position2: new THREE.Vector3(),
        color: new THREE.Color(),
        hidden: new THREE.Matrix4().makeScale(0, 0, 0)
      };

      this.resizeObserver = new ResizeObserver(() => this.resize());
      this.resizeObserver.observe(canvas.parentElement);
      canvas.addEventListener("pointermove", (event) => this.onPointerMove(event));
      canvas.addEventListener("pointerleave", () => this.emitHover(null, null));
      canvas.addEventListener("click", (event) => this.onClick(event));

      this.resize();
      this.renderLoop = this.renderLoop.bind(this);
      requestAnimationFrame(this.renderLoop);
    }

    disposeObject(object) {
      object.traverse((child) => {
        if (child.geometry) child.geometry.dispose();
        if (Array.isArray(child.material)) child.material.forEach((material) => material.dispose());
        else if (child.material) child.material.dispose();
      });
    }

    clearData() {
      this.disposeObject(this.graphRoot);
      this.root.remove(this.graphRoot);
      this.graphRoot = new this.THREE.Group();
      this.root.add(this.graphRoot);
      this.nodePositions.clear();
      this.edgePaths.clear();
      this.loopPaths.clear();
      this.edgePickMap = [];
      this.loopPickMap = [];
      this.lineMaterials = [];
      this.selectedLoop = null;
      this.animation = null;
      this.nodeMesh = null;
      this.nodeHaloMesh = null;
      this.edgePickMesh = null;
      this.loopPickMesh = null;
      this.selectedLine = null;
      this.triad = null;
    }

    setData(data) {
      this.clearData();
      this.data = data;
      this.createShells();
      this.computeNodePositions();
      this.createSwirls();
      this.createNodes();
      this.computeEdgePaths();
      this.rebuildVisibleGeometry();
      this.fitCamera();
    }

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
      if (!this.data) return;
      this.updateNodeInstances();
      this.rebuildVisibleGeometry();
      if (this.selectedLoop && !this.isLoopVisible(this.selectedLoop)) this.selectLoop(null, false);
    }

    shellRadius(state) {
      if (state === "base") return 9.4;
      if (state === "insecure") return 11.15;
      const hash = window.GodelData.stableHash(state);
      return 10.15 + (hash % 5) * 0.32;
    }

    createShells() {
      const THREE = this.THREE;
      const states = new Set(this.data.nodes.map((node) => node.state));
      for (const state of states) {
        const geometry = new THREE.SphereGeometry(this.shellRadius(state), 48, 32);
        const material = new THREE.MeshPhysicalMaterial({
          color: state === "insecure" ? 0x6547aa : 0x2d7896,
          emissive: state === "insecure" ? 0x160b30 : 0x061e2c,
          transparent: true,
          opacity: state === "insecure" ? 0.035 : 0.05,
          roughness: 0.8,
          metalness: 0.05,
          depthWrite: false,
          side: THREE.DoubleSide
        });
        const shell = new THREE.Mesh(geometry, material);
        shell.renderOrder = -4;
        this.graphRoot.add(shell);

        const wire = new THREE.Mesh(
          new THREE.SphereGeometry(this.shellRadius(state) + 0.012, 24, 16),
          new THREE.MeshBasicMaterial({ color: 0x87b8d8, wireframe: true, transparent: true, opacity: 0.026, depthWrite: false })
        );
        wire.renderOrder = -3;
        this.graphRoot.add(wire);
      }
    }

    computeNodePositions() {
      const THREE = this.THREE;
      const numericLayers = this.data.nodes.map((node) => node.layer).filter(Number.isFinite);
      const minLayer = numericLayers.length ? Math.min(...numericLayers) : 0;
      const maxLayer = numericLayers.length ? Math.max(...numericLayers) : 1;
      const families = Array.from(new Set(this.data.nodes.map((node) => node.family))).sort();
      const familyIndex = new Map(families.map((family, index) => [family, index]));

      for (const node of this.data.nodes) {
        const t = Number.isFinite(node.layer) && maxLayer !== minLayer ? (node.layer - minLayer) / (maxLayer - minLayer) : 0.5;
        const latitude = -Math.PI * 0.31 + t * Math.PI * 0.62;
        const index = familyIndex.get(node.family) || 0;
        const familyAngle = families.length > 1 ? (index / families.length) * Math.PI * 2 : 0;
        const jitter = (((node.stable_hash % 1000) / 999) - 0.5) * Math.min(0.38, Math.PI / Math.max(6, families.length * 2));
        const stateOffset = node.state === "insecure" ? 0.07 : node.state === "base" ? -0.07 : 0;
        const longitude = familyAngle + jitter + stateOffset;
        const radius = this.shellRadius(node.state) + 0.12;
        const cosLat = Math.cos(latitude);
        const position = new THREE.Vector3(
          radius * cosLat * Math.cos(longitude),
          radius * Math.sin(latitude),
          radius * cosLat * Math.sin(longitude)
        );
        this.nodePositions.set(node.id, position);
        node.position = position;
      }
    }

    createSwirls() {
      const THREE = this.THREE;
      const positions = [];
      const colors = [];
      const color = new THREE.Color(0x7e83ff);
      const count = 14;
      const steps = 180;
      for (let line = 0; line < count; line += 1) {
        const phase = (line / count) * Math.PI * 2;
        const radius = 11.55 + (line % 3) * 0.08;
        for (let i = 0; i < steps - 1; i += 1) {
          const a = i / (steps - 1);
          const b = (i + 1) / (steps - 1);
          this.pushSwirlPoint(positions, colors, color, radius, phase, a);
          this.pushSwirlPoint(positions, colors, color, radius, phase, b);
        }
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
      const material = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.07, blending: THREE.AdditiveBlending, depthWrite: false });
      const lines = new THREE.LineSegments(geometry, material);
      lines.renderOrder = -1;
      this.graphRoot.add(lines);
    }

    pushSwirlPoint(positions, colors, color, radius, phase, t) {
      const theta = t * Math.PI * 2;
      const latitude = 0.18 * Math.sin(theta * 2 + phase) + 0.06 * Math.sin(theta * 5 - phase);
      const twist = theta + phase + 0.38 * Math.sin(theta + phase);
      const cosLat = Math.cos(latitude);
      positions.push(radius * cosLat * Math.cos(twist), radius * Math.sin(latitude), radius * cosLat * Math.sin(twist));
      const fade = 0.42 + 0.58 * Math.sin(Math.PI * t);
      colors.push(color.r * fade, color.g * fade, color.b * fade);
    }

    certificationColor(level, target) {
      if (level === "holonomy_clean") return target.setHex(0x55e69d);
      if (level === "lineage_certified") return target.setHex(0xffbd59);
      return target.setHex(0x7d8ba5);
    }

    createNodes() {
      const THREE = this.THREE;
      const geometry = new THREE.IcosahedronGeometry(0.13, 1);
      const material = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.35, metalness: 0.25 });
      this.nodeMesh = new THREE.InstancedMesh(geometry, material, this.data.nodes.length);
      this.nodeMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
      this.nodeMesh.userData.kind = "nodes";
      this.nodeMesh.frustumCulled = false;

      const haloGeometry = new THREE.IcosahedronGeometry(0.24, 1);
      const haloMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.24, blending: THREE.AdditiveBlending, depthWrite: false });
      this.nodeHaloMesh = new THREE.InstancedMesh(haloGeometry, haloMaterial, this.data.nodes.length);
      this.nodeHaloMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
      this.nodeHaloMesh.frustumCulled = false;
      this.nodeHaloMesh.raycast = function () {};

      this.data.nodes.forEach((node, index) => {
        node.instanceId = index;
        this.certificationColor(node.certification, this.scratch.color);
        this.nodeMesh.setColorAt(index, this.scratch.color);
        this.nodeHaloMesh.setColorAt(index, this.scratch.color);
      });
      this.nodeMesh.instanceColor.needsUpdate = true;
      this.nodeHaloMesh.instanceColor.needsUpdate = true;
      this.graphRoot.add(this.nodeHaloMesh, this.nodeMesh);
      this.updateNodeInstances();
    }

    nodeMatchesFilters(node) {
      if (this.filters.family !== "all" && node.family !== this.filters.family) return false;
      if (this.filters.state !== "both" && node.state !== this.filters.state) return false;
      if (this.filters.search && !node.id.toLowerCase().includes(this.filters.search.toLowerCase())) return false;
      return true;
    }

    updateNodeInstances() {
      if (!this.nodeMesh) return;
      const THREE = this.THREE;
      const matrix = this.scratch.matrix;
      const scale = this.scratch.scale;
      const quat = this.scratch.quat.identity();
      for (const node of this.data.nodes) {
        if (!this.nodeMatchesFilters(node)) {
          this.nodeMesh.setMatrixAt(node.instanceId, this.scratch.hidden);
          this.nodeHaloMesh.setMatrixAt(node.instanceId, this.scratch.hidden);
          continue;
        }
        const emphasized = this.filters.search ? 1.35 : 1;
        scale.setScalar(emphasized);
        matrix.compose(node.position, quat, scale);
        this.nodeMesh.setMatrixAt(node.instanceId, matrix);
        scale.setScalar(emphasized * 1.15);
        matrix.compose(node.position, quat, scale);
        this.nodeHaloMesh.setMatrixAt(node.instanceId, matrix);
      }
      this.nodeMesh.instanceMatrix.needsUpdate = true;
      this.nodeHaloMesh.instanceMatrix.needsUpdate = true;
    }

    computeEdgePaths() {
      for (const edge of this.data.edges) {
        const source = this.nodePositions.get(edge.source_node);
        const target = this.nodePositions.get(edge.target_node);
        if (!source || !target) continue;
        this.edgePaths.set(edge.edge_id, this.makeArc(source, target, 9));
      }
      for (const loop of this.data.loops) this.loopPaths.set(loop.loop_id, this.buildLoopPath(loop));
    }

    makeArc(source, target, segments) {
      const THREE = this.THREE;
      const points = new Array(segments + 1);
      const sourceRadius = source.length();
      const targetRadius = target.length();
      const separation = source.angleTo(target);
      const lift = 0.25 + separation * 0.9 + Math.abs(sourceRadius - targetRadius) * 0.12;
      for (let i = 0; i <= segments; i += 1) {
        const t = i / segments;
        const direction = new THREE.Vector3().copy(source).normalize().lerp(new THREE.Vector3().copy(target).normalize(), t).normalize();
        const radius = sourceRadius + (targetRadius - sourceRadius) * t + Math.sin(Math.PI * t) * lift;
        points[i] = direction.multiplyScalar(radius);
      }
      return points;
    }

    buildLoopPath(loop) {
      if (loop.invalid) return [];
      const points = [];
      let current = loop.root_node;
      for (const edgeId of loop.edge_order) {
        const edge = this.data.edgeMap.get(edgeId);
        const path = this.edgePaths.get(edgeId);
        if (!edge || !path) continue;
        let oriented;
        if (edge.source_node === current) {
          oriented = path;
          current = edge.target_node;
        } else if (edge.target_node === current) {
          oriented = path.slice().reverse();
          current = edge.source_node;
        } else {
          const currentPosition = this.nodePositions.get(current);
          const sourceDistance = currentPosition ? currentPosition.distanceToSquared(path[0]) : 0;
          const targetDistance = currentPosition ? currentPosition.distanceToSquared(path[path.length - 1]) : 1;
          oriented = sourceDistance <= targetDistance ? path : path.slice().reverse();
          current = sourceDistance <= targetDistance ? edge.target_node : edge.source_node;
        }
        if (points.length) points.push(...oriented.slice(1));
        else points.push(...oriented);
      }
      if (points.length > 2 && !points[0].equals(points[points.length - 1])) points.push(points[0].clone());
      return points;
    }

    edgeVisible(edge) {
      const source = this.data.nodeMap.get(edge.source_node);
      const target = this.data.nodeMap.get(edge.target_node);
      if (!source || !target || !this.nodeMatchesFilters(source) || !this.nodeMatchesFilters(target)) return false;
      if (this.filters.rank !== "all" && edge.rank !== Number(this.filters.rank)) return false;
      return true;
    }

    isLoopVisible(loop) {
      if (loop.invalid) return false;
      if (this.filters.family !== "all" && loop.family !== this.filters.family) return false;
      if (this.filters.rank !== "all" && loop.rank !== Number(this.filters.rank)) return false;
      if (this.filters.state !== "both" && !loop.states.every((state) => state === this.filters.state)) return false;
      if (this.filters.search) {
        const query = this.filters.search.toLowerCase();
        const touches = loop.edge_order.some((edgeId) => {
          const edge = this.data.edgeMap.get(edgeId);
          return edge && (edge.source_node.toLowerCase().includes(query) || edge.target_node.toLowerCase().includes(query));
        });
        if (!touches) return false;
      }
      return loop.edge_order.every((edgeId) => {
        const edge = this.data.edgeMap.get(edgeId);
        return edge && this.edgeVisible(edge);
      });
    }

    lineageColor(value, target) {
      const min = this.data.ranges.lineageMin;
      const max = this.data.ranges.lineageMax;
      const t = max > min ? Math.max(0, Math.min(1, (value - min) / (max - min))) : 1;
      if (t < 0.5) return target.setRGB(1, 0.325 + t * 0.92, 0.431 - t * 0.12);
      const u = (t - 0.5) * 2;
      return target.setRGB(1 - u * 0.667, 0.79 + u * 0.112, 0.384 + u * 0.243);
    }

    rebuildVisibleGeometry() {
      this.removeNamed("selected-loop");
      this.removeNamed("transport-triad");
      this.removeNamed("edge-lines");
      this.removeNamed("edge-picker");
      this.removeNamed("loop-lines");
      this.removeNamed("loop-reversals");
      this.removeNamed("loop-picker");
      this.animation = null;
      this.selectedLine = null;
      this.triad = null;
      this.edgePickMap = [];
      this.loopPickMap = [];
      this.buildEdges();
      this.buildLoops();
      if (this.selectedLoop) this.drawSelectedLoop(this.selectedLoop);
    }

    removeNamed(name) {
      const object = this.graphRoot.getObjectByName(name);
      if (!object) return;
      const ownedMaterials = new Set();
      object.traverse((child) => {
        if (Array.isArray(child.material)) child.material.forEach((material) => ownedMaterials.add(material));
        else if (child.material) ownedMaterials.add(child.material);
      });
      this.lineMaterials = this.lineMaterials.filter((material) => !ownedMaterials.has(material));
      this.disposeObject(object);
      this.graphRoot.remove(object);
    }

    buildEdges() {
      const THREE = this.THREE;
      const bins = Array.from({ length: 5 }, () => ({ positions: [], colors: [] }));
      const pickPositions = [];
      const visible = this.data.edges.filter((edge) => this.edgeVisible(edge));
      for (const edge of visible) {
        const path = this.edgePaths.get(edge.edge_id);
        if (!path) continue;
        const bin = Math.max(0, Math.min(4, Math.floor(edge.worst_direction_retention * 5)));
        this.lineageColor(edge.mean_chordal_lineage, this.scratch.color);
        for (let i = 0; i < path.length - 1; i += 1) {
          const a = path[i];
          const b = path[i + 1];
          bins[bin].positions.push(a.x, a.y, a.z, b.x, b.y, b.z);
          bins[bin].colors.push(this.scratch.color.r, this.scratch.color.g, this.scratch.color.b, this.scratch.color.r, this.scratch.color.g, this.scratch.color.b);
          pickPositions.push(a.x, a.y, a.z, b.x, b.y, b.z);
          this.edgePickMap.push(edge);
        }
      }

      const edgeGroup = new THREE.Group();
      edgeGroup.name = "edge-lines";
      bins.forEach((bin, index) => {
        if (!bin.positions.length) return;
        const geometry = new this.deps.LineSegmentsGeometry();
        geometry.setPositions(bin.positions);
        geometry.setColors(bin.colors);
        const material = new this.deps.LineMaterial({
          color: 0xffffff,
          vertexColors: true,
          linewidth: 0.75 + index * 0.55,
          worldUnits: false,
          transparent: true,
          opacity: 0.74,
          depthWrite: false
        });
        material.resolution.set(this.canvas.clientWidth, this.canvas.clientHeight);
        this.lineMaterials.push(material);
        const line = new this.deps.LineSegments2(geometry, material);
        line.computeLineDistances();
        line.renderOrder = 1;
        edgeGroup.add(line);
      });
      this.graphRoot.add(edgeGroup);

      if (pickPositions.length) {
        const pickGeometry = new THREE.BufferGeometry();
        pickGeometry.setAttribute("position", new THREE.Float32BufferAttribute(pickPositions, 3));
        const pickMaterial = new THREE.LineBasicMaterial({ transparent: true, opacity: 0, depthWrite: false });
        this.edgePickMesh = new THREE.LineSegments(pickGeometry, pickMaterial);
        this.edgePickMesh.name = "edge-picker";
        this.edgePickMesh.userData.kind = "edges";
        this.graphRoot.add(this.edgePickMesh);
      }
    }

    buildLoops() {
      const THREE = this.THREE;
      const normalPositions = [];
      const normalColors = [];
      const reversalPositions = [];
      const pickPositions = [];
      const floor = Number(this.data.calibration.bias_floor_degrees || 0);
      const visibleLoops = this.data.loops.filter((loop) => this.isLoopVisible(loop));

      for (const loop of visibleLoops) {
        const path = this.loopPaths.get(loop.loop_id) || [];
        const belowFloor = loop.max_angle !== null && loop.max_angle < floor;
        loop.below_floor = belowFloor;
        for (let i = 0; i < path.length - 1; i += 1) {
          const a = path[i];
          const b = path[i + 1];
          pickPositions.push(a.x, a.y, a.z, b.x, b.y, b.z);
          this.loopPickMap.push(loop);
          if (loop.orientation_flag) {
            if (i % 2 === 0) reversalPositions.push(a.x, a.y, a.z, b.x, b.y, b.z);
          } else {
            normalPositions.push(a.x, a.y, a.z, b.x, b.y, b.z);
            const color = belowFloor ? [0.28, 0.42, 0.5] : [0.46, 0.76, 1.0];
            normalColors.push(...color, ...color);
          }
        }
      }

      if (normalPositions.length) {
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(normalPositions, 3));
        geometry.setAttribute("color", new THREE.Float32BufferAttribute(normalColors, 3));
        const material = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.34, blending: THREE.AdditiveBlending, depthWrite: false });
        const lines = new THREE.LineSegments(geometry, material);
        lines.name = "loop-lines";
        lines.renderOrder = 2;
        this.graphRoot.add(lines);
      }
      if (reversalPositions.length) {
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(reversalPositions, 3));
        const material = new THREE.LineBasicMaterial({ color: 0xff304f, transparent: true, opacity: 0.96, depthWrite: false });
        const lines = new THREE.LineSegments(geometry, material);
        lines.name = "loop-reversals";
        lines.renderOrder = 4;
        this.graphRoot.add(lines);
      }
      if (pickPositions.length) {
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(pickPositions, 3));
        const material = new THREE.LineBasicMaterial({ transparent: true, opacity: 0, depthWrite: false });
        this.loopPickMesh = new THREE.LineSegments(geometry, material);
        this.loopPickMesh.name = "loop-picker";
        this.loopPickMesh.userData.kind = "loops";
        this.graphRoot.add(this.loopPickMesh);
      }
    }

    selectLoop(loop, play) {
      this.selectedLoop = loop || null;
      this.animation = null;
      this.removeNamed("selected-loop");
      this.removeNamed("transport-triad");
      this.selectedLine = null;
      this.triad = null;
      if (!loop) return;
      this.drawSelectedLoop(loop);
      if (play) this.playLoop(loop);
    }

    drawSelectedLoop(loop) {
      const path = this.loopPaths.get(loop.loop_id) || [];
      if (path.length < 2) return;
      const positions = [];
      path.forEach((point) => positions.push(point.x, point.y, point.z));
      const geometry = new this.deps.LineGeometry();
      geometry.setPositions(positions);
      const color = loop.orientation_flag ? 0xff304f : loop.below_floor ? 0x6c8797 : 0x9cecff;
      const material = new this.deps.LineMaterial({
        color,
        linewidth: loop.orientation_flag ? 4.2 : 3.1,
        transparent: true,
        opacity: loop.below_floor ? 0.45 : 1,
        depthWrite: false,
        dashed: loop.orientation_flag,
        dashSize: 0.42,
        gapSize: 0.24
      });
      material.resolution.set(this.canvas.clientWidth, this.canvas.clientHeight);
      this.lineMaterials.push(material);
      this.selectedLine = new this.deps.Line2(geometry, material);
      this.selectedLine.name = "selected-loop";
      this.selectedLine.computeLineDistances();
      this.selectedLine.renderOrder = 7;
      this.graphRoot.add(this.selectedLine);
    }

    playLoop(loop) {
      const floor = Number(this.data.calibration.bias_floor_degrees || 0);
      if (loop.orientation_flag || loop.max_angle === null || loop.max_angle < floor) return false;
      const path = this.loopPaths.get(loop.loop_id) || [];
      if (path.length < 2) return false;
      const lengths = new Float32Array(path.length);
      let total = 0;
      for (let i = 1; i < path.length; i += 1) {
        total += path[i - 1].distanceTo(path[i]);
        lengths[i] = total;
      }
      const triad = this.createTriad();
      triad.name = "transport-triad";
      triad.position.copy(path[0]);

      const radial = path[0].clone().normalize();
      const tangent = path[1].clone().sub(path[0]).normalize();
      const lateral = new this.THREE.Vector3().crossVectors(radial, tangent).normalize();
      tangent.crossVectors(lateral, radial).normalize();
      const basis = new this.THREE.Matrix4().makeBasis(tangent, lateral, radial);
      triad.quaternion.setFromRotationMatrix(basis);
      const baseQuaternion = triad.quaternion.clone();
      this.graphRoot.add(triad);
      this.triad = triad;
      if (this.reducedMotion) {
        this.scratch.quat2.setFromAxisAngle(radial, this.THREE.MathUtils.degToRad(loop.max_angle));
        triad.quaternion.copy(this.scratch.quat2).multiply(baseQuaternion);
        return true;
      }
      this.animation = {
        loop,
        path,
        lengths,
        total,
        start: performance.now(),
        travelMs: 4200,
        closureMs: 950,
        baseQuaternion,
        radial,
        measuredRadians: this.THREE.MathUtils.degToRad(loop.max_angle)
      };
      return true;
    }

    createTriad() {
      const THREE = this.THREE;
      const positions = [0,0,0, 0.9,0,0, 0,0,0, 0,0.9,0, 0,0,0, 0,0,0.9];
      const colors = [1,0.28,0.36, 1,0.28,0.36, 0.35,1,0.62, 0.35,1,0.62, 0.38,0.72,1, 0.38,0.72,1];
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
      const material = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 1, depthTest: false });
      const triad = new THREE.LineSegments(geometry, material);
      triad.renderOrder = 12;
      return triad;
    }

    updateAnimation(now) {
      const animation = this.animation;
      if (!animation || !this.triad) return;
      const elapsed = now - animation.start;
      if (elapsed <= animation.travelMs) {
        const targetDistance = (elapsed / animation.travelMs) * animation.total;
        let index = 1;
        while (index < animation.lengths.length && animation.lengths[index] < targetDistance) index += 1;
        index = Math.min(index, animation.path.length - 1);
        const before = animation.lengths[index - 1];
        const after = animation.lengths[index];
        const local = after > before ? (targetDistance - before) / (after - before) : 0;
        this.triad.position.copy(animation.path[index - 1]).lerp(animation.path[index], local);
        this.triad.quaternion.copy(animation.baseQuaternion);
      } else {
        this.triad.position.copy(animation.path[0]);
        const closureT = Math.min(1, (elapsed - animation.travelMs) / animation.closureMs);
        const eased = closureT * closureT * (3 - 2 * closureT);
        this.scratch.quat2.setFromAxisAngle(animation.radial, animation.measuredRadians * eased);
        this.triad.quaternion.copy(this.scratch.quat2).multiply(animation.baseQuaternion);
        if (closureT >= 1) this.animation = null;
      }
    }

    onPointerMove(event) {
      this.pendingPointer = event;
      if (this.hoverRaf) return;
      this.hoverRaf = requestAnimationFrame(() => {
        this.hoverRaf = 0;
        if (!this.pendingPointer) return;
        this.pick(this.pendingPointer, false);
      });
    }

    onClick(event) {
      const picked = this.pick(event, true);
      if (picked && picked.kind === "loop" && this.callbacks.onLoopSelect) this.callbacks.onLoopSelect(picked.value);
    }

    pick(event, click) {
      const rect = this.canvas.getBoundingClientRect();
      this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      this.raycaster.setFromCamera(this.pointer, this.camera);

      if (this.nodeMesh) {
        const hits = this.raycaster.intersectObject(this.nodeMesh, false);
        if (hits.length && Number.isInteger(hits[0].instanceId)) {
          const node = this.data.nodes[hits[0].instanceId];
          if (node && this.nodeMatchesFilters(node)) {
            if (!click) this.emitHover("node", node, event);
            return { kind: "node", value: node };
          }
        }
      }

      if (this.loopPickMesh) {
        const hits = this.raycaster.intersectObject(this.loopPickMesh, false);
        if (hits.length) {
          const loop = this.loopPickMap[Math.floor(hits[0].index / 2)];
          if (loop) {
            if (!click) this.emitHover("loop", loop, event);
            return { kind: "loop", value: loop };
          }
        }
      }

      if (this.edgePickMesh) {
        const hits = this.raycaster.intersectObject(this.edgePickMesh, false);
        if (hits.length) {
          const edge = this.edgePickMap[Math.floor(hits[0].index / 2)];
          if (edge) {
            if (!click) this.emitHover("edge", edge, event);
            return { kind: "edge", value: edge };
          }
        }
      }

      if (!click) this.emitHover(null, null);
      return null;
    }

    emitHover(kind, value, event) {
      if (this.callbacks.onHover) this.callbacks.onHover(kind, value, event);
    }

    fitCamera() {
      const radius = Math.max(...this.data.nodes.map((node) => this.shellRadius(node.state)), 11);
      this.camera.position.set(0, radius * 0.13, radius * 2.75);
      this.controls.target.set(0, 0, 0);
      this.controls.update();
    }

    resize() {
      const parent = this.canvas.parentElement;
      const width = Math.max(1, parent.clientWidth);
      const height = Math.max(1, parent.clientHeight);
      this.renderer.setSize(width, height, false);
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.lineMaterials.forEach((material) => material.resolution && material.resolution.set(width, height));
    }

    renderLoop(now) {
      requestAnimationFrame(this.renderLoop);
      const delta = Math.min(0.05, (now - this.lastTime) / 1000);
      this.lastTime = now;
      if (!this.controlsActive && !this.reducedMotion) this.root.rotation.y += delta * 0.032;
      this.updateAnimation(now);
      this.controls.update();
      this.renderer.render(this.scene, this.camera);
    }
  }

  window.GodelGlobeRenderer = { GodelGlobe };
}());
