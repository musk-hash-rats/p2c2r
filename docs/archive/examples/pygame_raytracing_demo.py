"""
P2C2R Functional Demo: Ray Tracing Game with Peer Offloading

A simple space shooter that demonstrates:
1. Base game runs locally at 60 FPS (Pygame)
2. Ray tracing (reflections, shadows) offloaded to peers
3. Game gets progressively more complex (more objects = more ray tracing work)
4. Visual comparison: with/without P2C2R offloading

Controls:
- Arrow keys: Move ship
- Space: Shoot
- T: Toggle P2C2R offloading (see the difference!)
- R: Reset game
- ESC: Quit
"""

import pygame
import asyncio
import random
import time
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

# Import P2C2R components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.p2c2g.models import Task
from src.p2c2g.peer import PeerAgent
from src.p2c2g.ml_coordinator import MLCoordinator


# Game configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 50, 50),
    'green': (50, 255, 50),
    'blue': (50, 100, 255),
    'yellow': (255, 255, 50),
    'cyan': (50, 255, 255),
    'purple': (200, 50, 255),
}


@dataclass
class GameObject:
    """Base game object."""
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    color: Tuple[int, int, int]
    reflectivity: float = 0.0  # 0-1, how much it reflects
    emissive: float = 0.0  # 0-1, how much light it emits


