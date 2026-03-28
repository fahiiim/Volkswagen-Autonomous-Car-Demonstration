# Road system with lanes and rendering

import pygame
import config


class Road:
    """
    Represents a multi-lane highway system.
    Handles road rendering with lane markers and professional visuals.
    """
    
    def __init__(self, width, height, num_lanes):
        self.width = width
        self.height = height
        self.num_lanes = num_lanes
        self.lane_height = height / num_lanes
        self.dash_offset = 0  # For animated lane markings
        
    def get_lane_center_y(self, lane_id):
        """Get the Y coordinate of a lane center."""
        if lane_id < 0 or lane_id >= self.num_lanes:
            lane_id = max(0, min(self.num_lanes - 1, lane_id))
        return (lane_id + 0.5) * self.lane_height
    
    def get_lane_id(self, y):
        """Get lane ID from Y coordinate."""
        lane_id = int(y / self.lane_height)
        return max(0, min(self.num_lanes - 1, lane_id))
    
    def update(self, dt):
        """Update road animations (lane marking movement)."""
        self.dash_offset += 200 * dt  # Scroll speed related to obstacle spawn rates
        self.dash_offset = self.dash_offset % 40  # Loop every 40 pixels
    
    def draw(self, surface):
        """Draw professional highway with lane markings."""
        # Draw asphalt background
        surface.fill((40, 40, 45))  # Dark asphalt color
        
        # Draw lane dividers (dashed yellow lines)
        for lane_idx in range(self.num_lanes - 1):
            y_pos = (lane_idx + 1) * self.lane_height
            self._draw_dashed_line(
                surface,
                (255, 255, 0),  # Yellow
                (0, y_pos),
                (self.width, y_pos),
                config.LINE_WIDTH,
                dash_length=20,
                gap_length=20,
                offset=self.dash_offset
            )
        
        # Draw solid road edges (white)
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (0, 0),
            (self.width, 0),
            config.LINE_WIDTH + 1
        )
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (0, self.height - 1),
            (self.width, self.height - 1),
            config.LINE_WIDTH + 1
        )
        
        # Draw subtle lane background shading for depth
        for lane_idx in range(self.num_lanes):
            lane_top = lane_idx * self.lane_height
            lane_rect = pygame.Rect(0, lane_top, self.width, self.lane_height)
            # Alternate slightly different shades
            color = (45, 45, 50) if lane_idx % 2 == 0 else (40, 40, 45)
            pygame.draw.rect(surface, color, lane_rect)
            
            # Draw lane center guidance line (slightly darker)
            center_y = self.get_lane_center_y(lane_idx)
            pygame.draw.line(
                surface,
                (60, 60, 65),
                (0, center_y),
                (self.width, center_y),
                1
            )
    
    def _draw_dashed_line(self, surface, color, start_pos, end_pos, width, dash_length=20, gap_length=20, offset=0):
        """Draw a dashed line with animation offset."""
        x_start, y_start = start_pos
        x_end, y_end = end_pos
        
        # Handle both horizontal and vertical lines
        if y_start == y_end:  # Horizontal line
            current_x = x_start - offset
            while current_x < x_end:
                dash_end_x = min(current_x + dash_length, x_end)
                if current_x < x_end:
                    pygame.draw.line(surface, color, (current_x, y_start), (dash_end_x, y_end), width)
                current_x += dash_length + gap_length
        else:  # Vertical line
            current_y = y_start - offset
            while current_y < y_end:
                dash_end_y = min(current_y + dash_length, y_end)
                if current_y < y_end:
                    pygame.draw.line(surface, color, (x_start, current_y), (x_end, dash_end_y), width)
                current_y += dash_length + gap_length
