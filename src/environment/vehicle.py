# Vehicle base class with physics

import pygame
import math
import config


class Vehicle:
    """
    Base vehicle class with position, velocity, and physics.
    """
    
    def __init__(self, x, y, width, height, color, max_speed=config.MAX_SPEED):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        
        # Physics
        self.vx = 0  # Velocity X (horizontal)
        self.vy = 0  # Velocity Y (vertical)
        self.speed = 0  # Forward speed (pixels/sec)
        self.angle = 0  # Steering angle (degrees)
        self.max_speed = max_speed
        
        self.acceleration = 0  # Current acceleration
        self.is_alive = True
    
    def update(self, dt):
        """Update position based on physics."""
        if not self.is_alive:
            return
        
        # Apply forward acceleration (simple model)
        self.speed += self.acceleration * dt
        self.speed = max(-self.max_speed, min(self.max_speed, self.speed))
        
        # Highway kinematics:
        # - Longitudinal motion on X axis via speed
        # - Steering angle controls lateral drift on Y axis
        angle_rad = math.radians(self.angle)
        self.vx = self.speed
        self.vy = self.speed * math.sin(angle_rad)
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Keep Y on the road bounds. X can go off-screen for despawn logic.
        self.y = max(0, min(config.SCREEN_HEIGHT, self.y))
        # Mark for despawn if too far off-screen vertically
        if self.y < -100 or self.y > config.SCREEN_HEIGHT + 100:
            self.is_alive = False
    
    def accelerate(self, amount):
        """Set acceleration (positive or negative)."""
        self.acceleration = amount
    
    def set_steering(self, angle, dt=0.016):
        """Set steering angle with smooth rate limiting (~300°/sec)."""
        # Limit steering rate to realistic vehicle dynamics
        max_change = config.TURNING_SPEED * dt
        target = max(self.angle - max_change, min(self.angle + max_change, angle))
        self.angle = max(-config.STEERING_ANGLE_MAX, min(config.STEERING_ANGLE_MAX, target))
    
    def steer(self, delta_angle, dt=0.016):
        """Adjust steering angle with rate limiting."""
        self.set_steering(self.angle + delta_angle, dt)
    
    def get_rect(self):
        """Get bounding box for collision detection."""
        return pygame.Rect(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )
    
    def collides_with(self, other):
        """Check collision with another vehicle."""
        return self.get_rect().colliderect(other.get_rect())
    
    def draw(self, surface):
        """Draw vehicle as a car silhouette (not a block)."""
        if not self.is_alive:
            return

        cx = self.x
        cy = self.y
        half_w = self.width / 2
        half_h = self.height / 2
        heading = math.radians(self.angle)

        def rot(px, py):
            """Rotate local point around car center by heading angle."""
            rx = px * math.cos(heading) - py * math.sin(heading)
            ry = px * math.sin(heading) + py * math.cos(heading)
            return (cx + rx, cy + ry)

        # Main body polygon (car-like tapered front)
        body = [
            rot(-half_w, -half_h * 0.8),
            rot(half_w * 0.5, -half_h * 0.8),
            rot(half_w, 0),
            rot(half_w * 0.5, half_h * 0.8),
            rot(-half_w, half_h * 0.8),
        ]
        pygame.draw.polygon(surface, self.color, body)
        pygame.draw.polygon(surface, (220, 220, 220), body, 1)

        # Windshield and rear window
        windshield = [
            rot(half_w * 0.05, -half_h * 0.45),
            rot(half_w * 0.55, -half_h * 0.30),
            rot(half_w * 0.55, half_h * 0.30),
            rot(half_w * 0.05, half_h * 0.45),
        ]
        rear_window = [
            rot(-half_w * 0.75, -half_h * 0.38),
            rot(-half_w * 0.25, -half_h * 0.38),
            rot(-half_w * 0.25, half_h * 0.38),
            rot(-half_w * 0.75, half_h * 0.38),
        ]
        pygame.draw.polygon(surface, (140, 190, 235), windshield)
        pygame.draw.polygon(surface, (120, 170, 220), rear_window)

        # Wheels
        wheel_color = (35, 35, 35)
        wheel_positions = [
            rot(-half_w * 0.55, -half_h * 0.95),
            rot(half_w * 0.25, -half_h * 0.95),
            rot(-half_w * 0.55, half_h * 0.95),
            rot(half_w * 0.25, half_h * 0.95),
        ]
        for wx, wy in wheel_positions:
            pygame.draw.circle(surface, wheel_color, (int(wx), int(wy)), max(2, int(self.height * 0.08)))

        # Headlights for orientation
        headlight_l = rot(half_w * 0.95, -half_h * 0.22)
        headlight_r = rot(half_w * 0.95, half_h * 0.22)
        pygame.draw.circle(surface, (250, 245, 180), (int(headlight_l[0]), int(headlight_l[1])), 2)
        pygame.draw.circle(surface, (250, 245, 180), (int(headlight_r[0]), int(headlight_r[1])), 2)
    
    def get_state(self):
        """Return vehicle state as dictionary."""
        return {
            'x': self.x,
            'y': self.y,
            'speed': self.speed,
            'angle': self.angle,
            'vx': self.vx,
            'vy': self.vy,
            'is_alive': self.is_alive
        }
    
    def reset(self, x, y):
        """Reset vehicle to starting position."""
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.speed = 0
        self.angle = 0
        self.acceleration = 0
        self.is_alive = True
