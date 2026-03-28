# Main entry point for Self-Driving Car Simulation

import pygame
import sys
import config
from src.environment.simulation import Simulation
from src.agent.agent import Agent
from src.utils.debug import DebugOverlay, StateLogger


def main():
    """Main simulation loop for professional highway autonomous driving."""
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Volkswagen Autonomous Car Simulation - Phase 1")
    clock = pygame.time.Clock()
    
    # Initialize simulation and agent
    simulation = Simulation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.NUM_LANES)
    agent = Agent(simulation, agent_type='rule_based')
    debug_overlay = DebugOverlay(font_size=11)
    state_logger = StateLogger(config.LOG_FILE)
    
    if config.LOG_STATE:
        state_logger.open()
    
    # Simulation state
    episode = 0
    manual_control = False
    show_debug = config.DEBUG_MODE
    
    print("=" * 70)
    print("VOLKSWAGEN AUTONOMOUS CAR SIMULATION - PHASE 1 (PROFESSIONAL)")
    print("=" * 70)
    print(f"Platform: Autonomous Driving Research & Development")
    print(f"Mode: {'Manual Control' if manual_control else 'Autonomous Agent (Rule-Based)'}")
    print(f"Environment: Multi-lane Highway Simulation")
    print(f"Resolution: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT} | Lanes: {config.NUM_LANES}")
    print("-" * 70)
    print("CONTROLS:")
    print("  ↑ ↓      : Accelerate/Brake (manual mode only)")
    print("  ← →      : Steer left/right (manual mode only)")
    print("  SPACE    : Toggle Autonomous ↔ Manual Control")
    print("  D        : Toggle Debug Overlay")
    print("  Q        : Quit Simulation")
    print("=" * 70)
    print()
    
    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    manual_control = not manual_control
                    mode_str = "MANUAL CONTROL" if manual_control else "AUTONOMOUS AGENT"
                    print(f"\n► Mode switched to: {mode_str}")
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                    debug_str = "ON" if show_debug else "OFF"
                    print(f"► Debug overlay: {debug_str}")
        
        # Get action (manual or agent-based)
        if manual_control:
            action = _handle_manual_input(simulation)
        else:
            action = agent.step()
        
        # Step simulation
        reward, done, info = simulation.step(dt, action)
        
        # Log if enabled
        if config.LOG_STATE:
            state_logger.log_state(simulation, agent, action)
        
        # Handle episode termination
        if done:
            episode += 1
            summary = agent.log_summary()
            print(f"\n[Episode {episode}] SUMMARY:")
            for key, value in summary.items():
                if key == 'agent_type':
                    print(f"  Agent Type: {value}")
                elif key == 'steps':
                    print(f"  Total Steps: {value}")
                elif key == 'collision':
                    print(f"  Collision: {'YES ✗' if value else 'NO ✓ (Safe Landing)'}")
                elif key == 'time_survived':
                    print(f"  Time Survived: {value:.2f} seconds")
                elif key == 'reward':
                    print(f"  Episode Reward: {value:.2f}")
            print()
            
            # Reset
            simulation.reset()
            agent.reset()
        
        # Render
        screen.fill(config.BACKGROUND_COLOR)  # Clear screen
        simulation.render(screen)
        
        # Draw professional UI overlay
        _draw_professional_ui(screen, simulation, agent, clock, show_debug, manual_control, debug_overlay)
        
        pygame.display.flip()
    
    # Cleanup
    if config.LOG_STATE:
        state_logger.close()
    
    print("\n" + "=" * 70)
    print(f"Simulation Statistics:")
    print(f"  Total Episodes Run: {episode}")
    print(f"  Final Episode Time: {simulation.time_elapsed:.1f}s")
    print(f"  Final Episode Reward: {simulation.episode_reward:.1f}")
    print("=" * 70)
    print("Simulation ended gracefully. Thank you for using the system.")
    
    pygame.quit()
    sys.exit()


def _handle_manual_input(simulation):
    """Handle keyboard input for manual control."""
    keys = pygame.key.get_pressed()
    
    acceleration = 0
    steering = 0
    
    # Acceleration / Braking
    if keys[pygame.K_UP]:
        acceleration = config.ACCELERATION
    elif keys[pygame.K_DOWN]:
        acceleration = -config.BRAKING_DECELERATION
    
    # Steering
    if keys[pygame.K_LEFT]:
        steering = -config.STEERING_ANGLE_MAX
    elif keys[pygame.K_RIGHT]:
        steering = config.STEERING_ANGLE_MAX
    
    return acceleration, steering


def _draw_professional_ui(screen, simulation, agent, clock, show_debug, manual_control, debug_overlay):
    """Draw professional UI overlay with status information."""
    font_small = pygame.font.Font(None, 11)
    
    
    # Top status bar background
    status_bar_rect = pygame.Rect(0, 0, config.SCREEN_WIDTH, 60)
    pygame.draw.rect(screen, (20, 20, 25), status_bar_rect)
    pygame.draw.line(screen, (100, 200, 100), (0, 60), (config.SCREEN_WIDTH, 60), 2)
    
    # Top status info
    fps = int(clock.get_fps())
    mode_text = "MANUAL" if manual_control else "AUTONOMOUS"
    status_text = f"FPS: {fps} | Mode: {mode_text} | Speed: {simulation.player_vehicle.speed:.0f} px/s"
    status_surf = font_small.render(status_text, True, (100, 255, 100))
    screen.blit(status_surf, (10, 8))
    
    lane_info = f"Lane: {simulation.road.get_lane_id(simulation.player_vehicle.y)} | Time: {simulation.time_elapsed:.1f}s | Reward: {simulation.episode_reward:.1f}"
    lane_surf = font_small.render(lane_info, True, (255, 255, 255))
    screen.blit(lane_surf, (10, 25))
    
    obstacles_info = f"Obstacles: {len(simulation.obstacle_manager.get_all_obstacles())} | Collision: {'ALERT' if simulation.collision_occurred else 'SAFE'}"
    obs_color = (255, 100, 100) if simulation.collision_occurred else (100, 255, 100)
    obs_surf = font_small.render(obstacles_info, True, obs_color)
    screen.blit(obs_surf, (10, 42))
    
    # Bottom status bar
    bottom_bar_rect = pygame.Rect(0, config.SCREEN_HEIGHT - 40, config.SCREEN_WIDTH, 40)
    pygame.draw.rect(screen, (20, 20, 25), bottom_bar_rect)
    pygame.draw.line(screen, (100, 200, 100), (0, config.SCREEN_HEIGHT - 40), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT - 40), 2)
    
    # Bottom info
    control_text = "[SPACE] Toggle | [D] Debug | [Q] Quit"
    control_surf = font_small.render(control_text, True, (150, 150, 255))
    screen.blit(control_surf, (10, config.SCREEN_HEIGHT - 32))
    
    # Debug overlay (if enabled)
    if show_debug:
        debug_overlay.render_agent_state(screen, agent, simulation, x=config.SCREEN_WIDTH - 320, y=70)
        debug_overlay.render_nearest_obstacle(screen, simulation, x=config.SCREEN_WIDTH - 320, y=200)


if __name__ == "__main__":
    main()
