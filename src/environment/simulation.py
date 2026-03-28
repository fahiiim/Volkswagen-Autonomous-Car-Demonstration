# Main simulation engine

import pygame
import config
from src.environment.road import Road
from src.environment.vehicle import Vehicle
from src.environment.obstacles import ObstacleManager


class Simulation:
    """
    Main simulation engine. Orchestrates road, player vehicle, obstacles, and physics.
    """
    
    def __init__(self, screen_width, screen_height, num_lanes):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.num_lanes = num_lanes
        
        # Initialize components
        self.road = Road(screen_width, screen_height, num_lanes)
        start_y = self.road.get_lane_center_y(config.PLAYER_START_LANE)
        self.player_vehicle = Vehicle(
            config.PLAYER_START_X,
            start_y,
            config.PLAYER_CAR_WIDTH,
            config.PLAYER_CAR_HEIGHT,
            config.PLAYER_CAR_COLOR,
            max_speed=config.MAX_SPEED
        )
        self.obstacle_manager = ObstacleManager(self.road)
        
        # State tracking
        self.time_elapsed = 0
        self.collision_occurred = False
        self.episode_reward = 0
        self.steps = 0
    
    def reset(self):
        """Reset simulation to initial state."""
        start_y = self.road.get_lane_center_y(config.PLAYER_START_LANE)
        self.player_vehicle.reset(config.PLAYER_START_X, start_y)
        self.player_vehicle.speed = config.RULE_BASED_TARGET_SPEED
        self.obstacle_manager.reset()
        self.time_elapsed = 0
        self.collision_occurred = False
        self.episode_reward = 0
        self.steps = 0
    
    def step(self, dt, action=None):
        """
        Advance simulation by dt seconds.
        
        Args:
            dt: Time step (seconds)
            action: (accel, steering_angle) tuple or None for manual control
        
        Returns:
            reward: float, step reward
            done: bool, episode terminated?
            info: dict, additional info
        """
        self.steps += 1
        self.time_elapsed += dt
        
        # Update road animations
        self.road.update(dt)
        
        # Apply action if provided
        if action is not None:
            accel, steering = action
            self.player_vehicle.accelerate(accel)
            self.player_vehicle.set_steering(steering, dt)
        
        # Update physics
        self.player_vehicle.update(dt)
        self.obstacle_manager.update(dt, self.player_vehicle.speed)

        # Camera-like behavior: keep ego X anchored so simulation looks like a highway game.
        self.player_vehicle.x = config.PLAYER_START_X
        self.player_vehicle.vx = 0
        # Do not allow reverse for ego in this demo.
        if self.player_vehicle.speed < 0:
            self.player_vehicle.speed = 0
        
        # Check collisions
        if self.obstacle_manager.check_collisions(self.player_vehicle):
            self.collision_occurred = True
        
        # Compute reward
        reward = self._compute_reward()
        self.episode_reward += reward
        
        # Check if episode is done
        done = self.collision_occurred or self.time_elapsed > 120  # Max 2 minutes
        
        info = {
            'time': self.time_elapsed,
            'steps': self.steps,
            'collision': self.collision_occurred,
            'reward': reward,
            'total_reward': self.episode_reward,
            'lane_id': self.road.get_lane_id(self.player_vehicle.y)
        }
        
        return reward, done, info
    
    def _compute_reward(self):
        """Compute step reward based on current state."""
        reward = config.REWARD_ALIVE  # Base reward for staying alive
        
        # Penalty for lane deviation (proportional to distance from center)
        target_y = self.road.get_lane_center_y(self.road.get_lane_id(self.player_vehicle.y))
        lane_deviation = abs(target_y - self.player_vehicle.y)
        reward += config.REWARD_LANE_DEVIATION * lane_deviation  # Negative coefficient = penalty
        
        # Collision penalty (large negative)
        if self.collision_occurred:
            reward += config.REWARD_COLLISION
        
        return reward
    
    def render(self, surface):
        """Draw everything to the pygame surface."""
        # Draw road
        self.road.draw(surface)
        
        # Draw obstacles
        self.obstacle_manager.draw(surface)
        
        # Draw player vehicle
        self.player_vehicle.draw(surface)
    
    def get_state(self):
        """Get simulation state for agent."""
        return {
            'player_pos': (self.player_vehicle.x, self.player_vehicle.y),
            'player_speed': self.player_vehicle.speed,
            'player_angle': self.player_vehicle.angle,
            'lane_id': self.road.get_lane_id(self.player_vehicle.y),
            'obstacles': [obs.get_state() for obs in self.obstacle_manager.get_all_obstacles()],
            'time': self.time_elapsed,
            'collision': self.collision_occurred
        }
    
    def get_nearby_obstacles(self, max_distance=config.RULE_BASED_DETECTION_RANGE):
        """Get obstacles ahead in ego lane corridor (forward X distance)."""
        nearby = []
        player_x = self.player_vehicle.x
        player_y = self.player_vehicle.y
        lane_corridor = config.LANE_HEIGHT * 0.35
        
        for obs in self.obstacle_manager.get_all_obstacles():
            obs_x = obs.x
            obs_y = obs.y
            # Forward distance on highway axis: positive = ahead (to the right)
            forward_distance = obs_x - player_x
            lateral_offset = abs(obs_y - player_y)
            
            # Detect only obstacles ahead and roughly in our lane corridor
            if 0 < forward_distance < max_distance and lateral_offset < lane_corridor:
                nearby.append({
                    'id': id(obs),
                    'x': obs.x,
                    'y': obs.y,
                    'distance': forward_distance,
                    'speed': obs.speed,
                    'lateral_offset': lateral_offset,
                    'type': 'vehicle' if hasattr(obs, 'lane_id') else 'pedestrian'
                })
        
        return sorted(nearby, key=lambda o: o['distance'])
