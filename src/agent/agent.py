# Agent interface wrapper

from src.agent.sensors import Sensors
from src.agent.rule_based import RuleBasedAgent


class Agent:
    """
    High-level agent interface.
    Wraps sensors and decision logic (rule-based in Phase 1).
    """
    
    def __init__(self, simulation, agent_type='rule_based'):
        self.simulation = simulation
        self.sensors = Sensors(simulation)
        self.agent_type = agent_type
        
        if agent_type == 'rule_based':
            self.policy = RuleBasedAgent(simulation, self.sensors)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        self.action_history = []
        self.state_history = []
    
    def step(self):
        """
        Execute one agent step.
        
        Returns:
            action: (acceleration, steering_angle)
        """
        # Get state
        state = self.sensors.extract_state()
        self.state_history.append(state)
        
        # Decide action
        action = self.policy.decide()
        self.action_history.append(action)
        
        return action
    
    def get_state(self):
        """Get last extracted state."""
        if self.state_history:
            return self.state_history[-1]
        return None
    
    def reset(self):
        """Reset agent history."""
        self.action_history = []
        self.state_history = []
    
    def log_summary(self):
        """Return summary of agent performance."""
        return {
            'agent_type': self.agent_type,
            'steps': len(self.action_history),
            'collision': self.simulation.collision_occurred,
            'time_survived': self.simulation.time_elapsed,
            'reward': self.simulation.episode_reward
        }
