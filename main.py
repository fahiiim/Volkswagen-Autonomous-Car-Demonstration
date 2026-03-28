# Main entry point for Self-Driving Car Simulation

import pygame
import sys
import config
from src.environment.simulation import Simulation
from src.agent.agent import Agent
from src.utils.debug import DebugOverlay, StateLogger


def main():
    """Main simulation loop."""
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Self-Driving Car Simulation - Phase 1")
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
    manual_control = False  # Set to True for manual keyboard control
    
    print("=" * 60)
    print("Self-Driving Car Simulation - Phase 1")
    print("=" * 60)
    print(f"Mode: {'Manual Control' if manual_control else 'Agent Control (Rule-Based)'}")
    print(f"Controls: ARROW KEYS (steering/speed), SPACE (toggle agent/manual), Q (quit)")
    print("=" * 60)
    
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
                    mode_str = "Manual" if manual_control else "Agent (Rule-Based)"
                    print(f"Switched to {mode_str} Control")
        
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
            print(f"\n[Episode {episode}] " + " | ".join([f"{k}: {v}" for k, v in summary.items()]))
            
            # Reset
            simulation.reset()
            agent.reset()
        
        # Render
        simulation.render(screen)
        
        # Draw debug overlay
        if config.DEBUG_MODE:
            debug_overlay.render_fps(screen, clock)
            debug_overlay.render_agent_state(screen, agent, simulation)
            debug_overlay.render_nearest_obstacle(screen, simulation)
            debug_overlay.draw_detection_zone(screen, simulation)
        
        pygame.display.flip()
    
    # Cleanup
    if config.LOG_STATE:
        state_logger.close()
    
    pygame.quit()
    print("\nSimulation ended. Goodbye!")
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


if __name__ == "__main__":
    main()
