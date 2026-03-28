# Obstacle management: NPC vehicles, pedestrians, spawning

import pygame
import random
import config
from src.environment.vehicle import Vehicle


class ObstacleVehicle(Vehicle):
    """
    NPC vehicle with simple autonomous behavior.
    Moves in a lane with occasional lane changes.
    """
    
    def __init__(self, x, y, lane_id, road):
        super().__init__(
            x, y,
            config.OBSTACLE_CAR_WIDTH,
            config.OBSTACLE_CAR_HEIGHT,
            config.OBSTACLE_CAR_COLOR,
            max_speed=config.OBSTACLE_MAX_SPEED
        )
        self.lane_id = lane_id
        self.road = road
        self.speed = random.uniform(config.OBSTACLE_MIN_SPEED, config.OBSTACLE_MAX_SPEED)
        self.acceleration = 0
        self.lane_change_timer = 0
        self.lane_change_cooldown = 3.0  # seconds before next lane change
        self.target_lane = lane_id
    
    def update(self, dt):
        """Update with simple lane-following AI."""
        super().update(dt)
        
        # Lane change logic
        self.lane_change_timer += dt
        if self.lane_change_timer > self.lane_change_cooldown:
            if random.random() < 0.1:  # 10% chance to change lane
                self.target_lane = random.randint(0, self.road.num_lanes - 1)
                self.lane_change_timer = 0
        
        # Steer toward target lane
        target_y = self.road.get_lane_center_y(self.target_lane)
        lane_error = target_y - self.y
        
        if abs(lane_error) > config.RULE_BASED_LANE_TOLERANCE:
            if lane_error > 0:
                self.steer(5)  # Turn slightly down
            else:
                self.steer(-5)  # Turn slightly up
        else:
            self.steer(-self.angle * 0.1)  # Straighten out
        
        self.lane_id = self.road.get_lane_id(self.y)
        
        # Keep on road
        buffer = 50
        if self.y < buffer:
            self.y = buffer
        elif self.y > config.SCREEN_HEIGHT - buffer:
            self.y = config.SCREEN_HEIGHT - buffer


class Pedestrian(Vehicle):
    """
    Pedestrian with simple crossing behavior.
    """
    
    def __init__(self, x, y, road):
        super().__init__(
            x, y,
            config.PEDESTRIAN_WIDTH,
            config.PEDESTRIAN_HEIGHT,
            config.PEDESTRIAN_COLOR,
            max_speed=50  # Pedestrians are slow
        )
        self.road = road
        self.speed = random.uniform(30, 50)  # Random walk speed
        self.crossing = True  # Is actively crossing
        self.crossing_timer = 0
        self.crossing_duration = random.uniform(3, 7)  # How long to cross
    
    def update(self, dt):
        """Pedestrian crossing behavior."""
        super().update(dt)
        
        self.crossing_timer += dt
        if self.crossing_timer > self.crossing_duration:
            self.crossing = False
        
        # Random walk pattern
        if random.random() < 0.05:
            self.angle = random.uniform(-45, 45)


class ObstacleManager:
    """
    Manages spawning and despawning of obstacles (NPC vehicles, pedestrians).
    """
    
    def __init__(self, road):
        self.road = road
        self.obstacles = []
        self.vehicles = []  # NPC vehicles
        self.pedestrians = []  # Pedestrians
        self.spawn_timer = 0
        self.spawn_interval = config.OBSTACLE_SPAWN_INTERVAL
    
    def update(self, dt):
        """Spawn obstacles and update them."""
        # Spawn new obstacles
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._try_spawn_obstacle()
        
        # Update all obstacles
        for obstacle in self.vehicles:
            obstacle.update(dt)
        
        for pedestrian in self.pedestrians:
            pedestrian.update(dt)
        
        # Despawn off-screen obstacles
        self.vehicles = [v for v in self.vehicles if v.is_alive and -100 < v.y < config.SCREEN_HEIGHT + 100]
        self.pedestrians = [p for p in self.pedestrians if p.is_alive and -100 < p.x < config.SCREEN_WIDTH + 100]
    
    def _try_spawn_obstacle(self):
        """Attempt to spawn a new obstacle."""
        if random.random() < config.OBSTACLE_SPAWN_CHANCE and len(self.vehicles) < config.MAX_OBSTACLES:
            lane_id = random.randint(0, self.road.num_lanes - 1)
            x = config.SCREEN_WIDTH / 2
            y = self.road.get_lane_center_y(lane_id)
            
            vehicle = ObstacleVehicle(x, y, lane_id, self.road)
            self.vehicles.append(vehicle)
    
    def get_all_obstacles(self):
        """Return combined list of all obstacles."""
        return self.vehicles + self.pedestrians
    
    def draw(self, surface):
        """Draw all obstacles."""
        for vehicle in self.vehicles:
            vehicle.draw(surface)
        
        for pedestrian in self.pedestrians:
            pedestrian.draw(surface)
    
    def check_collisions(self, player_vehicle):
        """Check if player hit any obstacle. Returns True if collision."""
        for obstacle in self.get_all_obstacles():
            if player_vehicle.collides_with(obstacle):
                return True
        return False
    
    def reset(self):
        """Clear all obstacles."""
        self.vehicles = []
        self.pedestrians = []
        self.spawn_timer = 0
