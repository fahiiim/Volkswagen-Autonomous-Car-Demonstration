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
        
        # Calculate velocity components based on angle
        angle_rad = math.radians(self.angle)
        self.vx = self.speed * math.sin(angle_rad)
        self.vy = -self.speed * math.cos(angle_rad)  # Negative because Y increases downward
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Wrap around screen horizontally
        if self.x < -self.width:
            self.x = config.SCREEN_WIDTH
        elif self.x > config.SCREEN_WIDTH:
            self.x = -self.width
    
    def accelerate(self, amount):
        """Set acceleration (positive or negative)."""
        self.acceleration = amount
    
    def set_steering(self, angle):
        """Set steering angle."""
        self.angle = max(-config.STEERING_ANGLE_MAX, min(config.STEERING_ANGLE_MAX, angle))
    
    def steer(self, delta_angle):
        """Adjust steering angle."""
        self.set_steering(self.angle + delta_angle)
    
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
        """Draw vehicle as a rectangle."""
        if not self.is_alive:
            return
        
        rect = self.get_rect()
        pygame.draw.rect(surface, self.color, rect)
        
        # Draw direction indicator (small line pointing forward)
        angle_rad = math.radians(self.angle)
        front_x = self.x + (self.height / 2) * math.sin(angle_rad)
        front_y = self.y - (self.height / 2) * math.cos(angle_rad)
        pygame.draw.line(surface, (255, 255, 255), (self.x, self.y), (front_x, front_y), 2)
    
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
