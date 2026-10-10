// Renderer, lights and the isometric camera rig.
import * as THREE from "three";

export const W = 1080, H = 1920;
export const ISO_EL = Math.atan(1 / Math.SQRT2); // true isometric elevation

export function createEngine(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const hemi = new THREE.HemisphereLight(0xfff4e2, 0x9db7d6, 1.75);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff1dc, 2.1);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1536, 1536);
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.02;
  sun.shadow.radius = 5;
  scene.add(sun, sun.target);
  const fill = new THREE.DirectionalLight(0xdbe9ff, 0.45);
  fill.position.set(10, 4, -2);
  scene.add(fill);

  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -300, 600);
  const aspect = W / H;
  const SUN_OFF = new THREE.Vector3(3, 14, 10);

  // cam: { x, y, z (target), vh (view height in world units), az (azimuth), el (elevation), roll }
  function setCamera(cam) {
    const vh = cam.vh;
    camera.top = vh / 2;
    camera.bottom = -vh / 2;
    camera.left = (-vh * aspect) / 2;
    camera.right = (vh * aspect) / 2;
    camera.updateProjectionMatrix();
    const el = cam.el ?? ISO_EL;
    const az = cam.az ?? Math.PI / 4;
    const d = 150;
    const t = new THREE.Vector3(cam.x, cam.y, cam.z);
    camera.position.set(t.x + d * Math.cos(el) * Math.sin(az), t.y + d * Math.sin(el), t.z + d * Math.cos(el) * Math.cos(az));
    camera.up.set(0, 1, 0);
    camera.lookAt(t);
    if (cam.roll) camera.rotateZ(cam.roll);
    // shadow frustum follows the view
    const r = Math.max(vh * 0.62, 8);
    sun.position.copy(t).add(SUN_OFF);
    sun.target.position.copy(t);
    sun.target.updateMatrixWorld();
    const sc = sun.shadow.camera;
    sc.left = -r; sc.right = r; sc.top = r; sc.bottom = -r;
    sc.near = 0.5; sc.far = 80;
    sc.updateProjectionMatrix();
  }

  // project a world point to canvas pixels (for HTML anchoring)
  const v = new THREE.Vector3();
  function project(p) {
    v.copy(p).project(camera);
    return { x: (v.x * 0.5 + 0.5) * W, y: (-v.y * 0.5 + 0.5) * H };
  }

  return { renderer, scene, camera, setCamera, project, lights: { hemi, sun, fill } };
}
