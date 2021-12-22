# Inkling for teaching a brain to play blackjack
inkling "2.0"

# State provided by the simulator
type SimState {
    # Value of player's hand.
    player: number,
    # Value of dealer's hand.
    dealer: number,
    # 1 for player's win, 0 otherwise
    won: number,
    # 1 for dealer's win, 0 otherwise
    lost: number,
    # 1 for draw, 0 otherwise
    draw: number,
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
    if (obs.won == 1) {
        return 1
    }
    else if (obs.lost == 1) {
        return -100
    }
    return 0
}

# Terminate when game ends
function Terminal(obs: SimState) {
    if (obs.won == 1 or obs.lost == 1 or obs.draw == 1) {
        return true
    }
    return false
}

graph (input: SimState): SimAction {
    concept PlayBlackjack(input): SimAction {
        curriculum {
            source Simulator
            reward Reward
            terminal Terminal
        }
    }
}
