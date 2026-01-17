

let scene, camera, renderer, particles;
let mouseX = 0, mouseY = 0;
let windowHalfX = window.innerWidth / 2;
let windowHalfY = window.innerHeight / 2;

function initBackground() {
    const canvas = document.getElementById('bg-canvas');

    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        1,
        1000
    );
    camera.position.z = 500;

    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true,
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1500;
    const posArray = new Float32Array(particlesCount * 3);
    const colorArray = new Float32Array(particlesCount * 3);

    for (let i = 0; i < particlesCount * 3; i += 3) {

        posArray[i] = (Math.random() - 0.5) * 1000;
        posArray[i + 1] = (Math.random() - 0.5) * 1000;
        posArray[i + 2] = (Math.random() - 0.5) * 1000;

        const colorChoice = Math.random();
        if (colorChoice < 0.5) {

            colorArray[i] = 0.39;     // R
            colorArray[i + 1] = 0.4;  // G
            colorArray[i + 2] = 0.95; // B
        } else {

            colorArray[i] = 0.93;     // R
            colorArray[i + 1] = 0.28; // G
            colorArray[i + 2] = 0.6;  // B
        }
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colorArray, 3));

    const originalColors = new Float32Array(colorArray);
    particlesGeometry.userData.originalColors = originalColors;

    const particlesMaterial = new THREE.PointsMaterial({
        size: 2,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    particles = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particles);

    const ambientLight = new THREE.AmbientLight(0x6366f1, 0.5);
    scene.add(ambientLight);

    document.addEventListener('mousemove', onMouseMove);
    window.addEventListener('resize', onWindowResize);

    animate();
}

function onMouseMove(event) {
    mouseX = (event.clientX - windowHalfX) * 0.5;
    mouseY = (event.clientY - windowHalfY) * 0.5;
}

function onWindowResize() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);

    particles.rotation.y += 0.0005;
    particles.rotation.x += 0.0003;

    const positions = particles.geometry.attributes.position.array;
    const colors = particles.geometry.attributes.color.array;
    const originalColors = particles.geometry.userData.originalColors;

    const mouseX3D = (mouseX / windowHalfX) * 300;
    const mouseY3D = (mouseY / windowHalfY) * 300;

    for (let i = 0; i < positions.length; i += 3) {
        const x = positions[i];
        const y = positions[i + 1];

        const dx = x - mouseX3D;
        const dy = y + mouseY3D;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 150) {
            const intensity = 1 - (distance / 150); // Fade based on distance
            colors[i] = originalColors[i] + (1 - originalColors[i]) * intensity;     // R -> white
            colors[i + 1] = originalColors[i + 1] + (1 - originalColors[i + 1]) * intensity; // G -> white
            colors[i + 2] = originalColors[i + 2] + (1 - originalColors[i + 2]) * intensity; // B -> white
        } else {

            colors[i] = originalColors[i];
            colors[i + 1] = originalColors[i + 1];
            colors[i + 2] = originalColors[i + 2];
        }
    }

    particles.geometry.attributes.color.needsUpdate = true;

    camera.position.x += (mouseX - camera.position.x) * 0.02;
    camera.position.y += (-mouseY - camera.position.y) * 0.02;
    camera.lookAt(scene.position);

    const time = Date.now() * 0.0001;
    particles.material.opacity = 0.6 + Math.sin(time) * 0.2;

    renderer.render(scene, camera);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBackground);
} else {
    initBackground();
}
