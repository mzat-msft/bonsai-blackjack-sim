"""Main connector to the Bonsai platform."""
import argparse
import time
import traceback

from microsoft_bonsai_api.simulator.client import (BonsaiClient,
                                                   BonsaiClientConfig)
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface, SimulatorState)

from blackjack.blackjack import SimulatorModel
from blackjack.policies import AVAILABLE_POLICIES, evaluate_policy, generate_chart


parser = argparse.ArgumentParser(description="Run a simulation")
parser.add_argument('-p', '--policy', choices=AVAILABLE_POLICIES)
parser.add_argument('-e', '--episodes', type=int, default=100)
parser.add_argument('-v', '--verbose', action='store_true', default=False)
parser.add_argument(
    '--host', type=str, default='localhost', help='Host of deployed brain'
)
parser.add_argument('--port', type=int, default=5000, help='Port of deployed brain')
parser.add_argument(
    '--generate-chart', action='store_true', default=False,
    help='Generate a strategy chart from deployed brain',
)


class BonsaiConnector:
    """
    Class for connecting the sim to the Bonsai platform.

    Parameters
    ----------
    sim_model: object
        A class that wraps the simulation.
    verbose: bool
        If set to true enable API logging.

    ``sim_model`` must implement the following methods to work correctly
    with the connector:

    - ``step(action) -> sim_state``:
      perform a sim iteration. ``action`` is a dictionary that cointains
      as keys the name of all possible actions and their values as dictionary
      values. ``sim_state`` is the simulation state dictionary that is
      passed to Bonsai to get the next action.
    - ``reset(config) -> sim_state``:
        reset the simulation and start a new episode. Accepts ``config`` as
        dictionary with parameters to be used as configuration for the
        simulation episode.

    In addition, ``sim_model`` must have the following attribute

    - ``interface``: dict containing simulator informations to be used
      by the Bonsai Platform. (``name`` key is required)
    """
    def __init__(self, sim_model, *, verbose=False):
        self.sim_model = sim_model()
        client_config = BonsaiClientConfig(enable_logging=verbose)
        self.workspace = client_config.workspace
        self.client = BonsaiClient(client_config)

        reg_info = SimulatorInterface(
            simulator_context=client_config.simulator_context,
            **self.sim_model.interface,
        )
        self.registered_session = self.client.session.create(
            workspace_name=client_config.workspace,
            body=reg_info,
        )
        print(f'Created session with session_id {self.registered_session.session_id}')
        self.sim_model_state = {}
        self.sequence_id = 1

    def next_event(self):
        """Poll the Bonsai platform for the next event and advance the state."""
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
            self.sim_model_state = self.sim_model.reset(event.episode_start.config)
        elif event.type == 'EpisodeStep':
            action = event.episode_step.action
            self.sim_model_state = self.sim_model.step(action)
        elif event.type == 'EpisodeFinish':
            self.sim_model_state = {}
        elif event.type == 'Unregister':
            print(
                "Simulator Session unregistered by platform because of ",
                event.unregister.details,
            )
        print(time.strftime('%H:%M:%S'), event.type, self.sim_model_state)

    def event_loop(self):
        try:
            while True:
                self.next_event()
        except Exception:
            print('Error in the event loop')
            traceback.print_exc()
        finally:
            print('Deregistering simulator...')
            self.close_session()

    def close_session(self):
        self.client.session.delete(
            workspace_name=self.workspace,
            session_id=self.registered_session.session_id,
        )


def run_interface(verbose):
    bonsai_conn = BonsaiConnector(SimulatorModel, verbose=verbose)
    bonsai_conn.event_loop()


def main():
    args = parser.parse_args()
    if args.policy:
        evaluate_policy(args.episodes, args.policy, host=args.host, port=args.port)
    elif args.generate_chart:
        generate_chart(args.host, args.port)
    else:
        run_interface(args.verbose)


if __name__ == '__main__':
    main()
