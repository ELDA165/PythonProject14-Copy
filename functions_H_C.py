from otree.api import *
from constant import *
from functions_general import *


################# Functions for H-C version only ###############################################

class InitFunctions():
    # initalise data
    def getDataForFirstRound(p):
        InitFunctions_General.getDataForFirstRound(p, True)

    # get Datafrom Previous round:
    def getDataFromPreviousRound(p):
        InitFunctions_General.getDataFromPreviousRound(p, True)


# Process:
"""
(i) shipments from the upstream decision maker are received and placed in inventory, 
(ii) incoming orders are received from the downstream decision maker and either filled (if inventory is available) or placed in backorder, and 
(iii) a new order is placed and passed to the upstream player. 
"""


class Shipment():
    def getShipment(p, leadtimeDelivery, leadTimeProduction):
        # incoming Delivery
        p.incomingDelivery = Shipment_General.getDeliveryFromFactory(p, None, True, leadtimeDelivery)
        p.factory_incomingDelivery = Shipment_General.getDeliveryFromProduction(p, True, leadTimeProduction)

        # inventory
        Shipment_General.addToInventory(p, True)


class FulfillDemand():

    def fulfillShipment(p, leadtimeOrder):
        FulfillDemand_General.getDemand(p, None, True, leadtimeOrder)

        FulfillDemand_General.fulfillDemand(p, True, p.factory_inventory, p.factory_incomingDemand,
                                            p.factory_backlog_demand_cumulated)
        FulfillDemand_General.fulfillDemand(p, False, p.inventory, p.incomingDemand, p.backlog_demand_cumulated)

        FulfillDemand.updateCosts(p)
        FulfillDemand.updateTurnover(p)

    def updateCosts(p):
        p.totalCostsBackorders = FulfillDemand_General.getBackorderCosts(p.totalCostsBackorders,
                                                                         p.backlog_demand_cumulated)
        p.totalCostsInventory = FulfillDemand_General.getInventoryCosts(p.totalCostsInventory, p.inventory)
        p.factory_totalCostsBackorders = FulfillDemand_General.getBackorderCosts(p.factory_totalCostsBackorders,
                                                                                 p.factory_backlog_demand_cumulated)
        p.factory_totalCostsInventory = FulfillDemand_General.getInventoryCosts(p.factory_totalCostsInventory,
                                                                                p.factory_inventory)

    def updateTurnover(p):
        p.turnover = FulfillDemand_General.getTurnover(p.turnover, p.outgoingDelivery)
        p.factory_turnover = FulfillDemand_General.getTurnover(p.factory_turnover, p.factory_outgoingDelivery)


class Calculations():
    def getSupplyLinePreOrder(p, leadtimeRetailer, leadtimeProduction):
        roundNo = p.round_number

        p.supplyLinePreOrder = Calculations_General.getSupplyLinePreOrderRetailer(p, None, True, roundNo,
                                                                                  leadtimeRetailer)
        p.factory_supplyLinePreOrder = Calculations_General.getSupplyLinePreOrderFactory(p, True, roundNo,
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

    def getSupplyLinePostOrder(p):
        Calculations_General.getSupplyLinePostOrder(p, True)
        Calculations_General.getSupplyLinePostOrder(p, False)

    """
    Target inventory: 
    Input: group 
    output: none 
    prerequists: supply line post order has been updated; backlog is current and inventory is current
    ---------------------------------------------------------------------------------------
    Target inventory = (Inventory - Backlog) + Supply line Post Order
    """

    def getTargetInventory(p):
        Calculations_General.getTargetInventory(p, True)
        Calculations_General.getTargetInventory(p, False)


class OptimumCalculation():
    ##Optimum Calcualation
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

    def getOptimum(p):
        targetInventory = p.targetInventory
        return OptimumCalculation_General.optimumSuggestion(1, targetInventory, p.supplyLinePreOrder, p.inventory,
                                                            p.backlog_demand_cumulated)

    def setFactoryOptimum(p):
        targetInventory = p.factory_targetInventory
        p.factory_optimum = OptimumCalculation_General.optimumSuggestion(2, targetInventory,
                                                                         p.factory_supplyLinePreOrder,
                                                                         p.factory_inventory,
                                                                         p.factory_backlog_demand_cumulated)

        p.factory_order_t = p.factory_optimum
        return p.factory_optimum
