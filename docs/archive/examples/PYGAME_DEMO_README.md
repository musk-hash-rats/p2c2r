# 🎮 Pygame Ray Tracing Demo - README

## Overview

An **interactive demo** that shows P2C2R in action! A simple space shooter where ray tracing effects (reflections, glows, shadows) are offloaded to peer GPUs while the base game runs locally at 60 FPS.

## What It Demonstrates

### **The Core P2C2R Concept:**
1. **Base game runs locally** - Simple rendering at 60 FPS
2. **Ray tracing offloaded to peers** - Expensive effects computed remotely
3. **Complexity increases** - More objects = more expensive ray tracing
4. **Toggle P2C2R on/off** - See the performance difference!

### **Visual Effects Offloaded:**
- 🌟 **Glowing particles** (emissive objects)
- 💥 **Explosion light sources** (dynamic lighting)
- 🪞 **Reflections on asteroids** (ray traced)
- ✨ **Particle effects** (hundreds of light-emitting particles)

## Installation

```bash
# Install dependencies
pip install pygame numpy scikit-learn

# Or use requirements.txt
pip install -r requirements.txt
```

## Running the Demo

```bash
# From project root
python examples/pygame_raytracing_demo.py
```

## Controls

| Key | Action |
|-----|--------|
| **Arrow Keys** | Move ship |
| **Space** | Shoot |
| **T** | Toggle P2C2R (on/off) |
| **R** | Reset game |
| **ESC** | Quit |

## Gameplay

### **Objective:**
Destroy asteroids by shooting them. Each wave spawns more asteroids with increasing complexity!

### **Progression:**
- **Wave 1**: 5 asteroids, simple
- **Wave 2**: 7 asteroids, some reflective
- **Wave 3**: 9 asteroids, more lights
- **Wave 4+**: Exponentially more complex (particles, explosions, reflections)

### **Watch the Performance:**
- Bottom-left corner shows:
  - **FPS**: Current frame rate
  - **Ray Trace**: Time spent on ray tracing (ms)
  - **Complexity**: Number of objects/lights

## The Experiment

### **Try This:**

1. **Start with P2C2R ON** (green indicator)
   - Play for a few waves
   - Note the FPS stays around 60
   - Ray trace time: ~20-40ms (offloaded to peers)

2. **Press 'T' to turn P2C2R OFF** (red indicator)
   - Continue playing
   - Watch FPS drop as complexity increases
   - Ray trace time: ~80-200ms (local computation)
   - Game becomes laggy!

3. **Press 'T' again to turn P2C2R back ON**
   - FPS immediately recovers
   - Ray tracing continues smoothly
   - ML learns which peers are best

### **What You'll See:**

```
P2C2R ON:                      P2C2R OFF:
├─ FPS: 58-60                  ├─ FPS: 25-45 (varies)
├─ Ray Trace: 20-40ms          ├─ Ray Trace: 80-200ms
├─ Smooth gameplay             ├─ Laggy, stuttering
└─ Effects look great          └─ Effects slow down game

As complexity increases (more waves):
  P2C2R ON:  FPS stays ~60     ML gets smarter over time!
  P2C2R OFF: FPS drops to ~20  Game becomes unplayable
```

## Behind the Scenes

### **What's Happening:**

```
Every Frame:

1. Base Game Render (LOCAL, <16ms):
   ├─ Draw stars (background)
   ├─ Draw asteroids
   ├─ Draw bullets
   ├─ Draw player ship
   └─ Draw particles

2. Ray Tracing (OFFLOADED if P2C2R ON, ~40ms):
   ├─ Count light sources (explosions, particles)
   ├─ Count reflective objects (shiny asteroids)
   ├─ Create Task with complexity metrics
   ├─ ML Coordinator assigns to best peer
   │   → RTX_4090: 15ms latency, 98% reliable
   │   → RTX_4070: 20ms latency, 95% reliable
   │   → RTX_3080: 25ms latency, 93% reliable
   │   → RTX_3070: 30ms latency, 90% reliable
   ├─ Peer computes ray tracing asynchronously
   ├─ Apply effects when result arrives
   └─ ML learns from execution time

3. If P2C2R OFF:
   └─ All ray tracing computed locally (SLOW!)
```

