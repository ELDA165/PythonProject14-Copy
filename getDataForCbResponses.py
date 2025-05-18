from localChatbot import Chatbot
from constant import Constant


class DataForCbResponses():
    def calculations(key, player, answerOpt):
        if key == "suggestion":
            calculationValues = DataForCbResponses.__getSuggestionValues(player)
        elif key == "explain":
            calculationValues = DataForCbResponses.__getExplainValues(player)
        elif key == "explainGeneral":
            calculationValues = DataForCbResponses.__getExplainGeneralValues(player)
        elif key == "userEstimate":
            calculationValues = DataForCbResponses.__getUserEstimateValues(player, answerOpt)

        elif key == "deviate":
            calculationValues = DataForCbResponses.__getDeviateValues(player, answerOpt)

        return calculationValues

    """
    Method to collect data for keyword "suggestion"
    """

    def __getSuggestionValues(player):
        calculationValues = []
        # 0: player.suggestedOptimum

        calculationValues.append(player.suggestedOptimum)
        return calculationValues

    """
    Method to collect data for keyword "Explain"
    """

    def __getExplainValues(player):
        calculationValues = []
        role = player.getId()
        # retailer: & #factory:
        # 0: leadtime
        calculationValues.append(player.leadTime())

        # 1: order xt-3 (only retailer)
        # 2: order xt-2
        # 3: oerder xt-1
        calculationValues.extend(
            DataForCbResponses.getPastOrders(player, player.leadTime(), player.round_number - 1, []))

        # 4: inventory
        inventory = player.inventory
        calculationValues.append(inventory)
        # 5: opt
        calculationValues.append(player.suggestedOptimum)

        # 5: avergage demand (factory)
        if role == 2:
            calculationValues.append(DataForCbResponses.averageDemand(player))

        # 6: targetlevel
        if player.round_number == 1:
            targetInventory = player.initTargetInventory()
        else:
            targetInventory = player.targetInventory
        calculationValues.append(targetInventory)
        # 7: sum of past orders, and inventory
        pastDemand = DataForCbResponses.getPastIncomingDemand(player, player.leadTime(), player.round_number - 1, [])

        val = sum(pastDemand) + inventory
        calculationValues.append(val)

        # 8: targeltevel - #7
        val2 = targetInventory - val
        calculationValues.append(val2)

        return calculationValues

    """
    Method to collect data for keyword "explainGeneral"
    """

    def __getExplainGeneralValues(player):
        calculationValues = []

        # retailer & factory
        # 0,1,2: round number
        calculationValues.extend(DataForCbResponses.getLastThreeRoundNumbers(player))

        # 3,4,5: past demand
        calculationValues.extend(
            DataForCbResponses.getPastIncomingDemand(player, player.leadTime(), player.round_number - 1, []))
        # 6 average past demand
        calculationValues.append(DataForCbResponses.averageDemand(player))
        # retailer:
        # 7: order xt-3
        # 8: order xt-2
        # 9: oerder xt-1
        # factory only 2
        calculationValues.extend(
            DataForCbResponses.getPastOrders(player, player.leadTime(), player.round_number - 1, []))

        # 10: inventory (factory:9)
        calculationValues.append(player.inventory)
        return calculationValues

    """
    Method to collect data for keyword "userEstimate"
    """

    def __getUserEstimateValues(player, answerOpt):
        calculationValues = []
        usersSuggestion = answerOpt.userSuggestion
        opt = player.suggestedOptimum
        role = player.getId()

        if usersSuggestion == opt:
            pass
        else:
            # retailer & factory:
            # 0,1,2 round no
            calculationValues.extend(DataForCbResponses.getLastThreeRoundNumbers(player))
            # 3,4,5 past demand
            calculationValues.extend(
                DataForCbResponses.getPastIncomingDemand(player, player.leadTime(), player.round_number - 1, []))

            # 6 usersuggestion
            calculationValues.append(usersSuggestion)
            # 7 leadtime
            calculationValues.append(player.leadTime())

            if usersSuggestion > opt:
                # more
                if role == 1:
                    # retailer:
                    # 8 user suggestion - constant demand
                    calculationValues.append((usersSuggestion - Constant.CONSTANT_CUSTOMER_DEMAND))
                    # retailer
                    # 9 costsforInventory*(user suggestion - constant demand)
                    costInv = Constant.INVENTORY_COST_PER_UNIT * (usersSuggestion - Constant.CONSTANT_CUSTOMER_DEMAND)
                    calculationValues.append(costInv)

                else:
                    # factory:
                    # 8 user suggestion - avg(demand)
                    overestimation = usersSuggestion - DataForCbResponses.averageDemand(player)
                    calculationValues.append(overestimation)
                    # factory:
                    # 9 costs for inventory*(usersuggestion - avg(demand))
                    costInv = Constant.INVENTORY_COST_PER_UNIT * overestimation
                    calculationValues.append(costInv)

            elif usersSuggestion < opt:
                # less
                if role == 1:
                    # retailer:
                    # 8 (user suggestion *100)/constant demand
                    calculationValues.append((usersSuggestion * 100) / Constant.CONSTANT_CUSTOMER_DEMAND)
                    # retailer
                    # 9 constant demand - user suggestion)
                    backorder = (Constant.CONSTANT_CUSTOMER_DEMAND - usersSuggestion)
                    calculationValues.append(backorder)
                    # retailer
                    # 10 costsBackorders*(constant demand - user suggestion))
                    calculationValues.append((Constant.BACKORDER_PENALTY_COST_PER_UNIT * backorder))
                else:
                    # factory:
                    # 8 (user suggestion*100/ avg(demand)
                    avgDeman = DataForCbResponses.averageDemand(player)
                    calculationValues.append((usersSuggestion * 100) / avgDeman)
                    # factory:
                    # 9 avg(demand) - usersuggestion
                    backorder = avgDeman - usersSuggestion
                    calculationValues.append(backorder)
                    # factory
                    # 10 costsBackorders*(avg(demand) - usersuggestion )
                    calculationValues.append(Constant.BACKORDER_PENALTY_COST_PER_UNIT * backorder)
        return calculationValues

    """
    Method to collect data for keyword "deviate"
    """

    def __getDeviateValues(player, answerOpt):
        calculationValues = []
        usersSuggestion = answerOpt.userSuggestion
        opt = player.suggestedOptimum
        role = player.getId()

        if usersSuggestion == opt:
            calculationValues.append(opt)

        else:
            # (0) usersuggestion
            calculationValues.append(usersSuggestion)
            # (1) leadtime
            calculationValues.append(player.leadTime())

            if usersSuggestion > opt:
                if role == 2:
                    # factory
                    # 2: avg demand
                    avgDeman = DataForCbResponses.averageDemand(player)
                    calculationValues.append(avgDeman)
                    # 3 inventory: num - avg(dem)
                    inv = usersSuggestion - avgDeman
                else:
                    # (2r) (3f) inventory new (too much): suggestion - opt
                    inv = usersSuggestion - opt
                calculationValues.append(inv)
                # (3r) (4f) inv Costs: const. Inv * inv
                calculationValues.append(Constant.INVENTORY_COST_PER_UNIT * inv)
            else:
                if role == 2:
                    # factory
                    # 2 avg demand
                    avgDeman = avgDeman(player)
                    calculationValues.append(avgDeman)
                    # 3 backorders: avg dem  num
                    backorder = avgDeman - usersSuggestion
                else:
                    # (2) constant demand
                    calculationValues.append(Constant.CONSTANT_CUSTOMER_DEMAND)
                    # (3) backorders: opt - num
                    backorder = opt - usersSuggestion

                calculationValues.append(backorder)
                # (4) backorder costs : costs * backorders
                calculationValues.append(Constant.BACKORDER_PENALTY_COST_PER_UNIT * backorder)
        return calculationValues

    """
    Method to get the past orders. returns a list.
    """

    def getPastOrders(player, leadtime, till, pastOrders: list):
        return DataForCbResponses.recursiveDateExtraction(player, leadtime, till, pastOrders,
                                                          Constant.CONSTANT_CUSTOMER_DEMAND, "O")

    """
    Method to get the past demands. returns a list.
    """

    def getPastIncomingDemand(player, leadtime, till, pastDemand: list):
        return DataForCbResponses.recursiveDateExtraction(player, leadtime, till, pastDemand,
                                                          Constant.INITIAL_INCOMING_DEMAND, "D")

    """ 
    Method to get all past values between till and leadtime. 
    Either the orders or the demands are extracted. 
    This function recursively iterates and returns a list.
    """

    def recursiveDateExtraction(player, leadtime, till, list, constant, orderOrDemand):
        if till == (0 - leadtime + 1):
            return list
        if till <= 0:
            value = constant
        else:
            if orderOrDemand == "O":
                value = player.in_round(
                    till).order_t  # TODO: here is something wrong - round 0: data of round -3 == 0 not 4.
            else:
                value = player.in_round(till).incomingDemand
        list.append(value)
        return DataForCbResponses.recursiveDateExtraction(player, leadtime, till - 1, list, constant, orderOrDemand)

    def averageDemand(player):
        val = 0
        for i in range(1, player.round_number):
            val += player.in_round(i).incomingDemand

        return val / player.round_number

    def getLastThreeRoundNumbers(player):
        rounds = []
        for i in range((player.round_number - 4), player.round_number):
            rounds.append(i)
        return rounds



