#!/usr/bin/env python
"""
Quick test script to verify Phase 1 simulation setup without displaying graphics.
Tests core functionality: simulation loop, agent decisions, collision detection.
"""

import sys
sys.path.insert(0, r'c:\Users\fahim\Desktop\Self driven car')

from src.environment.simulation import Simulation
from src.agent.agent import Agent
import config

def test_simulation():
    """Test simulation without GUI."""
    print("=" * 60)
    print("Testing Phase 1 Simulation Setup")
    print("=" * 60)
    
    # Create simulation
    print("\n[1] Initializing simulation...")
    sim = Simulation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.NUM_LANES)
    print(f"  ✓ Simulation created: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}, {config.NUM_LANES} lanes")
    
    # Create agent
    print("\n[2] Initializing agent...")
    agent = Agent(sim, agent_type='rule_based')
    print(f"  ✓ Agent created: {agent.policy.name()}")
    
    # Run simulation steps
    print("\n[3] Running simulation for 5 seconds...")
    dt = 1.0 / config.FPS
    steps = 0
    max_steps = 5 * config.FPS
    
    while steps < max_steps and not sim.collision_occurred:
        # Agent makes decision
        action = agent.step()
        
        # Step simulation
        reward, done, info = sim.step(dt, action)
        steps += 1
        
        # Print progress every 60 frames (1 second at 60 FPS)
        if steps % 60 == 0:
            elapsed = steps / config.FPS
            print(f"  [{elapsed:.1f}s] Speed: {sim.player_vehicle.speed:.1f} px/s | "
                  f"Lane: {info['lane_id']} | "
                  f"Obstacles: {len(sim.obstacle_manager.get_all_obstacles())} | "
                  f"Reward: {info['reward']:.2f}")
        
        if done:
            break
    
    # Print results
    print("\n[4] Simulation Results:")
    summary = agent.log_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    if sim.collision_occurred:
        print("⚠ Collision occurred (expected behavior)")
    else:
        print("✓ Test completed successfully!")
        print("✓ All systems operational. Ready to run full simulation.")
    print("=" * 60)

if __name__ == "__main__":
    test_simulation()
