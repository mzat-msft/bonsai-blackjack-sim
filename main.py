"""Main connector to the Bonsai platform."""

import json
import os
import time

from microsoft_bonsai_api.simulator.client import (BonsaiClient,
                                                   BonsaiClientConfig)
from microsoft_bonsai_api.simulator.generated.models import (
    SimulatorInterface, SimulatorState)

from blackjack.blackjack import SimulatorModel


def get_env_or_fail(key):
    val = os.getenv(key, None)
    if val is None:
        raise ValueError(f'You must provide {key} as env variable.')


def main():
    workspace = get_env_or_fail('SIM_WORKSPACE')
    access_key = get_env_or_fail('SIM_ACCESS_KEY')
    client_config = BonsaiClientConfig()
    client = BonsaiClient(client_config)

    with open('blackjack-interface.json', 'r') as fp:
        interface = json.load(fp)
    reg_info = SimulatorInterface(
        simulator_context=client_config.simulator_context,
        **interface,
    )
    registered_session = client.session.create(
        workspace_name=client_config.workspace,
        body=reg_info,
    )

    sequence_id = 1

    sim_model = SimulatorModel()
    sim_model_state = {'halted': False}

    try:
        while True:
            sim_state = SimulatorState(
                sequence_id=sequence_id,
                state=sim_model_state,
                halted=sim_model_state.get('halted', False),
            )
            event = client.session.advance(
                workspace_name=client_config.workspace,
                session_id=registered_session.session_id,
                body=sim_state,
            )
            sequence_id = event.sequence_id
            if event.type == 'Idle':
                time.sleep(event.idle.callback_time)
            elif event.type == 'EpisodeStart':
                sim_model_state = sim_model.reset()
            elif event.type == 'EpisodeStep':
                sim_model_state = sim_model.step(
                    event.episode_step.action['command']
                )
            elif event.type == 'EpisodeFinish':
                sim_model_state = {'sim_halted': False}
            elif event.type == 'Unregister':
                print(
                    "Simulator Session unregistered by platform because of ",
                    event.unregister.details,
                )
            print(time.strftime('%H:%M:%S'), event.type, sim_model_state)

    except Exception as e:
        client.session.delete(
            workspace_name=client_config.workspace,
            session_id=registered_session.session_id,
        )
        raise RuntimeError('Error in event loop') from e


if __name__ == '__main__':
    main()