### **ML Learning:**

The coordinator learns over time:
- Which peer is fastest for ray tracing
- Failure patterns (peer drops out)
- Network conditions (latency varies)

Press **T** multiple times to see ML adapt!

## Performance Expectations

### **With P2C2R (Expected):**
```
Wave 1-3:  60 FPS constant
Wave 4-6:  58-60 FPS
Wave 7-10: 55-60 FPS (high complexity)

Ray trace time: 20-50ms (offloaded)
ML optimizes peer selection over time
```

### **Without P2C2R (Expected):**
```
Wave 1-3:  55-60 FPS (still manageable)
Wave 4-6:  40-50 FPS (getting laggy)
Wave 7-10: 20-35 FPS (unplayable)

Ray trace time: 80-200ms (local computation)
Game stutters, effects delayed
```

## Technical Details

### **Complexity Factors:**

| Object Type | Ray Trace Cost |
|-------------|----------------|
| **Explosion** | 50 complexity (bright light source) |
| **Emissive Particle** | 10 complexity (small light) |
| **Reflective Asteroid** | 5 complexity (needs reflection rays) |
| **Regular Object** | 1 complexity (simple) |

**Example Wave 5:**
- 11 asteroids (3 reflective) = 26 complexity
- 2 explosions = 100 complexity  
- 50 particles (30 emissive) = 350 complexity
- **Total: 476 complexity**

Without P2C2R: 476 / 10000 = ~48ms ray trace time (local)  
With P2C2R: Offloaded to peer, ~25ms async

### **P2C2R Task Creation:**

```python
# Game creates ray tracing task
task = Task(
    job_id=f"frame_{current_frame}",
    task_id="ray_trace",
    payload=scene_data,  # Light sources, reflective objects
    deadline_ms=50,  # Ray tracing can lag 3 frames
    constraints={
        'type': 'ray_tracing',
        'complexity': 476,
        'num_lights': 32,
        'num_reflective': 3
    }
)

# ML coordinator assigns to best peer
result = await coordinator.schedule_task_ml(task)

# Apply result asynchronously (non-blocking!)
if result.status == 'success':
    apply_ray_tracing_effects(result)
```

## Troubleshooting

### **Game runs slow even with P2C2R:**
- This is a **simulation** - peers don't actually compute ray tracing
- The demo shows the **architecture**, not real GPU offloading
- For production, peers would run actual ray tracing kernels

### **Want to see real performance difference:**
- Increase complexity faster: Edit `spawn_wave()` to spawn more asteroids
- Reduce local simulation: Comment out `time.sleep()` in `render_ray_tracing_local()`

### **ModuleNotFoundError: pygame**
```bash
pip install pygame
```

## What's Next?

This demo shows the **architecture**. For production:

1. **Real GPU offloading**: Use CUDA/OptiX for actual ray tracing
2. **Network layer**: WebRTC for peer communication
3. **Image compression**: Send actual rendered frames
4. **Game engine integration**: game engine plugin

See `docs/HYBRID_COMPUTE_ARCHITECTURE.md` for the full vision!

## Code Structure

```
pygame_raytracing_demo.py:
├─ GameObject: Base class for game entities
├─ SpaceGame: Main game class
│   ├─ setup_p2c2r(): Initialize coordinator and peers
│   ├─ render_base_game(): Local rendering (fast)
│   ├─ render_ray_tracing(): Offload to peers (or local)
│   ├─ render_ray_tracing_p2c2r(): P2C2R offloading
│   └─ render_ray_tracing_local(): Local (slow)
└─ main(): Entry point
```

---

**Enjoy the demo! Watch as P2C2R keeps the game smooth even as complexity explodes! 🚀**
