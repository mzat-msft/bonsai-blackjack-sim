"""Main connector to the Bonsai platform."""
import argparse
import collections
import json
import random
import time

from microsoft_bonsai_api.simulator.client import (BonsaiClient,
                                                   BonsaiClientConfig)
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface, SimulatorState)

from blackjack.blackjack import SimulatorModel


parser = argparse.ArgumentParser(description="Run a simulation")
parser.add_argument('-p', '--policy', choices=['random'])
parser.add_argument('-e', '--episodes', type=int, default=100)


class BonsaiConnector:
    """
    Class for connecting the sim to the Bonsai platform.

    Parameters
    ----------
    if_json: str or Path
        A json file containing all information concerning
        the simulation. It must contain at least a ``name``
        and ``timeout`` field.
    sim_model: object
        A class that wraps the simulation.

    The sim_model must have some methods available for the
    connector to work correctly
    - ``step``: perform a sim iteration. Must accept an action.
    - ``reset``: reset the simulation and start a new episode.
    """
    def __init__(self, if_json, sim_model):
        with open(if_json, 'r') as fp:
            interface = json.load(fp)
        client_config = BonsaiClientConfig()
        self.workspace = client_config.workspace
        self.client = BonsaiClient(client_config)

        reg_info = SimulatorInterface(
            simulator_context=client_config.simulator_context,
            **interface,
        )
        self.registered_session = self.client.session.create(
            workspace_name=client_config.workspace,
            body=reg_info,
        )
        self.sim_model = sim_model()
        self.sim_model_state = {}
        self.sequence_id = 1

    def next_event(self):
        sim_state = SimulatorState(
            sequence_id=self.sequence_id,
            state=self.sim_model_state,
            halted=self.sim_model_state.get('halted', False),
        )
        event = self.client.session.advance(
            workspace_name=self.workspace,
            session_id=self.registered_session.session_id,
            body=sim_state,
        )
        self.sequence_id = event.sequence_id
        if event.type == 'Idle':
            time.sleep(event.idle.callback_time)
        elif event.type == 'EpisodeStart':
            self.sim_model_state = self.sim_model.reset()
        elif event.type == 'EpisodeStep':
            action = event.episode_step.action
            self.sim_model_state = self.sim_model.step(action)
            self.sim_model_state['action'] = action
        elif event.type == 'EpisodeFinish':
            self.sim_model_state = {}
        elif event.type == 'Unregister':
            print(
                "Simulator Session unregistered by platform because of ",
                event.unregister.details,
            )
        print(time.strftime('%H:%M:%S'), event.type, self.sim_model_state)

    def close_session(self):
        self.client.session.delete(
            workspace_name=self.workspace,
            session_id=self.registered_session.session_id,
        )


def get_reward(results):
    reward_mapping = {
        0: -100,
        1: 0,
        2: 1,
    }
    counter = collections.Counter(results)
    reward = 0
    total = 0
    for elem, cnt in counter.items():
        total += cnt
        reward += reward_mapping[elem] * cnt
    return reward / total


def random_policy(state):
    return {'command': random.choice([0, 1])}


def test_policy(n_games, policy):
    if policy == 'random':
        f_policy = random_policy
    else:
        raise ValueError(f'Policy {policy} not found.')
    print(f'Using {policy} policy.')

    model = SimulatorModel()
    results = []
    for game in range(n_games):
        state = model.reset()
        while state['result'] < 0:
            state = model.step(f_policy(state))
            if state['result'] >= 0:
                results.append(state['result'])
    reward = get_reward(results)
    print(reward)


def run_interface():
    bonsai_conn = BonsaiConnector(
        'blackjack-interface.json',
        SimulatorModel,
    )

    while True:
        try:
            bonsai_conn.next_event()
        except Exception as e:
            bonsai_conn.close_session()
            raise RuntimeError('Error in event loop') from e


def main():
    args = parser.parse_args()
    if args.policy:
        test_policy(args.episodes, args.policy)
    else:
        run_interface()


if __name__ == '__main__':
    main()
