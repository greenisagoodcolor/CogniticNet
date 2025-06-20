"""
Active Inference Demo

This example demonstrates how to use the Active Inference framework in FreeAgentics
to create an intelligent agent that learns and adapts to its environment.
"""
import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from ....freeagentics_new.inference.engine.generative-model import DiscreteGenerativeModel, ModelDimensions, ModelParameters
from inference.engine.inference import VariationalInference
from ....freeagentics_new.inference.engine.policy-selection import PolicySelector, PolicyConfig
from ....freeagentics_new.inference.engine.precision import PrecisionController, PrecisionConfig
from ....freeagentics_new.inference.engine.parameter-learning import create_parameter_learner, LearningConfig
from ....freeagentics_new.inference.engine.active-learning import ActiveLearner, LearningConfig as ActiveLearningConfig
from ....freeagentics_new.inference.engine.computational-optimization import ComputationalOptimizer, OptimizationConfig
from ....freeagentics_new.inference.engine.diagnostics import DiagnosticSuite, DiagnosticConfig

class GridWorldEnvironment:
    """Simple grid world environment for demonstration"""

    def __init__(self, size=5):
        self.size = size
        self.agent_pos = [0, 0]
        self.goal_pos = [size - 1, size - 1]
        self.obstacles = [(2, 2), (2, 3), (3, 2)]

    def reset(self):
        """Reset environment to initial state"""
        self.agent_pos = [0, 0]
        return self._get_observation()

    def step(self, action):
        """Execute action and return observation"""
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        new_pos = [self.agent_pos[0] + moves[action][0], self.agent_pos[1] + moves[action][1]]
        if 0 <= new_pos[0] < self.size and 0 <= new_pos[1] < self.size and (tuple(new_pos) not in self.obstacles):
            self.agent_pos = new_pos
        obs = self._get_observation()
        reward = 1.0 if self.agent_pos == self.goal_pos else -0.01
        done = self.agent_pos == self.goal_pos
        return (obs, reward, done)

    def _get_observation(self):
        """Get observation based on agent position"""
        dx = self.goal_pos[0] - self.agent_pos[0]
        dy = self.goal_pos[1] - self.agent_pos[1]
        if dx > 0 and dy > 0:
            return 0
        elif dx > 0 and dy <= 0:
            return 1
        elif dx <= 0 and dy > 0:
            return 2
        else:
            return 3

    def render(self, ax=None):
        """Render the environment"""
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.clear()
        for i in range(self.size + 1):
            ax.axhline(i, color='gray', linewidth=0.5)
            ax.axvline(i, color='gray', linewidth=0.5)
        for obs in self.obstacles:
            ax.add_patch(plt.Rectangle((obs[1], obs[0]), 1, 1, facecolor='gray', edgecolor='black'))
        ax.add_patch(plt.Rectangle((self.goal_pos[1], self.goal_pos[0]), 1, 1, facecolor='green', edgecolor='black', alpha=0.5))
        ax.add_patch(plt.Circle((self.agent_pos[1] + 0.5, self.agent_pos[0] + 0.5), 0.3, facecolor='blue', edgecolor='black'))
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.set_title('Grid World Environment')
        return ax

