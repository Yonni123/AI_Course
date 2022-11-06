# identify if there is one or more pairs in the hand

# Rank: {2, 3, 4, 5, 6, 7, 8, 9, T, J, Q, K, A}
# Suit: {s, h, d, c}

import random

# 2 example poker hands
CurrentHand1 = ['9d', 'Ac', '9d']
CurrentHand2 = ['Jc', 'Ah', '4s']
ROUND = 0
agent1_winnings = 0
agent2_winnings = 0


# Randomly generate two hands of n cards
def generate_2hands(nn_card=3):
    possible_card_suits = ['s', 'h', 'd', 'c']  # spade, heart, diamond, club
    possible_card_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K',
                           'A']  # 2-10, Jack, Queen, King, Ace
    possible_cards = [r + s for r in possible_card_ranks for s in possible_card_suits] # all possible cards

    # generate one hand of n*2 cards using sample without replacement
    hands = random.sample(possible_cards, nn_card * 2)

    # split the hand into two hands
    hand1 = hands[:nn_card]
    hand2 = hands[nn_card:]

    return hand1, hand2


# return the value of the card (2-10, 11, 12, 13, 14)
def get_value(rank):
    if rank == 'A':
        return 14
    elif rank == 'K':
        return 13
    elif rank == 'Q':
        return 12
    elif rank == 'J':
        return 11
    elif rank == 'T':
        return 10
    else:
        return int(rank)


# identify hand category using IF-THEN rule
def identifyHand(hand):
    values = [get_value(card[0]) for card in hand]
    suits = [card[1] for card in hand]

    # check for three of a kind
    if values[0] == values[1] and values[1] == values[2]:
        return "three of a kind", values[0]

    # check for two pairs
    elif values[0] == values[1]:
        return "two pairs", values[0]
    elif values[1] == values[2]:
        return "two pairs", values[1]
    elif values[0] == values[2]:
        return "two pairs", values[2]

    # check for high cards
    else:
        return "high card", max(values)


# Print out the result
def analyseHands(hand1, hand2):
    hand1_type, hand1_value = identifyHand(hand1)
    hand2_type, hand2_value = identifyHand(hand2)

    if hand1_type == hand2_type:    # if both hands are three of a kind
        if hand1_value > hand2_value:
            return 1
        elif hand1_value < hand2_value:
            return 2
        else:
            return 0

    elif hand1_type == "three of a kind":   # if one of them is three of a kind
        return 1
    elif hand2_type == "three of a kind":
        return 2

    elif hand1_type == "two pairs":    # if one of them is two pairs
        return 1
    elif hand2_type == "two pairs":
        return 2
    else:
        return 0


def random_agent(value_other, self_hand):
    global ROUND
    # return a random value between 0 and 50 with 5 step increment
    return random.randrange(0, 50, 5)


# always returns 0, 25 or 50 in round 1, 2 and 3 respectively
def fixed_agent(value_other, self_hand):
    global ROUND
    return ROUND * 25


def reflex_agent(value_other, self_hand):
    global ROUND
    return 0


def memory_agent(value_other, self_hand):
    global ROUND
    return 0


#########################
#      Game flow        #
#########################


#########################
# phase 1: Card Dealing #
#########################

# generate two hands of 3 cards
CurrentHand1, CurrentHand2 = generate_2hands(3)

#########################
# phase 2:   Bidding    #
#########################

# CHOOSE BETWEEN random_agent, fixed_agent, reflex_agent, memory_agent
AGENT_1 = random_agent
AGENT_2 = fixed_agent

agent1_bid = [0, 0, 0]
agent2_bid = [0, 0, 0]

for i in range(3):
    ROUND = i
    if i == 0:
        agent1_bid[i] = AGENT_1(-1, CurrentHand1)
        agent2_bid[i] = AGENT_2(-1, CurrentHand2)
    else:
        agent1_bid[i] = AGENT_1(agent2_bid[i - 1], CurrentHand1)
        agent2_bid[i] = AGENT_2(agent1_bid[i - 1], CurrentHand2)

#########################
# phase 2:   Showdown   #
#########################

winner = analyseHands(CurrentHand1, CurrentHand2)
if winner == 0:
    print("Draw")
elif winner == 1:
    print("Agent 1 wins")
    agent1_winnings = sum(agent1_bid) + sum(agent2_bid)
elif winner == 2:
    print("Agent 2 wins")
    agent2_winnings = sum(agent1_bid) + sum(agent2_bid)

print("Agent 1 winnings: ", agent1_winnings)
print("Agent 2 winnings: ", agent2_winnings)

print("Agent 1 hand: ", CurrentHand1)
print("Agent 2 hand: ", CurrentHand2)

print("Agent 1 bids: ", agent1_bid)
print("Agent 2 bids: ", agent2_bid)