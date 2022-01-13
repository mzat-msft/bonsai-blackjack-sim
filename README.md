# Blackjack simulation

This repository implements a simulation of the card game Blackjack that can
be used with the Bonsai platform.

## Run it locally

In order to run the simulation locally you must install the dependencies in
`requirements.txt` and then

```bash
python main.py
```

Please remember to set in your shell environment the variables
`SIM_WORKSPACE` and `SIM_ACCESS_KEY`.

## Evaluate predefined policies

It is possible to evaluate how well some predefined policies behave with the
simulation. Currently the following policies are implemented:

- Random: at each step, choose randomly between *stay*, *hit* or
  *double-down*
- Random conservative: restrict random policy to choose only *stay* or *hit*
- Player: the program spins up an interactive session where a human player
  can try their luck by playing blackjack
- Basic strategy: use some commonly known strategy to choose the best action
  to use for a given game configuration

These policies have been evaluated on a total of 100'000 games and the mean
reward for each of them is reported in the table below. In addition, we
report the mean reward of a brain trained using Bonsai evaluated on 5'700
episodes.

| Policy              | Mean Reward |
| ------------------- | -----------:|
| Random              | -0.565      |
| Random conservative | -0.390      |
| Basic strategy      | -0.053      |
| Bonsai brain        | -0.060      |