class SpaceGame:
    """
    Simple space shooter that gets progressively more complex.
    
    Complexity increases:
    - More asteroids spawn over time
    - More particles/explosions
    - More light sources (emissive objects)
    - = More expensive ray tracing!
    """
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("P2C2R Demo: Ray Traced Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.running = True
        self.paused = False
        self.score = 0
        self.wave = 1
        
        # P2C2R state
        self.p2c2r_enabled = True
        self.ray_tracing_enabled = True
        
        # Game objects
        self.player: Optional[GameObject] = None
        self.bullets: List[GameObject] = []
        self.asteroids: List[GameObject] = []
        self.particles: List[GameObject] = []
        self.explosions: List[Tuple[float, float, float, int]] = []  # x, y, radius, ttl
        
        # Performance tracking
        self.frame_times: List[float] = []
        self.ray_trace_times: List[float] = []
        self.local_render_times: List[float] = []
        
        # P2C2R setup
        self.coordinator: Optional[MLCoordinator] = None
        self.setup_p2c2r()
        
        # Initialize game
        self.reset_game()
    
    def setup_p2c2r(self):
        """Initialize P2C2R coordinator and peers."""
        print("🚀 Setting up P2C2R system...")
        
        self.coordinator = MLCoordinator()
        
        # Create diverse peer pool
        peers = [
            PeerAgent(peer_id="RTX_4090", base_latency_ms=15, reliability=0.98),
            PeerAgent(peer_id="RTX_4070", base_latency_ms=20, reliability=0.95),
            PeerAgent(peer_id="RTX_3080", base_latency_ms=25, reliability=0.93),
            PeerAgent(peer_id="RTX_3070", base_latency_ms=30, reliability=0.90),
        ]
        
        for peer in peers:
            self.coordinator.register_peer(peer)
            print(f"  ✓ Registered {peer.peer_id}")
        
        print(f"✓ P2C2R ready with {len(peers)} peers\n")
    
    def reset_game(self):
        """Reset game to initial state."""
        # Player (at bottom center)
        self.player = GameObject(
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT - 60,
            vx=0, vy=0,
            radius=15,
            color=COLORS['cyan'],
            reflectivity=0.8,
            emissive=0.3  # Player ship glows
        )
        
        # Clear objects
        self.bullets.clear()
        self.asteroids.clear()
        self.particles.clear()
        self.explosions.clear()
        
        # Spawn initial asteroids
        self.spawn_wave()
        
        # Reset stats
        self.score = 0
        self.wave = 1
    
    def spawn_wave(self):
        """Spawn a wave of asteroids (complexity increases each wave)."""
        num_asteroids = 3 + self.wave * 2  # More asteroids each wave
        
        for i in range(num_asteroids):
            x = random.uniform(50, SCREEN_WIDTH - 50)
            y = random.uniform(-200, -50)
            vx = random.uniform(-2, 2)
            vy = random.uniform(1, 3)
            radius = random.uniform(20, 40)
            
            # Some asteroids are reflective (more expensive ray tracing)
            reflectivity = 0.6 if random.random() < 0.3 else 0.2
            
            asteroid = GameObject(
                x=x, y=y, vx=vx, vy=vy,
                radius=radius,
                color=COLORS['white'],
                reflectivity=reflectivity
            )
            self.asteroids.append(asteroid)
    
    def handle_input(self):
        """Handle player input."""
        keys = pygame.key.get_pressed()
        
        # Movement
        speed = 5
        if keys[pygame.K_LEFT]:
            self.player.vx = -speed
        elif keys[pygame.K_RIGHT]:
            self.player.vx = speed
        else:
            self.player.vx = 0
        
        if keys[pygame.K_UP]:
            self.player.vy = -speed
        elif keys[pygame.K_DOWN]:
            self.player.vy = speed
        else:
            self.player.vy = 0
    
    def update(self, dt: float):
        """Update game state."""
        if self.paused:
            return
        
        # Update player
        self.player.x += self.player.vx
        self.player.y += self.player.vy
        self.player.x = max(self.player.radius, min(SCREEN_WIDTH - self.player.radius, self.player.x))
        self.player.y = max(self.player.radius, min(SCREEN_HEIGHT - self.player.radius, self.player.y))
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.y += bullet.vy
            if bullet.y < 0:
                self.bullets.remove(bullet)
        
        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.x += asteroid.vx
            asteroid.y += asteroid.vy
            
            # Wrap around screen
            if asteroid.x < 0:
                asteroid.x = SCREEN_WIDTH
            elif asteroid.x > SCREEN_WIDTH:
                asteroid.x = 0
            
            # Remove if off screen
            if asteroid.y > SCREEN_HEIGHT + 100:
                self.asteroids.remove(asteroid)
        
        # Update particles
        for particle in self.particles[:]:
            particle.x += particle.vx
            particle.y += particle.vy
            particle.vy += 0.1  # Gravity
            particle.radius *= 0.98  # Shrink
            
            if particle.radius < 0.5:
                self.particles.remove(particle)
        
        # Update explosions
        for explosion in self.explosions[:]:
            x, y, radius, ttl = explosion
            if ttl <= 0:
                self.explosions.remove(explosion)
            else:
                self.explosions[self.explosions.index(explosion)] = (x, y, radius * 1.1, ttl - 1)
        
        # Check collisions
        self.check_collisions()
        
        # Spawn new wave if all asteroids destroyed
        if len(self.asteroids) == 0:
            self.wave += 1
            self.spawn_wave()
    
    def check_collisions(self):
        """Check for collisions between objects."""
        # Bullets vs asteroids
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                dist = math.sqrt((bullet.x - asteroid.x)**2 + (bullet.y - asteroid.y)**2)
                if dist < bullet.radius + asteroid.radius:
                    # Hit!
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += 10
                    
                    # Create explosion
                    self.create_explosion(asteroid.x, asteroid.y, asteroid.radius)
                    break
    
    def create_explosion(self, x: float, y: float, size: float):
        """Create explosion effect with particles."""
        # Add explosion (light source for ray tracing!)
        self.explosions.append((x, y, size, 20))  # 20 frames TTL
        
        # Spawn particles
        num_particles = int(size / 2)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            particle = GameObject(
                x=x, y=y, vx=vx, vy=vy,
                radius=random.uniform(2, 5),
                color=COLORS['yellow'],
                emissive=0.8  # Particles glow!
            )
            self.particles.append(particle)
    
    def shoot(self):
        """Fire a bullet."""
        bullet = GameObject(
            x=self.player.x,
            y=self.player.y - self.player.radius,
            vx=0, vy=-10,
            radius=5,
            color=COLORS['yellow'],
            emissive=1.0  # Bullets glow bright
        )
        self.bullets.append(bullet)
    
    def render_base_game(self):
        """Render base game (local, no ray tracing)."""
        render_start = time.time()
        
        # Clear screen
        self.screen.fill(COLORS['black'])
        
        # Draw stars (background)
        for i in range(100):
            x = (i * 123) % SCREEN_WIDTH
            y = (i * 456 + int(time.time() * 20)) % SCREEN_HEIGHT
            brightness = 100 + (i * 50) % 155
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), 1)
        
        # Draw asteroids
        for asteroid in self.asteroids:
            pygame.draw.circle(self.screen, asteroid.color, 
                             (int(asteroid.x), int(asteroid.y)), int(asteroid.radius))
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, bullet.color,
                             (int(bullet.x), int(bullet.y)), int(bullet.radius))
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle.color,
                             (int(particle.x), int(particle.y)), int(particle.radius))
        
        # Draw explosions (simple circles)
        for x, y, radius, ttl in self.explosions:
            alpha = int(255 * (ttl / 20))
            color = (255, alpha, 0)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), int(radius), 2)
        
        # Draw player
        pygame.draw.circle(self.screen, self.player.color,
                         (int(self.player.x), int(self.player.y)), int(self.player.radius))
        
        render_time = (time.time() - render_start) * 1000
        self.local_render_times.append(render_time)
        if len(self.local_render_times) > 60:
            self.local_render_times.pop(0)
    
    async def render_ray_tracing(self):
        """Render ray tracing effects (offloaded to peers if P2C2R enabled)."""
        if not self.ray_tracing_enabled:
            return
        
        rt_start = time.time()
        
        if self.p2c2r_enabled and self.coordinator:
            # Offload to P2C2R
            await self.render_ray_tracing_p2c2r()
        else:
            # Render locally (expensive!)
            self.render_ray_tracing_local()
        
        rt_time = (time.time() - rt_start) * 1000
        self.ray_trace_times.append(rt_time)
        if len(self.ray_trace_times) > 60:
            self.ray_trace_times.pop(0)
    
    async def render_ray_tracing_p2c2r(self):
        """Offload ray tracing to P2C2R peers."""
        # Count light sources and reflective objects (complexity)
        num_lights = len(self.explosions) + len([p for p in self.particles if p.emissive > 0.5])
        num_reflective = len([a for a in self.asteroids if a.reflectivity > 0.5])
        complexity = num_lights * 10 + num_reflective * 5 + len(self.particles)
        
        # Create ray tracing task
        task = Task(
            job_id=f"frame_{pygame.time.get_ticks()}",
            task_id="ray_trace",
            payload=self._serialize_scene(),
            deadline_ms=50,  # Ray tracing can lag behind
            constraints={
                'type': 'ray_tracing',
                'complexity': complexity,
                'num_lights': num_lights,
                'num_reflective': num_reflective
            }
        )
        
        # Offload to coordinator (async, non-blocking)
        result = await self.coordinator.schedule_task_ml(task)
        
        if result.status == 'success':
            # Apply ray traced effects
            self._apply_ray_tracing_result(result)
    
    def render_ray_tracing_local(self):
        """Render ray tracing locally (simulated, expensive)."""
        # Simulate expensive computation
        num_lights = len(self.explosions) + len([p for p in self.particles if p.emissive > 0.5])
        num_reflective = len([a for a in self.asteroids if a.reflectivity > 0.5])
        
        # Simulate ray tracing cost (very simplified)
        complexity = num_lights * 10 + num_reflective * 5 + len(self.particles)
        time.sleep(complexity / 10000)  # Simulate expensive computation
        
        # Apply simple effects
        self._apply_simple_ray_tracing()
    
    def _serialize_scene(self) -> bytes:
        """Serialize scene for peer processing."""
        # In production, this would be actual scene data
        # For demo, just send complexity metrics
        return b"scene_data"
    
    def _apply_ray_tracing_result(self, result):
        """Apply ray traced result from peer."""
        # In production, this would overlay actual ray traced image
        # For demo, just draw enhanced effects
        self._apply_simple_ray_tracing()
    
    def _apply_simple_ray_tracing(self):
        """Apply simple ray tracing effects (glow, reflections)."""
        # Draw glows around light sources
        for x, y, radius, ttl in self.explosions:
            # Glow effect
            alpha = int(128 * (ttl / 20))
            for i in range(3):
                glow_radius = int(radius * (2 + i * 0.5))
                glow_alpha = alpha // (i + 1)
                color = (255, glow_alpha, 0)
                pygame.draw.circle(self.screen, color, (int(x), int(y)), glow_radius, 2)
        
        # Draw glows for emissive particles
        for particle in self.particles:
            if particle.emissive > 0.5:
                glow_size = int(particle.radius * 3 * particle.emissive)
                color = tuple(int(c * particle.emissive) for c in particle.color)
                pygame.draw.circle(self.screen, color, 
                                 (int(particle.x), int(particle.y)), glow_size, 1)
        
        # Draw simple reflections on reflective asteroids
        for asteroid in self.asteroids:
            if asteroid.reflectivity > 0.5:
                # Find nearest light source
                nearest_light = None
                min_dist = float('inf')
                
                for x, y, radius, ttl in self.explosions:
                    dist = math.sqrt((asteroid.x - x)**2 + (asteroid.y - y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_light = (x, y, ttl)
                
                if nearest_light:
                    # Draw reflection
                    lx, ly, ttl = nearest_light
                    alpha = int(128 * asteroid.reflectivity * (ttl / 20))
                    if alpha > 0:
                        color = (255, alpha, 0)
                        pygame.draw.circle(self.screen, color,
                                         (int(asteroid.x), int(asteroid.y)),
                                         int(asteroid.radius * 0.8), 2)
    
    def render_ui(self):
        """Render UI overlay."""
        # Score and wave
        score_text = self.font.render(f"Score: {self.score}", True, COLORS['white'])
        wave_text = self.font.render(f"Wave: {self.wave}", True, COLORS['white'])
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(wave_text, (10, 50))
        
        # P2C2R status
        p2c2r_status = "P2C2R: ON" if self.p2c2r_enabled else "P2C2R: OFF"
        p2c2r_color = COLORS['green'] if self.p2c2r_enabled else COLORS['red']
        p2c2r_text = self.font.render(p2c2r_status, True, p2c2r_color)
        self.screen.blit(p2c2r_text, (SCREEN_WIDTH - 200, 10))
        
        # Performance stats
        if len(self.frame_times) > 0:
            avg_frame = sum(self.frame_times) / len(self.frame_times)
            fps = 1000 / avg_frame if avg_frame > 0 else 0
            fps_text = self.small_font.render(f"FPS: {fps:.1f}", True, COLORS['white'])
            self.screen.blit(fps_text, (10, SCREEN_HEIGHT - 30))
        
        if len(self.ray_trace_times) > 0 and self.ray_tracing_enabled:
            avg_rt = sum(self.ray_trace_times) / len(self.ray_trace_times)
            rt_text = self.small_font.render(f"Ray Trace: {avg_rt:.1f}ms", True, COLORS['yellow'])
            self.screen.blit(rt_text, (10, SCREEN_HEIGHT - 60))
        
        # Complexity indicator
        complexity = len(self.asteroids) + len(self.particles) + len(self.explosions) * 5
        complexity_text = self.small_font.render(f"Complexity: {complexity}", True, COLORS['cyan'])
        self.screen.blit(complexity_text, (10, SCREEN_HEIGHT - 90))
        
        # Controls
        controls = [
            "Arrow Keys: Move | Space: Shoot | T: Toggle P2C2R | R: Reset | ESC: Quit"
        ]
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, COLORS['white'])
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 30))
    
    async def run(self):
        """Main game loop."""
        print("\n" + "="*70)
        print("🎮 P2C2R RAY TRACING DEMO")
        print("="*70)
        print("\nControls:")
        print("  Arrow Keys: Move ship")
        print("  Space: Shoot")
        print("  T: Toggle P2C2R (compare performance!)")
        print("  R: Reset game")
        print("  ESC: Quit")
        print("\nWatch the complexity increase as more objects appear!")
        print("Toggle P2C2R on/off to see the performance difference.")
        print("="*70 + "\n")
        
        while self.running:
            frame_start = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.shoot()
                    elif event.key == pygame.K_t:
                        self.p2c2r_enabled = not self.p2c2r_enabled
                        print(f"\n{'✓' if self.p2c2r_enabled else '✗'} P2C2R {'ENABLED' if self.p2c2r_enabled else 'DISABLED'}")
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        print("\n🔄 Game reset")
            
            # Handle input
            self.handle_input()
            
            # Update game state
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            
            # Render
            self.render_base_game()
            await self.render_ray_tracing()
            self.render_ui()
            
            # Update display
            pygame.display.flip()
            
            # Track performance
            frame_time = (time.time() - frame_start) * 1000
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)
        
        # Cleanup
        pygame.quit()
        
        # Print final stats
        print("\n" + "="*70)
        print("📊 FINAL STATISTICS")
        print("="*70)
        if self.coordinator:
            print("\nML Performance Stats:")
            stats = self.coordinator.get_performance_stats()
            for peer_id, stat in stats.items():
                print(f"  {peer_id}: {stat['total_tasks']} tasks, "
                      f"{stat['success_rate']:.0%} success, "
                      f"avg {stat['avg_time_ms']:.1f}ms")
        print("\nThanks for playing! 🚀")
        print("="*70 + "\n")


async def main():
    """Run the demo."""
    game = SpaceGame()
    await game.run()


if __name__ == '__main__':
    asyncio.run(main())
