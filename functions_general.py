from otree.api import *
from constant import *


########################### Generalised Functions ###########################

class InitFunctions_General():
    # initalise data
    def getDataForFirstRound(p, automatedFactory: bool):
        if automatedFactory:
            p.factory_inventory = Constant.INITIAL_INVENTORY
            p.factory_backlog_demand_cumulated = Constant.INITIAL_BACKLOG_DEMANDS
            p.factory_fulfilledDemand = Constant.INITIAL_FULFILLED_DEMAND
            p.factory_totalCostsBackorders = Constant.INITIAL_COST_BACKORDERS
            p.factory_totalCostsInventory = Constant.INITIAL_COST_INVENTORY
            p.factory_turnover = Constant.INITIAL_TURNOVER

        p.inventory = Constant.INITIAL_INVENTORY
        p.backlog_demand_cumulated = Constant.INITIAL_BACKLOG_DEMANDS
        p.fulfilledDemand = Constant.INITIAL_FULFILLED_DEMAND
        p.totalCostsBackorders = Constant.INITIAL_COST_BACKORDERS
        p.totalCostsInventory = Constant.INITIAL_COST_INVENTORY
        p.turnover = Constant.INITIAL_TURNOVER

    def getDataFromPreviousRound(p, automatedFactory: bool):
        previousP = p.in_round(p.round_number - 1)
        if automatedFactory:
            p.factory_inventory = previousP.factory_inventory
            p.factory_backlog_demand_cumulated = previousP.factory_backlog_demand_cumulated
            p.factory_fulfilledDemand = previousP.factory_fulfilledDemand
            p.factory_totalCostsBackorders = previousP.factory_totalCostsBackorders
            p.factory_totalCostsInventory = previousP.factory_totalCostsInventory
            p.factory_turnover = previousP.factory_turnover

        p.inventory = previousP.inventory
        p.backlog_demand_cumulated = previousP.backlog_demand_cumulated
        p.fulfilledDemand = previousP.fulfilledDemand
        p.totalCostsBackorders = previousP.totalCostsBackorders
        p.totalCostsInventory = previousP.totalCostsInventory
        p.turnover = previousP.turnover


# Process:
"""
(i) shipments from the upstream decision maker are received and placed in inventory, 
(ii) incoming orders are received from the downstream decision maker and either filled (if inventory is available) or placed in backorder, and 
(iii) a new order is placed and passed to the upstream player. 
"""


class Shipment_General():
    # get shipment and add to inventory.
    # only works if leadtime not zero
    def getDeliveryFromFactory(p1, p2, automatedFactory: bool, leadtimeDelivery):
        t = p1.round_number - leadtimeDelivery
        if t <= 0:
            return Constant.INITIAL_OUTGOING_DELIVERY

        if automatedFactory:
            return p1.in_round(t).factory_outgoingDelivery
        else:
            return p2.in_round(t).outgoingDelivery

    def getDeliveryFromProduction(p, automatedFactory, leadTimeProduction):
        t = p.round_number - leadTimeProduction
        if t <= 0:
            return Constant.INITIAL_ORDER_T
        if automatedFactory == True:
            return p.in_round(t).factory_order_t
        else:
            return p.in_round(t).order_t

    def addToInventory(p, automatedFactory: bool):
        if automatedFactory:
            p.factory_inventory += p.factory_incomingDelivery
        p.inventory += p.incomingDelivery


