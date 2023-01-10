"""Main connector to the Bonsai platform."""
import argparse
import time

from bonsai_connector import BonsaiConnector

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


def clean_state(state):
    allowed_types = (bool, dict, float, int, list)
    return {key: val for key, val in state.items() if isinstance(val, allowed_types)}


def run_interface(verbose):
    sim = SimulatorModel()

    with BonsaiConnector(sim.interface, verbose=verbose) as agent:
        state = None
        while True:
            if state is None:
                state = {'halted': False}
            event = agent.next_event(clean_state(state))
            state = sim.dispatch_event(event)
            print(time.strftime('%H:%M:%S'), event.event_type, state)


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
