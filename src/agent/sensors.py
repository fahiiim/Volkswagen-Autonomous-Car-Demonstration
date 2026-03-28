# Sensor system for state extraction

import numpy as np
import config


class Sensors:
    """
    Extracts agent-observable state from simulation.
    Simulates a perception system (no real camera, just game state).
    """
    
    def __init__(self, simulation):
        self.simulation = simulation
    
    def extract_state(self):
        """
        Extract normalized state for agent decision-making.
        
        Returns:
            dict with agent-relevant observations
        """
        player = self.simulation.player_vehicle
        road = self.simulation.road
        
        # Own state
        lane_id = road.get_lane_id(player.y)
        lane_center_y = road.get_lane_center_y(lane_id)
        lane_deviation = player.y - lane_center_y
        
        # Nearby obstacles
        nearby_obstacles = self.simulation.get_nearby_obstacles()
        
        # Find closest obstacle ahead
        closest_obstacle = None
        closest_distance = float('inf')
        if nearby_obstacles:
            closest_obstacle = nearby_obstacles[0]
            closest_distance = closest_obstacle['distance']
        
        state = {
            # Self state (normalized)
            'self_pos_x': player.x / config.SCREEN_WIDTH,  # [0, 1]
            'self_pos_y': player.y / config.SCREEN_HEIGHT,  # [0, 1]
            'self_speed': player.speed / config.MAX_SPEED,  # [0, 1]
            'self_angle': player.angle / config.STEERING_ANGLE_MAX,  # [-1, 1]
            'lane_id': lane_id,
            'lane_deviation': lane_deviation / (config.LANE_HEIGHT / 2),  # [-1, 1]
            
            # Obstacle state
            'obstacle_count': len(nearby_obstacles),
            'closest_obstacle_distance': closest_distance / config.RULE_BASED_DETECTION_RANGE if closest_distance < config.RULE_BASED_DETECTION_RANGE else 1.0,
            'closest_obstacle_speed': closest_obstacle['speed'] / config.OBSTACLE_MAX_SPEED if closest_obstacle else 0,
            'closest_obstacle_type': closest_obstacle['type'] if closest_obstacle else 'none',
            
            # Time state
            'time': self.simulation.time_elapsed / 120.0,  # Normalized to 2 min max
            'collision': self.simulation.collision_occurred
        }
        
        return state
    
    def get_obstacles_ahead(self):
        """Get list of obstacles ahead of the player."""
        return self.simulation.get_nearby_obstacles()
    
    def get_lane_center(self):
        """Get Y coordinate of current lane center."""
        lane_id = self.simulation.road.get_lane_id(self.simulation.player_vehicle.y)
        return self.simulation.road.get_lane_center_y(lane_id)
    
    def get_lane_deviation(self):
        """Get deviation from lane center."""
        return self.simulation.player_vehicle.y - self.get_lane_center()
    
    def get_current_lane(self):
        """Get current lane ID."""
        return self.simulation.road.get_lane_id(self.simulation.player_vehicle.y)