class FulfillDemand_General():

    def getDemand(p1, p2, automatedFactory: bool, leadtimeOrder):
        factoryDemand = FulfillDemand_General.getOrderFromRetailer(p1, leadtimeOrder)

        if automatedFactory:
            p1.factory_incomingDemand = factoryDemand
        else:
            p2.incomingDemand = factoryDemand

        p1.incomingDemand = Constant.CONSTANT_CUSTOMER_DEMAND

    def getOrderFromRetailer(p1, leadtimeOrder):
        t = p1.round_number - leadtimeOrder
        if t <= 0:
            return Constant.INITIAL_ORDER_T
        return p1.in_round(t).order_t

    """
    -----------------------------------------------------
    Function to calculate the fulfillment of the demand
    input: Player 
    output: None 
    Prerequisits: Demand has been updated
    -----------------------------------------------------
    If the demand can be fullfilled it is fulfilled. If 
    backorders exist and (parts) can be fulfilled they are. 
    ----------
    Details: 
    If the the incoming demand is less than the inventory, then 
    the system checks if backorders exist. If backorders exist, 
    then these are tried to be fulfilled completely or partially. 
    Thus the backorders are reduced. 
    If no backorders exist than only the demand is fulfilled. 
    If the demand cannot be fulfilled, new backorders are generated. 
    """

    def fulfillDemand(p, automatedFactory: bool, inventory, incomingDemand, backlog_demand_cumulated):
        outgoingDelivery = 0
        # if can fulfill the demand
        if inventory > incomingDemand:
            # if have backorders
            if backlog_demand_cumulated > 0:
                toFulfill = incomingDemand + backlog_demand_cumulated
                amount = inventory - toFulfill
                # if able to fulfill than do that
                if amount >= 0:
                    outgoingDelivery = toFulfill
                    backlog_demand_cumulated = 0
                    # if only partially can fulfill it
                else:
                    outgoingDelivery = inventory
                    backlog_demand_cumulated = backlog_demand_cumulated - (inventory - incomingDemand)
            # if do not have a backlog of orders
            else:
                outgoingDelivery = incomingDemand
                # if cannot fulfill Demand
        elif inventory < incomingDemand:
            outgoingDelivery = inventory
            backlog_demand_cumulated += incomingDemand - inventory

            # p.inventory == p.incoming demand
        else:
            outgoingDelivery = inventory

        if automatedFactory:
            p.factory_backlog_demand_cumulated = backlog_demand_cumulated
            p.factory_outgoingDelivery = outgoingDelivery
            p.factory_inventory -= p.factory_outgoingDelivery
            p.factory_fulfilledDemand += p.factory_outgoingDelivery
        else:
            p.backlog_demand_cumulated = backlog_demand_cumulated
            p.outgoingDelivery = outgoingDelivery
            p.inventory -= p.outgoingDelivery
            p.fulfilledDemand += p.outgoingDelivery

    def getBackorderCosts(totalCostsBackorders, backlog_demand_cumulated):
        return totalCostsBackorders + (backlog_demand_cumulated * Constant.BACKORDER_PENALTY_COST_PER_UNIT)

    def getInventoryCosts(totalCostsInventory, inventory):
        return totalCostsInventory + (inventory * Constant.INVENTORY_COST_PER_UNIT)

    def getTurnover(currentTurnover, outgoingDelivery):
        return currentTurnover + (outgoingDelivery * Constant.TURNOVER_PER_UNIT_DELIVERED)


