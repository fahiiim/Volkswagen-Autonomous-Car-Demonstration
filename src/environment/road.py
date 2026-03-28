# Road system with lanes and rendering

import pygame
import config


class Road:
    """
    Represents a multi-lane road system.
    Handles road rendering with lane markers.
    """
    
    def __init__(self, width, height, num_lanes):
        self.width = width
        self.height = height
        self.num_lanes = num_lanes
        self.lane_height = height / num_lanes
        
    def get_lane_center_y(self, lane_id):
        """Get the Y coordinate of a lane center."""
        if lane_id < 0 or lane_id >= self.num_lanes:
            lane_id = max(0, min(self.num_lanes - 1, lane_id))
        return (lane_id + 0.5) * self.lane_height
    
    def get_lane_id(self, y):
        """Get lane ID from Y coordinate."""
        lane_id = int(y / self.lane_height)
        return max(0, min(self.num_lanes - 1, lane_id))
    
    def draw(self, surface):
        """Draw road background and lane markings."""
        # Draw background
        surface.fill(config.BACKGROUND_COLOR)
        
        # Draw lane lines
        for lane_idx in range(self.num_lanes - 1):
            y = (lane_idx + 1) * self.lane_height
            pygame.draw.line(
                surface,
                config.CENTER_LINE_COLOR,
                (0, y),
                (self.width, y),
                config.LINE_WIDTH
            )
        
        # Draw edge lines
        pygame.draw.line(
            surface,
            config.EDGE_LINE_COLOR,
            (0, 0),
            (self.width, 0),
            config.LINE_WIDTH
        )
        pygame.draw.line(
            surface,
            config.EDGE_LINE_COLOR,
            (0, self.height - 1),
            (self.width, self.height - 1),
            config.LINE_WIDTH
        )
