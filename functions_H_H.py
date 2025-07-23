from otree.api import *
from constant import *
from functions_general import *


################# Functions for H-H version only ###############################################

class InitFunctions():
    # initalise data
    def getDataForFirstRound(g):
        for p in g.get_players():
            InitFunctions_General.getDataForFirstRound(p, False)

    # get Datafrom Previous round:
    def getDataFromPreviousRound(g):
        for p in g.get_players():
            InitFunctions_General.getDataFromPreviousRound(p, False)


# Process:
"""
(i) shipments from the upstream decision maker are received and placed in inventory, 
(ii) incoming orders are received from the downstream decision maker and either filled (if inventory is available) or placed in backorder, and 
(iii) a new order is placed and passed to the upstream player. 
"""


class Shipment():
    def getShipment(g, leadtimeDelivery, leadTimeProduction):
        p1 = g.get_player_by_id(1)
        p2 = g.get_player_by_id(2)

        # incoming Delivery
        p1.incomingDelivery = Shipment_General.getDeliveryFromFactory(p1, p2, False, leadtimeDelivery)
        p2.incomingDelivery = Shipment_General.getDeliveryFromProduction(p2, False, leadTimeProduction)
        # inventory
        for p in [p1, p2]:
            Shipment_General.addToInventory(p, False)


class FulfillDemand():

    def fulfillShipment(g, leadtimeOrder):
        p1 = g.get_player_by_id(1)
        p2 = g.get_player_by_id(2)
        FulfillDemand_General.getDemand(p1, p2, False, leadtimeOrder)

        for p in [p1, p2]:
            FulfillDemand_General.fulfillDemand(p, False, p.inventory, p.incomingDemand, p.backlog_demand_cumulated)
            FulfillDemand.updateCosts(p)
            FulfillDemand.updateTurnover(p)

    def updateCosts(p):
        p.totalCostsBackorders = FulfillDemand_General.getBackorderCosts(p.totalCostsBackorders,
                                                                         p.backlog_demand_cumulated)
        p.totalCostsInventory = FulfillDemand_General.getInventoryCosts(p.totalCostsInventory, p.inventory)

    def updateTurnover(p):
        p.turnover = FulfillDemand_General.getTurnover(p.turnover, p.outgoingDelivery)


class Calculations():
    def getSupplyLinePreOrder(g, leadtimeDelivery, leadtimeOrder, leadtimeProduction):
        p1 = g.get_player_by_id(1)
        p2 = g.get_player_by_id(2)
        roundNo = p1.round_number

        p1.supplyLinePreOrder = Calculations_General.getSupplyLinePreOrderRetailer(p1, p2, False, roundNo,
                                                                                   (leadtimeDelivery + leadtimeOrder))
        p2.supplyLinePreOrder = Calculations_General.getSupplyLinePreOrderFactory(p2, False, roundNo,
                                                                                  leadtimeProduction)

    # ordering
    # post ordering
    """
    Supply line after ordering: 
    Input: group 
    output: none 
    prerequists: supply line pre order has been calculated, order has been submitted 
    ---------------------------------------------------------------------------------------
    Supply line Post order = Supply line pre order + Order 
    """

    def getSupplyLinePostOrder(g):
        for p in g.get_players():
            Calculations_General.getSupplyLinePostOrder(p, False)

    """
    Target inventory: 
    Input: group 
    output: none 
    prerequists: supply line post order has been updated; backlog is current and inventory is current
    ---------------------------------------------------------------------------------------
    Target inventory = (Inventory - Backlog) + Supply line Post Order
    """

    def getTargetInventory(g):
        for p in g.get_players():
            Calculations_General.getTargetInventory(p, False)


class OptimumCalculation():

    def getOptimum(p, initTargetRetailer, initTargetFactory):
        targetInventory = 0
        if p.round_number == 1:
            if p.id_in_group == 1:
                targetInventory = initTargetRetailer
            else:
                targetInventory = initTargetFactory
        else:
            targetInventory = p.in_round(p.round_number - 1).targetInventory

        return OptimumCalculation_General.optimumSuggestion(p.id_in_group, targetInventory, p.supplyLinePreOrder,
                                                            p.inventory, p.backlog_demand_cumulated)