# Call with ability(caller: Pokemon, player: Player, opponent: Player)
Action = 'action'       # an action that can be taken
Attacked = 'damaged'    # when damaged
OpponentTurn = 'opp turn'   # once at the start of the opponent's turn
PlayerTurn = 'player turn'  # once at the start of the player's turn

# Call with ability(caller: Pokemon, player: Player, opponent: Player)
# returns int defense to add to defense against attacks
Defend = 'defend'       # adds defense when attacked

# Call with ability(caller: Pokemon, player: Player, opponent: Player)
# returns int or None (new retreat cost or no change)
Retreat = 'retreat'     # alters retreat cost

# Call with ability(caller: Pokemon, player: Player, opponent: Player)
# multi check must return true before multi action can be taken
MultiAction = 'multi action'    # an action that can be taken more than once
MultiCheck = 'multi check'      # required for multiaction, checks if want to use

# Call with ability(energy_attached: str, caller: Pokemon, player: Player, opponent: Player)
EnergyGiven = 'energy given'    # effect on energy from energy zone given
EnergyAttached = 'energy attached'  # effect when energy attached to pokemon in any way