# Birthday Project

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 9 min read

Interactive birthday celebration page with animations and JavaScript effects

## Overview

The Birthday Project is a single-page interactive experience built as a creative coding experiment, exploring the limits of what CSS keyframe animations and the Canvas API can produce in a browser without any libraries. The page opens with CSS-animated balloons floating upward, layered confetti falling across the viewport, and sparkle pulse animations on the title. A JavaScript countdown timer displays the time until the birthday in days, hours, minutes, and seconds, updating every second via setInterval. A Canvas 2D particle system runs a requestAnimationFrame loop that renders hundreds of particles with individual velocity, gravity, and colour values. As the user scrolls, personalised messages are revealed in a staggered cascade using IntersectionObserver. On mobile, the particle count is automatically reduced based on screen size and touch device detection to prevent frame rate drops on lower-powered hardware.

## Architecture

JavaScript Modules

CSS Animation Layers

Single Page Structure

Updates every 1s

rAF loop

Viewport entry

index.htmlDocument Structure · Canvas Element · Message Sections

Balloon AnimationstranslateY + rotate keyframes

Confetti Fallmulti-transform keyframes · random delays

Sparkle Pulseopacity + scale keyframes

Countdown TimerDate.now · setInterval · DOM update

Particle SystemCanvas 2D · requestAnimationFrame · particle array

Message RevealIntersectionObserver · staggered CSS transitions

Countdown Display(DOM element)

Canvas ParticleRender Output

Message SectionsFade In Sequentially

## Tech Stack

- HTML5, Single page structure with a <canvas> element for particles and section elements for each scrollable message block

- CSS3 Keyframe Animations, @keyframes for balloon float (translateY + rotate), confetti fall (combined translateY, translateX, rotate), and sparkle pulse (opacity + scale)

- Canvas API, 2D context rendering of a particle system with per-particle velocity, gravity, alpha decay, and colour; driven by a requestAnimationFrame loop

- Vanilla JavaScript, Countdown timer via setInterval and Date arithmetic; IntersectionObserver for scroll-triggered message reveals; mobile particle count reduction via navigator.maxTouchPoints and screen width check

## Build Process

Three independent @keyframes sets were written: balloons float upward with a gentle left/right rotation oscillation; confetti pieces fall diagonally with a full rotation and horizontal drift; sparkles pulse between 40% and 100% opacity with a slight scale. Each animated element has a unique animation-delay to prevent synchronised motion.

@keyframes balloon-float {
  0%   { transform: translateY(0)    rotate(-3deg); }
  50%  { transform: translateY(-20px) rotate(3deg);  }
  100% { transform: translateY(0)    rotate(-3deg); }
}

@keyframes confetti-fall {
  0%   { transform: translateY(-10px) translateX(0)   rotate(0deg);   opacity: 1; }
  100% { transform: translateY(100vh) translateX(40px) rotate(720deg); opacity: 0; }
}

The target date is stored as a Date object. A setInterval at 1000 ms computes the difference between Date.now() and the target, then derives days, hours, minutes, and seconds by successive division and modulo operations. The results are written directly to DOM span elements.

const target = new Date('2026-05-15T00:00:00'); // example target date

