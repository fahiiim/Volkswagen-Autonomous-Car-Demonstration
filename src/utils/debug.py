# Debug utilities and visualization

import pygame
from src.utils.constants import DEBUG_TEXT_COLOR, DEBUG_TEXT_SIZE, DEBUG_FPS_X, DEBUG_FPS_Y, DEBUG_INFO_SPACING


class DebugOverlay:
    """Render debug information on screen."""
    
    def __init__(self, font_size=12):
        self.font = pygame.font.Font(None, font_size)
    
    def render_fps(self, surface, clock, x=DEBUG_FPS_X, y=DEBUG_FPS_Y):
        """Render FPS counter."""
        fps = int(clock.get_fps())
        text = self.font.render(f"FPS: {fps}", True, DEBUG_TEXT_COLOR)
        surface.blit(text, (x, y))
    
    def render_agent_state(self, surface, agent, simulation, x=DEBUG_FPS_X, y=DEBUG_FPS_Y + DEBUG_INFO_SPACING * 2):
        """Render agent and simulation state."""
        lines = [
            f"Speed: {simulation.player_vehicle.speed:.1f} px/s",
            f"Angle: {simulation.player_vehicle.angle:.1f}°",
            f"Lane: {simulation.road.get_lane_id(simulation.player_vehicle.y)}",
            f"Time: {simulation.time_elapsed:.1f}s",
            f"Reward: {simulation.episode_reward:.1f}",
            f"Obstacles: {len(simulation.obstacle_manager.get_all_obstacles())}",
            f"Collision: {simulation.collision_occurred}",
        ]
        
        for i, line in enumerate(lines):
            text = self.font.render(line, True, DEBUG_TEXT_COLOR)
            surface.blit(text, (x, y + i * DEBUG_INFO_SPACING))
    
    def render_nearest_obstacle(self, surface, simulation, x=DEBUG_FPS_X, y=DEBUG_FPS_Y + DEBUG_INFO_SPACING * 10):
        """Show nearest obstacle info."""
        obstacles = simulation.get_nearby_obstacles()
        
        if obstacles:
            closest = obstacles[0]
            lines = [
                "Nearest Obstacle:",
                f"  Distance: {closest['distance']:.1f} px",
                f"  Speed: {closest['speed']:.1f} px/s",
                f"  Type: {closest['type']}",
            ]
        else:
            lines = ["No nearby obstacles"]
        
        for i, line in enumerate(lines):
            text = self.font.render(line, True, DEBUG_TEXT_COLOR)
            surface.blit(text, (x, y + i * DEBUG_INFO_SPACING))
    
    def draw_detection_zone(self, surface, simulation):
        """Draw detection range around player vehicle."""
        import config
        import pygame as pg
        
        player = simulation.player_vehicle
        center = (int(player.x), int(player.y))
        radius = int(config.RULE_BASED_DETECTION_RANGE)
        
        # Draw detection radius
        pg.draw.circle(surface, (100, 100, 100), center, radius, 1)


class StateLogger:
    """Log simulation state to file."""
    
    def __init__(self, filename='simulation_log.csv'):
        self.filename = filename
        self.log_file = None
        self.write_header = True
    
    def open(self):
        """Open log file for writing."""
        self.log_file = open(self.filename, 'w')
    
    def close(self):
        """Close log file."""
        if self.log_file:
            self.log_file.close()
    
    def log_state(self, simulation, agent, action):
        """Log a simulation step."""
        if not self.log_file:
            return
        
        player = simulation.player_vehicle
        obstacles = simulation.get_nearby_obstacles()
        
        # Header
        if self.write_header:
            header = "time,step,player_x,player_y,player_speed,player_angle,lane_id,action_accel,action_steer,num_obstacles,collision,reward,total_reward\n"
            self.log_file.write(header)
            self.write_header = False
        
        # Data
        accel, steer = action if action else (0, 0)
        row = (
            f"{simulation.time_elapsed:.3f},"
            f"{simulation.steps},"
            f"{player.x:.1f},"
            f"{player.y:.1f},"
            f"{player.speed:.1f},"
            f"{player.angle:.1f},"
            f"{simulation.road.get_lane_id(player.y)},"
            f"{accel:.1f},"
            f"{steer:.1f},"
            f"{len(obstacles)},"
            f"{int(simulation.collision_occurred)},"
            f"{simulation.episode_reward:.1f}\n"
        )
        self.log_file.write(row)
        self.log_file.flush()