class ActiveInferenceAgent:
    """Active Inference agent for grid world navigation"""

    def __init__(self, config=None):
        self.dims = ModelDimensions(num_states=16, num_observations=4, num_actions=4)
        self.params = ModelParameters(use_gpu=torch.cuda.is_available(), precision=1e-16)
        self.gen_model = DiscreteGenerativeModel(self.dims, self.params)
        self._initialize_model()
        self.inference = VariationalInference(self.dims, self.params)
        self.policy_config = PolicyConfig(precision=2.0, planning_horizon=3, use_habits=True)
        self.policy_selector = PolicySelector(self.policy_config)
        self.precision_config = PrecisionConfig(initial_precision=1.0, adaptation_rate=0.1, use_volatility_estimation=True)
        self.precision_controller = PrecisionController(self.precision_config)
        self.learning_config = LearningConfig(learning_rate_A=0.05, learning_rate_B=0.05, use_bayesian_learning=True, use_experience_replay=True)
        self.param_learner = create_parameter_learner('online', self.learning_config, generative_model=self.gen_model)
        self.active_config = ActiveLearningConfig(exploration_weight=0.3, uncertainty_method='entropy')
        self.active_learner = ActiveLearner(self.active_config, self.gen_model)
        self.opt_config = OptimizationConfig(use_sparse_operations=True, use_caching=True, use_gpu=self.params.use_gpu)
        self.optimizer = ComputationalOptimizer(self.opt_config)
        self.belief = torch.ones(self.dims.num_states) / self.dims.num_states
        self.episode_rewards = []
        self.episode_lengths = []

    def _initialize_model(self):
        """Initialize the generative model with reasonable priors"""
        self.gen_model.A = torch.zeros(self.dims.num_observations, self.dims.num_states)
        for s in range(self.dims.num_states):
            row = s // 4
            col = s % 4
            if row < 2 and col < 2:
                obs = 0
            elif row < 2 and col >= 2:
                obs = 1
            elif row >= 2 and col < 2:
                obs = 2
            else:
                obs = 3
            self.gen_model.A[obs, s] = 0.8
            self.gen_model.A[(obs + 1) % 4, s] = 0.1
            self.gen_model.A[(obs - 1) % 4, s] = 0.1
        self.gen_model.B = torch.zeros(self.dims.num_states, self.dims.num_states, self.dims.num_actions)
        for a in range(self.dims.num_actions):
            for s in range(self.dims.num_states):
                row = s // 4
                col = s % 4
                if a == 0 and row > 0:
                    next_s = (row - 1) * 4 + col
                elif a == 1 and col < 3:
                    next_s = row * 4 + (col + 1)
                elif a == 2 and row < 3:
                    next_s = (row + 1) * 4 + col
                elif a == 3 and col > 0:
                    next_s = row * 4 + (col - 1)
                else:
                    next_s = s
                self.gen_model.B[next_s, s, a] = 0.9
                self.gen_model.B[s, s, a] += 0.1
        self.gen_model.B = self.gen_model.B / self.gen_model.B.sum(dim=0, keepdim=True)
        self.gen_model.C = torch.ones(self.dims.num_observations) * 0.1
        self.gen_model.C[3] = 0.8
        self.gen_model.C = self.gen_model.C / self.gen_model.C.sum()
        self.gen_model.D = torch.zeros(self.dims.num_states)
        self.gen_model.D[0] = 1.0

    def observe(self, observation):
        """Update beliefs based on observation"""
        obs_vec = torch.zeros(self.dims.num_observations)
        obs_vec[observation] = 1.0
        self.belief = self.optimizer.optimized_belief_update(self.belief, obs_vec, self.gen_model.A)
        return self.belief

    def act(self, exploration_bonus=0.0):
        """Select action based on current beliefs"""
        precision = self.precision_controller.get_precision()
        G_values = self.policy_selector.compute_expected_free_energy(self.belief, self.gen_model.A, self.gen_model.B, self.gen_model.C, num_actions=self.dims.num_actions, horizon=self.policy_config.planning_horizon, precision=precision)
        if exploration_bonus > 0:
            G_adjusted = self.active_learner.select_informative_action(self.belief, G_values)
        else:
            G_adjusted = G_values
        action_probs = self.policy_selector.select_action(G_adjusted, precision)
        action = torch.multinomial(action_probs, 1).item()
        return (action, action_probs)

    def learn(self, prev_belief, action, observation, reward):
        """Learn from experience"""
        pred_error = -torch.log(self.gen_model.A[observation, :] @ prev_belief + 1e-16)
        self.precision_controller.update_precision(pred_error.item())
        action_vec = torch.zeros(self.dims.num_actions)
        action_vec[action] = 1.0
        obs_vec = torch.zeros(self.dims.num_observations)
        obs_vec[observation] = 1.0
        self.param_learner.observe(state=prev_belief, action=action_vec, observation=obs_vec, next_state=self.belief, reward=torch.tensor(reward))

    def train_episode(self, env, max_steps=100, exploration_decay=0.95):
        """Train agent for one episode"""
        obs = env.reset()
        self.belief = torch.ones(self.dims.num_states) / self.dims.num_states
        total_reward = 0
        steps = 0
        exploration = self.active_config.exploration_weight
        for step in range(max_steps):
            prev_belief = self.belief.clone()
            self.observe(obs)
            action, _ = self.act(exploration_bonus=exploration)
            next_obs, reward, done = env.step(action)
            self.learn(prev_belief, action, next_obs, reward)
            total_reward += reward
            steps += 1
            if done:
                break
            obs = next_obs
            exploration *= exploration_decay
        self.episode_rewards.append(total_reward)
        self.episode_lengths.append(steps)
        return (total_reward, steps)