class Calculations_General():
    """
    Calculation of the supply line pre order of the retailer:
    input: player 1 (retailer), player 2 (factory),
        round number, the leadtime of delivering products from the factory to the retailer,
        leadtime of sending the orders from the retailer to the factory.
    output: supply line pre order retailer
    Prerequisits: None
    -----------------------------------------------------------------------------------------
    The supply line pre order cumulates from all past orders that have been sent to the factory but not fulfilled yet
    plus all the products in route.
    Dependend on the length of the leadtime of delivery all past outgoing deliveries from the factory are
    cumulated till last round. Dependend on the leadtime of the order, all past orders from the retailer are
    cumulated. Both values are summed and returned.
    -----------------------------------------------------------------------------------------
    Exceptions:
    If the roundnumber minus the lead time (e.g. round 3, leadtime= 4 -> 3-4 = -1) is below 0, thus lying in the past
    before the start of the experiment, then the initial values are used, as it is assumed that everything has been
    constant in the past.
    """

    def getSupplyLinePreOrderRetailer(p1, p2, automatedFactory: bool, roundNo, leadtime):
        sl_retailer = 0
        # get all sent products that are on their way from Factory to retailer
        # all product sent (in lead time 2: would be 2 products)
        # for t in range(roundNo-leadtimeDelivery, roundNo): # maybe wrong shift.
        #    if t <= 0:
        #        sl_retailer += Constant.INITIAL_INCOMING_DELIVERY_T
        #    else:
        #        if automatedFactory:
        #            sl_retailer += p1.in_round(t).factory_outgoingDelivery
        #            print(f"get Outgoing deliveries for the retailer (roundNo: {roundNo}) round: {t}; {p1.in_round(t).factory_outgoingDelivery}")
        #        else:
        #            sl_retailer += p2.in_round(t).outgoingDelivery

        # get all orders but not yet arrived at the factory
        # all orders sent - as we did not order yet only 1 order (if leadtime is 2) is on its way.
        for t in range(roundNo - leadtime + 1, roundNo):
            if t <= 0:
                sl_retailer += Constant.INITIAL_ORDER_T
            else:
                sl_retailer += p1.in_round(t).order_t
                print(
                    f"get incoming deliveries for the retailer (roundNo: {roundNo}) round: {t}; {p1.in_round(t).order_t}")
        return sl_retailer

    """
    Supply Line Pre Order calculation for the factory:
    Input: Player 1 (retailer), player 2 (factory), Round Number, Lead Time of the production
    output: supply line pre order factory 
    Prerequisits: None
    -----------------------------------------------------------------------------------------
    The supply line pre order cumulates from all past orders that have been sent to production and are in the produciotn line but have not arrived yet.
    Dependend on the length of the leadtime of production all past outgoing orders from the factory are 
    cumulated till last round. 
    -----------------------------------------------------------------------------------------
    Exceptions: 
    If the roundnumber minus the lead time (e.g. round 3, leadtime= 4 -> 3-4 = -1) is below 0, thus lying in the past
    before the start of the experiment, then the initial values are used, as it is assumed that everything has been 
    constant in the past. 
    """

    # as we have not ordered yet (e.g. lead time = 3; we are in round 5); we want the orders from round 4 and 3
    def getSupplyLinePreOrderFactory(p, automatedFactory: bool, roundNo, leadtimeProduction):
        sl_factory = 0
        for t in range(roundNo - leadtimeProduction + 1, roundNo):
            if t <= 0:
                sl_factory += Constant.INITIAL_INCOMING_DELIVERY_T
            else:
                if automatedFactory:
                    sl_factory += p.in_round(t).factory_order_t
                else:
                    sl_factory += p.in_round(t).order_t
        return sl_factory

    """
    Supply line after ordering: 
    Input: group 
    output: none 
    prerequists: supply line pre order has been calculated, order has been submitted 
    ---------------------------------------------------------------------------------------
    Supply line Post order = Supply line pre order + Order 
    """

    def getSupplyLinePostOrder(p, automatedFactory: bool):
        if automatedFactory:
            p.factory_supplyLinePostOrder = p.factory_supplyLinePreOrder + p.factory_order_t
        p.supplyLinePostOrder = p.supplyLinePreOrder + p.order_t

    def getDemandforLeadtime(p, automatedFactory: bool, roundNo, leadtime):
        demand = 0
        for t in range(roundNo - leadtime + 1, roundNo + 1):  # testing this for factory -> check for retailer
            if t <= 0:
                demand += Constant.INITIAL_INCOMING_DEMAND
            else:
                if automatedFactory:
                    demand += p.in_round(t).factory_incomingDemand
                else:
                    demand += p.in_round(t).incomingDemand

        return demand

    """
    Target inventory: 
    Input: group 
    output: none 
    prerequists: supply line post order has been updated; backlog is current and inventory is current
    ---------------------------------------------------------------------------------------
    Target inventory = (Inventory - Backlog) + Supply line Post Order
    """

    def getTargetInventory(p, automatedFactory: bool):
        """
        if automatedFactory:
            p.factory_targetInventory = (p.factory_inventory -p.factory_backlog_demand_cumulated) + p.factory_supplyLinePostOrder
        p.targetInventory = (p.inventory -p.backlog_demand_cumulated) + p.supplyLinePostOrder
        """
        if automatedFactory:
            p.factory_targetInventory = Constant.LEAD_TIME_PRODUCTION * Constant.CONSTANT_CUSTOMER_DEMAND  # Calculations_General.getDemandforLeadtime(p, True, p.round_number, p.leadtimeProduction())
        p.targetInventory = Constant.LEAD_TIME_DELIVERY_F2R * Constant.CONSTANT_CUSTOMER_DEMAND + Constant.LEAD_TIME_ORDER_R2F * Constant.CONSTANT_CUSTOMER_DEMAND  # Calculations_General.getDemandforLeadtime(p, False, p.round_number, p.leadTime())

        # TODO: factory target inventory should be =  sum (received demand) over lead_time_production periods
    # target inventory: summe(over leadtime) of Demand


class OptimumCalculation_General():
    """
    The optimum calculation:
    Input: Player
    Output: Ordering optimum
    Prerequisit: Supply line pre order, inventory, backlog demand has been set.
    -------------------------------------------------------------------------------
    This function returns the optimum order, based on this rounds supplyline pre order, inventory, backlog and past rounds target inventory.
    Optimum = TargetInventory - (SL Pre Order + Inventory - Backlog)
    ---------------------------------------------------------------------------------
    Exception: if the round is the first round - then take the init value
    """

    # last rounds target inventory: p.in_round(roundNumber-1).targetInventory
    def optimumSuggestion(id, targetInventory, supplyLinePreOrder, inventory, backlog_demand_cumulated):
        opt = targetInventory - (supplyLinePreOrder + (inventory - backlog_demand_cumulated))
        print(
            f"id: {id}; targetinventory: {targetInventory}, supply Line pre order: {supplyLinePreOrder}, optimum: {opt}")
        if opt <= 0:
            return 0
        return opt

    # supply line pre increases if order more than best (e.g. 6) -> because in Supply line
    # target inventory from last period: increases as supply line post increases in period before.
    # both increased by increased order amount: eg.g 2 -> SLPre : 14 (instead of 12); and Targetinv = 18 (instead of 16)

    # if have that in formula: 18 - 14 +0 = 4
    # but we want to include if there has been a shift in the demand. (not considered in SL pre or post and target inventory. ) 