# Configuration file for Self-Driving Car Simulation

# ============ SCREEN & DISPLAY ============
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (50, 50, 50)  # Dark gray

# ============ ROAD CONFIGURATION ============
NUM_LANES = 3
LANE_HEIGHT = SCREEN_HEIGHT // NUM_LANES
LANE_WIDTH = SCREEN_WIDTH

# Road markings
CENTER_LINE_COLOR = (255, 255, 0)  # Yellow
EDGE_LINE_COLOR = (255, 255, 255)  # White
LINE_WIDTH = 2

# ============ VEHICLE CONFIGURATION ============
PLAYER_CAR_WIDTH = 30
PLAYER_CAR_HEIGHT = 50
PLAYER_CAR_COLOR = (0, 255, 0)  # Green
PLAYER_START_LANE = 1  # Middle lane (0-indexed)
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - 100

# Physics
MAX_SPEED = 300  # pixels per second
ACCELERATION = 150  # pixels per second squared
BRAKING_DECELERATION = 200  # pixels per second squared
STEERING_ANGLE_MAX = 15  # degrees, smoothly applied
TURNING_SPEED = 180  # degrees per second

# ============ OBSTACLE CONFIGURATION ============
OBSTACLE_CAR_WIDTH = 25
OBSTACLE_CAR_HEIGHT = 40
OBSTACLE_CAR_COLOR = (200, 0, 0)  # Red

PEDESTRIAN_WIDTH = 15
PEDESTRIAN_HEIGHT = 15
PEDESTRIAN_COLOR = (0, 0, 255)  # Blue

# Obstacle spawning
OBSTACLE_SPAWN_INTERVAL = 2.0  # seconds
OBSTACLE_SPAWN_CHANCE = 0.7  # probability per spawn event
OBSTACLE_MIN_SPEED = 80  # pixels/sec
OBSTACLE_MAX_SPEED = 250  # pixels/sec
MAX_OBSTACLES = 15

# ============ AGENT CONFIGURATION ============
RULE_BASED_DETECTION_RANGE = 150  # pixels ahead to detect obstacles
RULE_BASED_LANE_TOLERANCE = 20  # pixels allowed deviation from lane center
RULE_BASED_CRITICAL_DISTANCE = 60  # collision threshold
RULE_BASED_SAFE_DISTANCE = 100  # comfortable following distance
RULE_BASED_TARGET_SPEED = 200  # pixels/sec

# ============ REWARD CONFIGURATION (Phase 2) ============
REWARD_ALIVE = 1.0
REWARD_COLLISION = -500.0
REWARD_LANE_DEVIATION = -0.1  # per pixel away from lane center
REWARD_SPEED_BONUS = 0.0  # can be positive if speed is desired

# ============ DEBUG & LOGGING ============
DEBUG_MODE = True
LOG_STATE = False  # If True, logs state to file each frame
LOG_FILE = "simulation_log.csv"