const timer = setInterval(() => {
  const diff = target - Date.now();
  if (diff <= 0) { clearInterval(timer); return; }
  const d = Math.floor(diff / 86400000);
  const h = Math.floor((diff % 86400000) / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  document.getElementById('cd-days').textContent  = String(d).padStart(2, '0');
  document.getElementById('cd-hours').textContent = String(h).padStart(2, '0');
  document.getElementById('cd-mins').textContent  = String(m).padStart(2, '0');
  document.getElementById('cd-secs').textContent  = String(s).padStart(2, '0');
}, 1000);

A particle array is initialised with randomised x/y positions, velocity components, radii, colours, and alpha values. The requestAnimationFrame loop clears the canvas, advances each particle's position by its velocity, applies a gravity constant to the y-velocity, decrements alpha, and removes dead particles (alpha ≤ 0). New particles are spawned each frame to maintain a target count.

function Particle() {
  this.x = Math.random() * canvas.width;
  this.y = Math.random() * canvas.height;
  this.vx = (Math.random() - 0.5) * 3;
  this.vy = (Math.random() - 0.5) * 3 - 1;
  this.radius = Math.random() * 4 + 1;
  this.alpha = 1;
  this.color = `hsl(${Math.random() * 360}, 80%, 60%)`;
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  particles.forEach((p, i) => {
    p.vy += 0.05; // gravity
    p.x += p.vx; p.y += p.vy;
    p.alpha -= 0.008;
    if (p.alpha <= 0) particles.splice(i, 1);
    ctx.globalAlpha = p.alpha;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();
  });
  while (particles.length < MAX_PARTICLES) particles.push(new Particle());
  requestAnimationFrame(animate);
}

Message sections start at opacity: 0; transform: translateY(24px). An IntersectionObserver with a threshold: 0.2 adds .is-visible on entry, triggering a CSS transition to full opacity and no transform. Child elements within each section use increasing --delay custom properties to stagger their reveals.

Running 300 particles on a low-powered mobile device causes dropped frames. On page load, the maximum particle count is reduced based on device capabilities. Touch devices with narrow screens receive a significantly lower cap, keeping the animation smooth at 60 fps.

const isMobile = navigator.maxTouchPoints > 0 && window.innerWidth < 768;
const MAX_PARTICLES = isMobile ? 60 : 250;

The single-page app was pushed to the main branch and served via GitHub Pages. No build step was required, pure HTML, CSS, and JavaScript. All asset paths were verified as relative to the root so the deployed version resolved them correctly from the GitHub Pages subdomain.

## Page Lifecycle Flow

Every second

~60fps

Section enters viewport

Page Loads

CSS AnimationsAuto-StartBalloons · Confetti · Sparkles

JS InitialisesCountdown TimersetInterval 1000ms

Canvas InitParticle ArrayrAF Loop Starts

IntersectionObserverAttached toMessage Sections

Timer DisplayUpdates in DOM

Particles Renderedto Canvas

CSS TransitionTriggeredopacity + translateY

Messages RevealStaggered Cascade

## Challenges & Solutions

Canvas Particle Performance on Mobile. The initial implementation spawned 250 particles on all devices. On mid-range Android phones this caused the requestAnimationFrame loop to drop below 30 fps, making the animation janky. The solution was to detect touch devices with navigator.maxTouchPoints > 0 combined with a screen width check, then cap MAX_PARTICLES at 60 for those devices. This maintains smooth 60 fps on mobile while preserving the full density effect on desktop. A further optimisation was to reduce particle spawn rate on each frame rather than always maintaining the full count, giving a more organic effect.

Animation Synchronisation Between CSS and JavaScript Timers. The CSS balloon animations loop on their own timing, completely independent of the JavaScript countdown and particle system. If the page is backgrounded and then returned to, CSS animations resume from their current state while the JS timer catches up to the current time on the next tick. Since the animations are decorative and non-interactive, this desynchronisation is invisible to users and requires no fix. However it was a useful lesson in the architectural separation between CSS-driven and JS-driven animation.

## What I Learned

- The Canvas 2D API's requestAnimationFrame loop pattern: clear → update → draw → repeat, and how to structure a particle system as an array of objects with per-particle state

- Gravity in a particle system is simply a constant added to the y-velocity each frame, it accumulates naturally without any special physics library

- setInterval for countdown timers is appropriate but drifts slightly over long durations; for precision, always compute from Date.now() rather than decrementing a counter

- CSS animations and JavaScript timers are architecturally independent, they do not share a clock and should not be relied upon to stay synchronised

- Mobile performance must be tested on real hardware, not just browser DevTools throttling, the particle count that runs smoothly in DevTools mobile simulation can still drop frames on a physical device

- navigator.maxTouchPoints combined with a viewport width check is a more reliable mobile detection heuristic than userAgent string parsing

## How I Built It

Phase 1: CSS animation layers. I started with the purely decorative layers: balloons rising with translateY plus rotation keyframes, multi-transform confetti fall with randomized delays, and an opacity-plus-scale sparkle pulse on the title. Each layer runs on its own keyframe loop, completely independent of the JavaScript.

Phase 2: The Canvas particle system. Next I built a Canvas 2D particle system around the classic clear, update, draw, repeat loop driven by requestAnimationFrame. Each particle carries its own velocity, gravity, and colour, and gravity is just a constant added to the y-velocity each frame.

Phase 3: Countdown and interactivity. A setInterval countdown computes time remaining from Date.now() rather than decrementing a counter, so it cannot drift. Scroll-triggered message reveals use IntersectionObserver with a staggered cascade.

Phase 4: Mobile performance work. The initial 250-particle default dropped frames on mid-range phones, so I added device detection (navigator.maxTouchPoints plus a viewport width check) that caps the particle count on mobile, and reduced the per-frame spawn rate for a more organic effect.

Phase 5: Graceful degradation. A feature-detection check wraps the IntersectionObserver setup so browsers without the API simply show all messages without animation, no polyfill required.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Tool | A modern web browser | Canvas 2D, requestAnimationFrame, and CSS keyframes are all that is required |
| Software | Code editor | Single-page build; no build step, no dependencies |
| Skill | CSS keyframe animations | translateY, rotate, opacity, and scale loops with randomized delays |
| Skill | Canvas 2D API | The clear/update/draw loop and per-particle state objects |
| Skill | IntersectionObserver | Scroll-triggered reveals with feature detection for older browsers |
| Skill | Performance budgeting | Testing on real mobile hardware, not just DevTools throttling |

## Challenges and Lessons Learned

Mobile frame rate. The full particle count ran fine on desktop but janked on real phones. Capping particles by device capability restored 60 fps. The honest lesson: DevTools mobile simulation is not a substitute for physical hardware when you are budgeting frames.

CSS and JS animations do not share a clock. Backgrounding the tab desynchronises the CSS loops from the JS timer, and there is nothing to fix because decorative layers are allowed to drift. That was a useful architectural insight: only synchronise what the user can actually perceive.

Countdowns should compute, not decrement. Deriving the display from Date.now() each tick makes the timer immune to drift from blocked event loops. A decrementing counter would silently lose time.

## What Is Next

- Configurable mode: make the name, date, and message list data-driven so one page serves any birthday

- Music toggle with an audio visualiser tied to the particle system

- WebGL upgrade path if the particle count ever needs to scale into the thousands

- Prefers-reduced-motion support so users with motion sensitivity get a static celebration instead

- Shareable link generator that encodes the recipient's name and date in the URL

## Related Projects

- Faiaz Shisha, a multi-page business site with booking.

- HomeBound Aisha, a responsive business website.

- Practice Apps, TypeScript practice builds.
