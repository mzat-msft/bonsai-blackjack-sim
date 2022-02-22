# Inkling for teaching a brain to play blackjack
# WARNING: The brain does not learn to play blackjack.
#          It just outputs STAY at every step.
inkling "2.0"

# State provided by the simulator
type SimState {
    # Value of player's hand.
    player: number,
    # Value of dealer's hand.
    dealer: number,
    # The final result of the game.
    result: number<Play = -1, Lost = 0, Draw = 1, Won = 2>,
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
    # Whether dealer has aces.
    player_ace: number <0, 1,>,
    # Whether dealer has aces.
    dealer_ace: number <0, 1,>,
}

using Math
using Goal


# 0 -> Stay, 1 -> Hit, 2 -> Double
type SimAction {
    # The available actions for the agent.
    command: number<Stay = 0, Hit = 1, `Double-down` = 2>,
}

simulator Simulator(action: SimAction): SimState {
}

graph (input: ObservableState): SimAction {
    concept PlayBlackjack(input): SimAction {
        curriculum {
            source Simulator
            goal (SimState: SimState) {
                avoid Bust:
                    SimState.player in Goal.RangeAbove(22)
                maximize Blackjack:
                    SimState.player in Goal.RangeAbove(SimState.dealer)
                reach End:
                    SimState.result in Goal.RangeAbove(0)
                avoid Lose:
                    SimState.result in Goal.Range(0.99, 1.01)
                maximize DealerBust:
                    SimState.dealer in Goal.RangeAbove(22)
            }
        }
    }
}
