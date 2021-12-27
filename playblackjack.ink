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


# 0 -> Stay, 1 -> Hit, 2 -> Double
type SimAction {
    # Whether to stay (0), hit (1) or double-down (2).
    command: number<0 .. 2 step 1>,
}

simulator Simulator(action: SimAction): SimState {
    package "Blackjack"
}

function Reward(obs: SimState) {
    # Normal win
    if (obs.result == 2) {
        return 1
    }
    # Win after double
    else if (obs.result == 3) {
	return 2
    }
    # Lose
    else if (obs.result == 0) {
        return -100
    }
    # Lose after double
    else if (obs.result == 4) {
        return -200
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
