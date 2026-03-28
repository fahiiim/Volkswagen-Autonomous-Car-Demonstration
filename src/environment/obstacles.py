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
        # World-frame cruise speed; screen-relative speed is computed against ego speed.
        self.cruise_speed = random.uniform(config.OBSTACLE_MIN_SPEED, config.OBSTACLE_MAX_SPEED)
        self.speed = 0
        self.acceleration = 0
        self.lane_change_timer = 0
        self.lane_change_cooldown = 3.0  # seconds before next lane change
        self.target_lane = lane_id
        self.last_update_time = 0
        self.speed_noise_timer = 0
    
    def update(self, dt, ego_speed):
        """Update with lane-following AI and ego-relative highway motion."""
        self.last_update_time = dt
        self.speed_noise_timer += dt

        # Small random cruise speed drift to keep traffic dynamic.
        if self.speed_noise_timer >= 1.0:
            self.speed_noise_timer = 0
            self.cruise_speed += random.uniform(-15, 15)
            self.cruise_speed = max(config.OBSTACLE_MIN_SPEED, min(config.OBSTACLE_MAX_SPEED, self.cruise_speed))

        # Relative screen speed: negative means obstacle approaches ego from ahead.
        self.speed = self.cruise_speed - ego_speed
        super().update(dt)
        
        # Lane change logic
        self.lane_change_timer += dt
        if self.lane_change_timer > self.lane_change_cooldown:
            if random.random() < 0.1:  # 10% chance to change lane
                new_lane = random.randint(0, self.road.num_lanes - 1)
                if new_lane != self.target_lane:
                    self.target_lane = new_lane
                    self.lane_change_timer = 0
        
        # Smooth, proportional steering toward target lane
        target_y = self.road.get_lane_center_y(self.target_lane)
        lane_error = target_y - self.y
        
        # Proportional control: steer more if farther from lane
        proportional_gain = 0.15  # Tuned for realistic behavior
        target_angle = max(-config.STEERING_ANGLE_MAX, min(config.STEERING_ANGLE_MAX, lane_error * proportional_gain))
        self.set_steering(target_angle, dt)
        
        self.lane_id = self.road.get_lane_id(self.y)
        
        # Keep roughly on road
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
    
    def update(self, dt, ego_speed):
        """Spawn obstacles and update them using ego-relative speed."""
        # Spawn new obstacles
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._try_spawn_obstacle()
        
        # Update all obstacles
        for obstacle in self.vehicles:
            obstacle.update(dt, ego_speed)
        
        for pedestrian in self.pedestrians:
            pedestrian.update(dt)
        
        # Despawn off-screen obstacles (prevent memory leaks)
        # Vehicles: despawn when completely off-screen in X
        self.vehicles = [v for v in self.vehicles if v.is_alive and -200 < v.x < config.SCREEN_WIDTH + 200]
        # Pedestrians: despawn when off-screen
        self.pedestrians = [p for p in self.pedestrians if p.is_alive and -100 < p.x < config.SCREEN_WIDTH + 100 and -100 < p.y < config.SCREEN_HEIGHT + 100]
    
    def _try_spawn_obstacle(self):
        """Attempt to spawn a new obstacle ahead of ego (off-screen right)."""
        if random.random() < config.OBSTACLE_SPAWN_CHANCE and len(self.vehicles) < config.MAX_OBSTACLES:
            lane_id = random.randint(0, self.road.num_lanes - 1)
            # Spawn ahead in right side with lane-aligned Y
            x = config.SCREEN_WIDTH + random.uniform(30, 180)
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
