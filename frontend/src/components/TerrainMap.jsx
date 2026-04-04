import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

// Simple noise function (Perlin-like)
function noise(x, z) {
  return (
    Math.sin(x * 0.3) * Math.cos(z * 0.2) * 4 +
    Math.sin(x * 0.7 + 1) * Math.cos(z * 0.5 + 2) * 2 +
    Math.sin(x * 1.3 + 3) * Math.cos(z * 1.1 + 4) * 1
  );
}

export default function TerrainMap({ threatCoordinates = [], threatLevel = 'LOW' }) {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const frameRef = useRef(null);

  // Stringify to safely use in useEffect dependency array and avoid constant re-mounts
  const coordsStr = JSON.stringify(threatCoordinates);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const width = mount.clientWidth;
    const height = mount.clientHeight;

    // ── Scene ──
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050a0f, 0.018);
    sceneRef.current = scene;

    // ── Camera ──
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 500);
    camera.position.set(0, 45, 65);
    camera.lookAt(0, 0, 0);

    // ── Renderer ──
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x020609, 1);
    mount.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // ── Terrain ──
    const GRID = 80;
    const SIZE = 100;
    const geometry = new THREE.PlaneGeometry(SIZE, SIZE, GRID - 1, GRID - 1);
    geometry.rotateX(-Math.PI / 2);

    const positions = geometry.attributes.position;
    const colors = [];

    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);
      const y = noise(x * 0.1, z * 0.1);
      positions.setY(i, y);

      // Color by height — bright military green
      const t = Math.max(0, Math.min(1, (y + 7) / 14));
      const r = 0.02 + t * 0.05;
      const g = 0.35 + t * 0.55;
      const b = 0.12 + t * 0.1;
      colors.push(r, g, b);
    }

    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geometry.computeVertexNormals();

    const terrainMat = new THREE.MeshLambertMaterial({
      vertexColors: true,
      wireframe: false,
    });

    const terrain = new THREE.Mesh(geometry, terrainMat);
    scene.add(terrain);

    // ── Wireframe overlay ──
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x003320,
      wireframe: true,
      transparent: true,
      opacity: 0.25,
    });
    const wireMesh = new THREE.Mesh(geometry.clone(), wireMat);
    wireMesh.position.y = 0.05;
    scene.add(wireMesh);

    // ── Lighting ──
    const ambient = new THREE.AmbientLight(0x223344, 3.5);
    scene.add(ambient);

    const dirLight = new THREE.DirectionalLight(0x66ffaa, 5.0);
    dirLight.position.set(30, 60, 20);
    scene.add(dirLight);

    const dirLight2 = new THREE.DirectionalLight(0x002244, 2.0);
    dirLight2.position.set(-30, 40, -20);
    scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0x00ff88, 3.0, 200);
    pointLight.position.set(0, 30, 0);
    scene.add(pointLight);

    // ── Grid helper ──
    const gridHelper = new THREE.GridHelper(SIZE, 20, 0x001a0d, 0x001a0d);
    gridHelper.position.y = -7.5;
    scene.add(gridHelper);

    // ── Threat Markers ──
    const markerGroup = new THREE.Group();
    scene.add(markerGroup);

    const addMarker = (x, z, type, conf) => {
      const terrainY = noise(x * 0.1, z * 0.1) + 2.5;
      const color = type === 'Enemy Soldier' ? 0xff2244 : 0xffcc00;

      // Sphere marker
      const sphereGeo = new THREE.SphereGeometry(0.8, 12, 8);
      const sphereMat = new THREE.MeshBasicMaterial({ color });
      const sphere = new THREE.Mesh(sphereGeo, sphereMat);
      sphere.position.set(x, terrainY + 0.8, z);
      markerGroup.add(sphere);

      // Vertical pole
      const poleGeo = new THREE.CylinderGeometry(0.1, 0.1, terrainY + 0.8, 4);
      const poleMat = new THREE.MeshBasicMaterial({ color, opacity: 0.5, transparent: true });
      const pole = new THREE.Mesh(poleGeo, poleMat);
      pole.position.set(x, (terrainY + 0.8) / 2, z);
      markerGroup.add(pole);

      // Pulsing ring
      const ringGeo = new THREE.RingGeometry(1, 1.4, 20);
      const ringMat = new THREE.MeshBasicMaterial({
        color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(x, terrainY + 0.1, z);
      ring.userData.pulse = true;
      markerGroup.add(ring);
    };

    // Place threat markers
    if (threatCoordinates && threatCoordinates.length > 0) {
      threatCoordinates.forEach(tc => {
        addMarker(tc.x, tc.y, tc.type, tc.confidence);
      });
    } else {
      // Demo markers
      addMarker(15, 10, 'Enemy Soldier', 90);
      addMarker(-20, -15, 'Enemy Soldier', 75);
      addMarker(25, -20, 'Military Vehicle', 85);
      addMarker(-10, 20, 'Military Vehicle', 68);
    }

    // ── Camera auto-rotate ──
    let angle = 0;
    const RADIUS = 80;

    // ── Animate ──
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);

      angle += 0.003;
      camera.position.x = Math.sin(angle) * RADIUS * 0.8;
      camera.position.z = Math.cos(angle) * RADIUS;
      camera.position.y = 45 + Math.sin(angle * 0.5) * 5;
      camera.lookAt(0, 0, 0);

      // Pulse rings
      markerGroup.children.forEach(child => {
        if (child.userData.pulse) {
          child.material.opacity = 0.3 + 0.4 * Math.abs(Math.sin(Date.now() * 0.003));
          child.scale.setScalar(1 + 0.3 * Math.abs(Math.sin(Date.now() * 0.002)));
        }
      });

      renderer.render(scene, camera);
    };

    animate();

    // ── Resize ──
    const handleResize = () => {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(frameRef.current);
      if (mount.contains(renderer.domElement)) {
        mount.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [coordsStr]);

  return (
    <div
      ref={mountRef}
      style={{ width: '100%', height: '100%', cursor: 'grab' }}
    />
  );
}
