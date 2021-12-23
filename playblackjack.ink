# Inkling for teaching a brain to play blackjack
inkling "2.0"

# State provided by the simulator
type SimState {
    # Value of player's hand.
    player: number,
    # Value of dealer's hand.
    dealer: number,
    # The final result of the game
    result: number,
}

# Remove result from state as it is useless for the brain
type ObservableState {
    # Value of player's hand.
    player: number,
    # Value of dealer's hand.
    dealer: number,
}

using Math
using Goal


# 0 -> Stay, 1 -> Hit
type SimAction {
    # Whether to hit (1) or stay (0).
    command: number<0 .. 1 step 1>,
}

simulator Simulator(action: SimAction): SimState {
    package "Blackjack"
}

# Winning gives reward 1, Losing -100 and draw 0
function Reward(obs: SimState) {
    if (obs.result == 2) {
        return 1
    }
    else if (obs.result == 0) {
        return -100
    }
    return 0
}

# Terminate when game ends
function Terminal(obs: SimState) {
    if (obs.result < 0) {
        return false
    }
    return true
}

graph (input: ObservableState): SimAction {
    concept PlayBlackjack(input): SimAction {
        curriculum {
            source Simulator
            reward Reward
            terminal Terminal
        }
    }
}
