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


## Strategy Chart

Once we train a brain with Bonsai, we can generate a strategy chart which shows
us the different moves that the brain suggests for a particular game
configuration.
Rows in the following table represents the value of the player's hand, while
columns represent the dealer's hand.

### Hard totals
|       |       2       |       3       |       4       |       5       |       6       |       7       |       8       |       9       |       10      |       11      |
|---    |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |
| **17**        |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |
| **16**        |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |
| **15**        |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       H       |
| **14**        |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       H       |
| **13**        |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       H       |       H       |       H       |
| **12**        |       D       |       S       |       S       |       S       |       S       |       S       |       H       |       H       |       H       |       H       |
| **11**        |       D       |       S       |       D       |       D       |       D       |       D       |       D       |       D       |       H       |       H       |
| **10**        |       D       |       D       |       D       |       D       |       D       |       D       |       D       |       H       |       H       |       H       |
| **9** |       D       |       D       |       D       |       D       |       S       |       D       |       H       |       H       |       H       |       H       |
| **8** |       S       |       S       |       S       |       S       |       S       |       H       |       H       |       H       |       H       |       H       |

### Soft totals
|       |       2       |       3       |       4       |       5       |       6       |       7       |       8       |       9       |       10      |       11      |
|---    |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |       ---     |
| **A, 9**      |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |
| **A, 8**      |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |
| **A, 7**      |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |       S       |
| **A, 6**      |       S       |       S       |       S       |       S       |       D       |       S       |       S       |       H       |       S       |       H       |
| **A, 5**      |       S       |       S       |       S       |       D       |       D       |       D       |       H       |       S       |       H       |       H       |
| **A, 4**      |       S       |       S       |       S       |       D       |       D       |       H       |       S       |       H       |       H       |       H       |
| **A, 3**      |       S       |       S       |       S       |       D       |       D       |       H       |       H       |       H       |       H       |       H       |
| **A, 2**      |       S       |       S       |       D       |       D       |       S       |       H       |       H       |       H       |       H       |       H       |
