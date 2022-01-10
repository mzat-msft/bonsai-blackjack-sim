# Inkling for teaching a brain to play blackjack
inkling "2.0"

# State provided by the simulator
type SimState {
    # Value of player's hand.
    player: number,
    # Value of dealer's hand.
    dealer: number,
    # The final result of the game.
    result: number,
    # Whether player doubled.
    double: number <0, 1,>,
    # Whether player has aces.
    player_ace: number <0, 1,>,
    # Whether dealer has aces.
    dealer_ace: number <0, 1,>,
}

# Remove result from state as it is useless for the brain
type ObservableState {
    # Value of player's hand.
    player: number,
    # Value of dealer's hand.
    dealer: number,
    # Whether player has aces.
    player_ace: number <0, 1,>,
    # Whether dealer has aces.
    dealer_ace: number <0, 1,>,
}

using Math
using Goal


# 0 -> Stay, 1 -> Hit, 2 -> Double
type SimAction {
    # Whether to stay (0), hit (1) or double-down (2).
    command: number<0 .. 2 step 1>,
}

simulator Simulator(action: SimAction): SimState {
    package "Blackjack"
}

function Reward(obs: SimState) {
    # Win
    if (obs.result == 2) {
        if (obs.double == 1) {
            return 2
        }
        else {
            return 1
        }
    }
    # Lose
    else if (obs.result == 0) {
        if (obs.double == 1) {
            return -200
        }
        else {
            return -100
        }
    }
    # Draw
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
