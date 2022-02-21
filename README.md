# Blackjack simulation

This repository implements a simulation of the card game Blackjack that can
be used with the Bonsai platform.

## Run it locally

In order to run the simulation locally you must install the dependencies in
`requirements.txt` and then run

```bash
python main.py
```

Please remember to set in your shell environment the variables
`SIM_WORKSPACE` and `SIM_ACCESS_KEY`.

## Evaluate predefined policies

It is possible to evaluate how well some predefined policies behave with the
simulation with the following command

```bash
python main.py -p policy_name -e number_of_episodes
```

Currently the following policies are implemented:

- `random`: at each step, choose randomly between *stay*, *hit* or
  *double-down*
- `random_conservative`: restrict random policy to choose only *stay* or *hit*
- `player`: the program spins up an interactive session where a human player
  can try their luck by playing blackjack
- `basic`: use some commonly known strategy to choose the best action
  for a given game configuration
- `brain`: evaluate a deployed brain trained with Bonsai

These policies have been evaluated on a total of 100'000 episodes and the
mean reward obtained reported in the table below. In addition, we report the
mean reward of two brains trained using Bonsai evaluated on ~100'000 episodes.
One brain is trained with an inkling defining a custom reward function, and the
other defining concepts with goals.

| Policy                       | Mean Reward |
| ---------------------------- | -----------:|
| Random                       | -0.565      |
| Random conservative          | -0.390      |
| Basic strategy               | -0.059      |
| Bonsai brain - reward        | -0.057      |
| Bonsai brain - goal          | -0.190      |
