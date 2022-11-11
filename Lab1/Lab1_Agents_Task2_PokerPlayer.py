# identify if there is one or more pairs in the hand

# Rank: {2, 3, 4, 5, 6, 7, 8, 9, T, J, Q, K, A}
# Suit: {s, h, d, c}

import random

import numpy as np

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
    possible_cards = [r + s for r in possible_card_ranks for s in possible_card_suits]  # all possible cards

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


def get_hand_strength(hand):
    type, value = identifyHand(hand)
    if type == "three of a kind":
        return int(25 + (value / 14) * 25)  # return 25 or 50 depending on the value of the three of a kind
    elif type == "two pairs":
        return int(5 + (value / 14) * 25)  # return 5 or 30 depending on the value of the two pairs
    else:
        return value  # return the value of the high card


# Print out the result
def analyseHands(hand1, hand2):
    hand1_type, hand1_value = identifyHand(hand1)
    hand2_type, hand2_value = identifyHand(hand2)

    if hand1_type == hand2_type:  # if both hands are the same type, compare the value
        if hand1_value > hand2_value:
            return 1
        elif hand1_value < hand2_value:
            return 2
        else:
            return 0

    elif hand1_type == "three of a kind":  # if one of them is three of a kind
        return 1
    elif hand2_type == "three of a kind":
        return 2

    elif hand1_type == "two pairs":  # if one of them is two pairs
        return 1
    elif hand2_type == "two pairs":
        return 2
    else:
        return 0


def random_agent(value_other, self_hand):
    global ROUND
    # return a random value between 0 and 50
    return random.randint(0, 50)


def fixed_agent(value_other, self_hand):
    global ROUND
    # always returns 0, 25 or 50 in round 1, 2 and 3 respectively
    return ROUND * 25


def reflex_agent(value_other, self_hand):
    global ROUND
    return get_hand_strength(self_hand)


# Figure out which agent we are playing against based on old bets and hands
def get_enemy_agent(bets, hands):
    if bets[0] == bets[1] and bets[1] == bets[2]:  # If all bets are the same, then the agent is fixed
        return "fixed"
    else:
        hands_strength = [0, 0, 0, 0, 0]
        for i in range(5):
            type, value = identifyHand(hands[i])
            if type == "three of a kind":
                hands_strength[i] = int(25 + (value / 14) * 25)
            elif type == "two pairs":
                hands_strength[i] = int(5 + (value / 14) * 25)
            else:
                hands_strength[i] = value

        # plot old bets against hands strength
        average_bets = [(bets[0][0] + bets[0][1] + bets[0][2]) / 3,
                        (bets[1][0] + bets[1][1] + bets[1][2]) / 3,
                        (bets[2][0] + bets[2][1] + bets[2][2]) / 3,
                        (bets[3][0] + bets[3][1] + bets[3][2]) / 3,
                        (bets[4][0] + bets[4][1] + bets[4][2]) / 3]

        # fit a line to the data
        z = np.polyfit(hands_strength, average_bets, 1)
        p = np.poly1d(z)

        # Get the sum of squared residuals
        ssr = np.sum((p(hands_strength) - average_bets) ** 2)

        # If the sum of squared residuals is less than 0.1, we are playing against a reflex agent
        if ssr < 0.1:
            return "reflex"
        else:
            return "random"


old_bets = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
old_hands = [[], [], [], [], []]
current_round = -1
enemy_agent = ""


def memory_agent(value_other, self_hand):
    global ROUND, current_round, old_bets, enemy_agent

    # Return random values for the first five rounds
    if current_round < 5:
        return random.randrange(0, 50, 1)  # return a random value in the first 3 rounds

    # Figure out which agent we are playing against based on old bets
    if current_round == 5 and enemy_agent == "":
        enemy_agent = get_enemy_agent(old_bets, old_hands)
        print("Enemy agent is: " + enemy_agent)

    # Against a fixed agent or random agent, there is no better strategy than betting according to the hand strength
    if enemy_agent == "random" or enemy_agent == "fixed":
        return reflex_agent(value_other, self_hand)

    # If we are playing against a fixed agent, return 25
    elif enemy_agent == "reflex":
        self_strength = get_hand_strength(self_hand)
        if self_strength > value_other:
            return 50
        else:
            return 0
    else:
        return random.randrange(0, 50, 1)


#########################
#      Game flow        #
#########################

# CHOOSE BETWEEN random_agent, fixed_agent, reflex_agent, memory_agent
# DON'T CHOOSE TWO MEMORY AGENTS, they will share variables and cause errors
AGENT_1 = memory_agent
AGENT_2 = random_agent

TOTAL_EARNINGS = [0] * 100  # store the total earnings of each game
for k in range(100):  # play 100 games
    print("Game", k)
    for j in range(50):  # play 50 rounds in each game
        current_round += 1
        #########################
        # phase 1: Card Dealing #
        #########################

        # generate two hands of 3 cards
        CurrentHand1, CurrentHand2 = generate_2hands(3)

        #########################
        # phase 2:   Bidding    #
        #########################

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

        if AGENT_1 == memory_agent and j < 5:  # store the old bets and hands for the first 5 rounds
            old_bets[j] = agent2_bid  # so that we can figure out which agent we are playing against
            old_hands[j] = CurrentHand2
        elif AGENT_2 == memory_agent and j < 5:
            old_bets[j] = agent1_bid
            old_hands[j] = CurrentHand1

        #########################
        # phase 2:   Showdown   #
        #########################

        winner = analyseHands(CurrentHand1, CurrentHand2)
        if winner == 0:
            print("Draw")
        elif winner == 1:
            print("Agent 1 wins")
            agent1_winnings += sum(agent1_bid) + sum(agent2_bid)
        elif winner == 2:
            print("Agent 2 wins")
            agent2_winnings += sum(agent1_bid) + sum(agent2_bid)

        print("Agent 1 winnings: ", agent1_winnings, "Agent 1 hand: ", CurrentHand1, "Agent 1 bids: ", agent1_bid)
        print("Agent 2 winnings: ", agent2_winnings, "Agent 2 hand: ", CurrentHand2, "Agent 2 bids: ", agent2_bid)
        TOTAL_EARNINGS[k] = agent1_winnings - agent2_winnings
        agent1_winnings = 0
        agent2_winnings = 0

print("Total earnings: ", TOTAL_EARNINGS)
# Calulate the mean and standard deviation of the total earnings
print("Earnings = ", np.mean(TOTAL_EARNINGS), "+/-", np.std(TOTAL_EARNINGS))
if enemy_agent != "":
    print("Enemy agent is: " + enemy_agent)
