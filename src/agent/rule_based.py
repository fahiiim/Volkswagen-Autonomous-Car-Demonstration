# Rule-based agent for Phase 1 baseline

import config


class RuleBasedAgent:
    """
    Simple rule-based agent for baseline performance.
    Decision logic:
    1. If obstacle detected ahead and too close → brake or turn
    2. If lane deviation too large → steer back to center
    3. Otherwise → maintain target speed
    """
    
    def __init__(self, simulation, sensors):
        self.simulation = simulation
        self.sensors = sensors
    
    def decide(self):
        """
        Make decision based on current state.
        
        Returns:
            (acceleration, steering_angle) tuple
        """
        state = self.sensors.extract_state()
        acceleration = 0
        steering_angle = 0
        
        # Get nearby obstacles
        obstacles = self.sensors.get_obstacles_ahead()
        lane_deviation = self.sensors.get_lane_deviation()
        
        # Rule 1: Handle obstacles
        if obstacles:
            closest = obstacles[0]
            distance = closest['distance']
            
            # Critical range - must react
            if distance < config.RULE_BASED_CRITICAL_DISTANCE:
                # Try to change lane if available
                current_lane = self.sensors.get_current_lane()
                neighbor_lanes = []
                
                if current_lane > 0:
                    neighbor_lanes.append(current_lane - 1)
                if current_lane < self.simulation.road.num_lanes - 1:
                    neighbor_lanes.append(current_lane + 1)
                
                # Check if we can safely change lane
                if neighbor_lanes:
                    # Simple heuristic: change to first available lane
                    target_lane = neighbor_lanes[0]
                    target_y = self.simulation.road.get_lane_center_y(target_lane)
                    lane_error = target_y - self.simulation.player_vehicle.y
                    
                    if lane_error > 0:
                        steering_angle = config.STEERING_ANGLE_MAX * 0.7
                    else:
                        steering_angle = -config.STEERING_ANGLE_MAX * 0.7
                
                # Emergency braking
                acceleration = -config.BRAKING_DECELERATION
            
            # Safe but uncomfortable distance - reduce speed
            elif distance < config.RULE_BASED_SAFE_DISTANCE:
                acceleration = -config.BRAKING_DECELERATION * 0.5  # Gentle braking
        
        # Rule 2: Lane keeping
        if abs(lane_deviation) > config.RULE_BASED_LANE_TOLERANCE:
            # Proportional steering toward lane center
            deviation_ratio = lane_deviation / (config.LANE_HEIGHT / 2)
            steering_angle = -deviation_ratio * config.STEERING_ANGLE_MAX * 0.5
        
        # Rule 3: Speed maintenance
        current_speed = self.simulation.player_vehicle.speed
        if current_speed < config.RULE_BASED_TARGET_SPEED and acceleration == 0:
            acceleration = config.ACCELERATION
        elif current_speed > config.RULE_BASED_TARGET_SPEED + 50:
            acceleration = -config.BRAKING_DECELERATION * 0.3
        
        # Clamp steering
        steering_angle = max(-config.STEERING_ANGLE_MAX, min(config.STEERING_ANGLE_MAX, steering_angle))
        
        return acceleration, steering_angle
    
    def name(self):
        return "RuleBasedAgent"