def main():
    """Run Active Inference demonstration"""
    print('Active Inference Demo: Grid World Navigation\n')
    env = GridWorldEnvironment(size=5)
    agent = ActiveInferenceAgent()
    diag_config = DiagnosticConfig(save_figures=True, figure_dir=Path('./active_inference_demo_results'), enable_realtime=False)
    diagnostics = DiagnosticSuite(diag_config)
    belief_tracker = diagnostics.create_belief_tracker('grid_agent', num_states=16, state_labels=[f'Pos({i // 4},{i % 4})' for i in range(16)])
    num_episodes = 50
    print('Training agent...')
    for episode in range(num_episodes):
        reward, steps = agent.train_episode(env)
        belief_tracker.record_belief(agent.belief)
        vfe_accuracy = -torch.sum(agent.belief * torch.log(agent.belief + 1e-16))
        vfe_complexity = torch.sum((agent.belief - agent.gen_model.D) ** 2)
        diagnostics.fe_monitor.record_vfe(accuracy=vfe_accuracy.item(), complexity=vfe_complexity.item())
        if episode % 10 == 0:
            print(f'Episode {episode}: Reward = {reward:.2f}, Steps = {steps}')
    print('\nTraining complete!')
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes[0, 0].plot(agent.episode_rewards)
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Total Reward')
    axes[0, 0].set_title('Learning Progress: Rewards')
    axes[0, 0].grid(True)
    axes[0, 1].plot(agent.episode_lengths)
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Steps to Goal')
    axes[0, 1].set_title('Learning Progress: Efficiency')
    axes[0, 1].grid(True)
    final_belief = agent.belief.detach().cpu().numpy()
    im = axes[1, 0].imshow(final_belief.reshape(4, 4), cmap='viridis')
    axes[1, 0].set_title('Final Belief State')
    axes[1, 0].set_xlabel('Column')
    axes[1, 0].set_ylabel('Row')
    plt.colorbar(im, ax=axes[1, 0])
    A_matrix = agent.gen_model.A.detach().cpu().numpy()
    im = axes[1, 1].imshow(A_matrix, cmap='viridis', aspect='auto')
    axes[1, 1].set_title('Learned Observation Model')
    axes[1, 1].set_xlabel('State')
    axes[1, 1].set_ylabel('Observation')
    plt.colorbar(im, ax=axes[1, 1])
    plt.tight_layout()
    plt.savefig('./active_inference_demo_results/training_results.png')
    plt.show()
    report = diagnostics.generate_report()
    print(f'\nDiagnostic Report:')
    print(f"- Total updates: {report['belief_statistics']['grid_agent']['total_updates']}")
    print(f"- Mean entropy: {report['belief_statistics']['grid_agent']['mean_entropy']:.3f}")
    learning_stats = agent.param_learner.get_statistics()
    print(f'\nLearning Statistics:')
    print(f"- Total experiences: {learning_stats['total_experiences']}")
    print(f"- Model updates: {learning_stats['num_updates']}")
    perf_report = agent.optimizer.get_performance_report()
    print(f'\nPerformance Report:')
    print(f"- Device: {perf_report['device']}")
    print(f"- Cache hit rate: {perf_report['cache_stats']['hit_rate']:.2%}")
    print('\nTesting learned agent...')
    env.reset()
    agent.belief = torch.ones(agent.dims.num_states) / agent.dims.num_states
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    for step in range(20):
        obs = env._get_observation()
        agent.observe(obs)
        action, action_probs = agent.act(exploration_bonus=0.0)
        env.render(ax)
        ax.set_title(f"Step {step}: Action = {['Up', 'Right', 'Down', 'Left'][action]}")
        plt.pause(0.5)
        _, _, done = env.step(action)
        if done:
            print(f'Goal reached in {step + 1} steps!')
            break
    plt.show()
    agent.optimizer.cleanup()
    print('\nDemo complete!')
if __name__ == '__main__':
    main()