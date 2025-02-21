// Three.js Scene Setup
let scene, camera, renderer;
let car;

// Framer Motion Configuration
const pageTransition = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
};

const staggerContainer = {
    animate: {
        transition: {
            staggerChildren: 0.1
        }
    }
};

const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { 
        opacity: 1, 
        y: 0,
        transition: {
            duration: 0.6,
            ease: [0.6, -0.05, 0.01, 0.99]
        }
    }
};

// Three.js Functions
function initThreeJS() {
    // Scene setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('hero-canvas'), alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 1, 1);
    scene.add(directionalLight);

    // Camera position
    camera.position.z = 5;

    // Create a simple car shape (placeholder)
    const geometry = new THREE.BoxGeometry(2, 1, 3);
    const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
    car = new THREE.Mesh(geometry, material);
    scene.add(car);

    // Start animation
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    
    // Rotate the car
    if (car) {
        car.rotation.y += 0.01;
    }
    
    renderer.render(scene, camera);
}

// Handle window resize
function onWindowResize() {
    if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
}

// Initialize everything when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Three.js scene if hero canvas exists
    const heroCanvas = document.getElementById('hero-canvas');
    if (heroCanvas) {
        initThreeJS();
        window.addEventListener('resize', onWindowResize, false);
    }

    // Initialize Framer Motion animations
    const animatedElements = document.querySelectorAll('[data-animate]');
    animatedElements.forEach(element => {
        motion(element, fadeInUp);
    });
});

// Product card hover animation
function initProductCardAnimations() {
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            motion(card, {
                scale: 1.05,
                transition: { duration: 0.3 }
            });
        });

        card.addEventListener('mouseleave', () => {
            motion(card, {
                scale: 1,
                transition: { duration: 0.3 }
            });
        });
    });
}

// Smooth scroll function
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        window.scrollTo({
            top: element.offsetTop,
            behavior: 'smooth'
        });
    }
}

// Export functions for use in other files
window.smoothScroll = smoothScroll;
window.initProductCardAnimations = initProductCardAnimations;
