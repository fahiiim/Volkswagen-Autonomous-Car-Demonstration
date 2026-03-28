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
        self.target_lane = None
    
    def decide(self):
        """
        Make decision based on current state.
        
        Returns:
            (acceleration, steering_angle) tuple
        """
        _ = self.sensors.extract_state()
        
        # Reset controls each decision cycle
        acceleration = 0
        steering_angle = 0
        
        current_lane = self.sensors.get_current_lane()

        # Continue an ongoing lane change to avoid indecisive oscillations.
        if self.target_lane is not None:
            target_y = self.simulation.road.get_lane_center_y(self.target_lane)
            lane_error = target_y - self.simulation.player_vehicle.y
            if abs(lane_error) <= (config.RULE_BASED_LANE_TOLERANCE * 0.6):
                self.target_lane = None
            else:
                steering_angle = max(-config.STEERING_ANGLE_MAX, min(config.STEERING_ANGLE_MAX, lane_error * 0.25))

        # Get nearby obstacles
        obstacles = self.sensors.get_obstacles_ahead()
        lane_deviation = self.sensors.get_lane_deviation()
        current_speed = self.simulation.player_vehicle.speed
        
        # Rule 1: Handle obstacles (safety-critical)
        if obstacles:
            closest = obstacles[0]
            distance = closest['distance']
            obstacle_rel_speed = closest['speed']  # obstacle_world - ego_speed
            closing_speed = max(0.0, -obstacle_rel_speed)
            ttc = float('inf') if closing_speed < 1e-3 else distance / closing_speed
            
            # Proactive and emergency maneuvers
            if distance < (config.RULE_BASED_SAFE_DISTANCE * 1.5) or ttc < 3.0:
                candidate_lanes = [lane for lane in range(self.simulation.road.num_lanes) if lane != current_lane]
                safest_lane = self._select_safest_lane(current_lane, candidate_lanes)

                # Initiate lane change if a safer option exists.
                if safest_lane != current_lane:
                    self.target_lane = safest_lane
                    target_y = self.simulation.road.get_lane_center_y(safest_lane)
                    lane_error = target_y - self.simulation.player_vehicle.y
                    steering_angle = max(-config.STEERING_ANGLE_MAX, min(config.STEERING_ANGLE_MAX, lane_error * 0.25))

                # Speed policy based on threat level.
                if distance < config.RULE_BASED_CRITICAL_DISTANCE or ttc < 1.1:
                    acceleration = -config.BRAKING_DECELERATION
                elif distance < config.RULE_BASED_SAFE_DISTANCE or ttc < 1.9:
                    acceleration = -config.BRAKING_DECELERATION * 0.65
                elif ttc < 3.0:
                    acceleration = -config.BRAKING_DECELERATION * 0.35

            # Adaptive follow-speed: match slower traffic to avoid rear-end collision.
            obstacle_world_speed = max(0.0, current_speed + obstacle_rel_speed)
            speed_buffer = 12.0
            desired_follow_speed = max(80.0, min(config.RULE_BASED_TARGET_SPEED, obstacle_world_speed - speed_buffer + distance * 0.20))
            speed_error = desired_follow_speed - current_speed
            if speed_error < 0:
                adaptive_brake = max(-config.BRAKING_DECELERATION, speed_error * 1.6)
                acceleration = min(acceleration, adaptive_brake)
        
        # Rule 2: Lane keeping (continuous control)
        if self.target_lane is None and abs(lane_deviation) > config.RULE_BASED_LANE_TOLERANCE:
            # Proportional steering back to center
            deviation_ratio = lane_deviation / (config.LANE_HEIGHT / 2)
            steering_angle = -deviation_ratio * config.STEERING_ANGLE_MAX * 0.4
        
        # Rule 3: Speed maintenance (if no immediate threats)
        if acceleration == 0:  # No obstacle avoidance happening
            if current_speed < config.RULE_BASED_TARGET_SPEED:
                acceleration = config.ACCELERATION
            elif current_speed > config.RULE_BASED_TARGET_SPEED + 25:
                acceleration = -config.BRAKING_DECELERATION * 0.3
        
        # Clamp outputs
        steering_angle = max(-config.STEERING_ANGLE_MAX, min(config.STEERING_ANGLE_MAX, steering_angle))
        
        return acceleration, steering_angle

    def _select_safest_lane(self, current_lane, candidate_lanes):
        """Pick lane with maximum nearest forward gap."""
        best_lane = current_lane
        best_gap = -1

        player_x = self.simulation.player_vehicle.x
        lane_half_height = config.LANE_HEIGHT * 0.35

        for lane in candidate_lanes:
            lane_center = self.simulation.road.get_lane_center_y(lane)
            nearest_gap = float('inf')
            blocked_nearby = False

            for obs in self.simulation.obstacle_manager.get_all_obstacles():
                if abs(obs.y - lane_center) <= lane_half_height:
                    gap = obs.x - player_x
                    if abs(gap) < (config.RULE_BASED_CRITICAL_DISTANCE * 0.9):
                        blocked_nearby = True
                    if 0 < gap < nearest_gap:
                        nearest_gap = gap

            if blocked_nearby:
                continue

            if nearest_gap == float('inf'):
                nearest_gap = 9999

            if nearest_gap > best_gap:
                best_gap = nearest_gap
                best_lane = lane

        return best_lane
    
    def name(self):
        return "RuleBasedAgent"
