"""
-------------------------------------------------------
This file contains and defines the init classes.
The classes are prerequisits of oTree and the models as well.
-------------------------------------------------------
Author: Viviana Oberhofer
Email: viviana.oberhofer@uibk.ac.at
Version: September 2023
-------------------------------------------------------
"""
from otree.api import *
from constant import *
from functions_H_C import InitFunctions
from functions_H_C import Shipment, FulfillDemand, Calculations
from functions_H_C import OptimumCalculation
#from localChatbot import Chatbot
#from chatbot_functions import Chatbot_Functions
from conversationLogging import Log
from django.utils.html import mark_safe

c = cu

doc = "here should be the app description"


class C(BaseConstants):
    NAME_IN_URL = 'beer_exp_H_C'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 18

    # cannot be 0 as otherwise the sequence would have to change (min = 1 )
    LEAD_TIME_ORDER_R2F = Constant.LEAD_TIME_ORDER_R2F
    LEAD_TIME_DELIVERY_F2R = Constant.LEAD_TIME_DELIVERY_F2R
    LEAD_TIME_PRODUCTION = Constant.LEAD_TIME_PRODUCTION

    INITIAL_TARGET_INVENTORY_RETAILER = LEAD_TIME_ORDER_R2F * Constant.INITIAL_ORDER_T + LEAD_TIME_DELIVERY_F2R * Constant.INITIAL_ORDER_T
    INITIAL_TARGET_INVENTORY_FACTORY = LEAD_TIME_PRODUCTION * Constant.INITIAL_ORDER_T


class Subsession(BaseSubsession):
    # here should be variables over subsessions
    pass


class Group(BaseGroup):
    # here are variables that are on group level - note are deleted after each round and group id is new assigned (thus not reachable anymore)
    pass


class Player(BasePlayer):
    incomingDemand = models.IntegerField()  # == order_t_1 of the the lower level
    order_t = models.IntegerField(label='How much will you order?', max=Constant.MAX_ORDER_QUANTITY,
                                  min=Constant.MIN_ORDER_QUANTITY)
    incomingDelivery = models.IntegerField()
    outgoingDelivery = models.IntegerField()  # == incomingDelivery_t_1 of lower level

    inventory = models.IntegerField()  # inventory

    backlog_demand_cumulated = models.IntegerField()  # unfulfilled demand for lower level
    totalCostsBackorders = models.CurrencyField()
    totalCostsInventory = models.CurrencyField()

    fulfilledDemand = models.IntegerField()
    turnover = models.CurrencyField()

    supplyLinePreOrder = models.IntegerField()
    supplyLinePostOrder = models.IntegerField()
    targetInventory = models.IntegerField()

    treatment = models.IntegerField(min=1, max=3)
    game = models.StringField()
    suggestedOptimum = models.IntegerField()

    factory_order_t = models.IntegerField()  # saves what the factory orders at time t.
    factory_incomingDemand = models.IntegerField()  # == order_t_1 of the the lower level
    factory_incomingDelivery = models.IntegerField()
    factory_outgoingDelivery = models.IntegerField()  # == incomingDelivery_t_1 of lower level

    factory_inventory = models.IntegerField()  # inventory

    factory_backlog_demand_cumulated = models.IntegerField()  # unfulfilled demand for lower level
    factory_totalCostsBackorders = models.CurrencyField()
    factory_totalCostsInventory = models.CurrencyField()

    factory_fulfilledDemand = models.IntegerField()
    factory_turnover = models.CurrencyField()

    factory_supplyLinePreOrder = models.IntegerField()
    factory_supplyLinePostOrder = models.IntegerField()
    factory_targetInventory = models.IntegerField()
    factory_optimum = models.IntegerField

    # chat data log
    chatLog = models.LongStringField(blank=True)
    # input data for gpt
    msg = models.LongStringField(blank=True)
    dssButtonClicked = models.BooleanField(initial=False)

    def role(self):
        # if self.id_in_group == 1:
        return 'Retailer'
        # if self.id_in_group == 2:
        #    return 'Factory'

    def getId(self):
        return 1

    def leadTime(self):
        return C.LEAD_TIME_ORDER_R2F + C.LEAD_TIME_DELIVERY_F2R

    def leadtimeDelivery(self):
        return C.LEAD_TIME_DELIVERY_F2R

    def leadtimeOrder(self):
        return C.LEAD_TIME_ORDER_R2F

    def leadtimeProduction(self):
        return C.LEAD_TIME_PRODUCTION

    def initTargetInventory(self):
        return C.INITIAL_TARGET_INVENTORY_RETAILER


# FUNCTIONS
###### randomization / treatments: #careful for one player need a different function!
def creating_session(subsession: Subsession):
    for group in subsession.get_groups():
        for player in group.get_players():
            player.treatment = player.participant.treatment
            player.game = subsession.session.config['game']  # maybe need this if have certain varying surveys.
            Log.startLog(player)


def live_response(player, data):
    if data["user_input"] != None:
        userinput = data["user_input"]
        Log.log(player, userinput, bot=False)
        if userinput == "reset":
            print("reset sent")
            Chatbot_Functions.reset(player)
        elif userinput == "clicked":
            print("button clicked")
            player.dssButtonClicked = True
        else:
            print(f"user Input received :{data}")
            botResponse = Chatbot_Functions.getResponse(userinput, player)
            Log.log(player, botResponse, bot=True)
            return {player.id_in_group: {"bot_response": mark_safe(botResponse)}}

    return {player.id_in_group: {"bot_response": None}}


# Process:
"""
(i) shipments from the upstream decision maker are received and placed in inventory, 
(ii) incoming orders are received from the downstream decision maker and either filled (if inventory is available) or placed in backorder, and 
(iii) a new order is placed and passed to the upstream player. 
"""


# Game Play
def gameAction(p: Player):
    Shipment.getShipment(p, C.LEAD_TIME_DELIVERY_F2R, C.LEAD_TIME_PRODUCTION)
    FulfillDemand.fulfillShipment(p, C.LEAD_TIME_ORDER_R2F)
    Calculations.getTargetInventory(p)
    Calculations.getSupplyLinePreOrder(p, (C.LEAD_TIME_DELIVERY_F2R + C.LEAD_TIME_ORDER_R2F), C.LEAD_TIME_PRODUCTION)


##PAGES
class Introduction(Page):  # TODO: this will be the start page - instructions seperate etc.
    # Display on Introduction page the instructions.

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class NextRound(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == 1:
            InitFunctions.getDataForFirstRound(player)
        else:
            InitFunctions.getDataFromPreviousRound(player)
        gameAction(player)

    # TODO: should we set a time limit here?


class Action(Page):
    def vars_for_template(p: Player):
        round_past = p.round_number - 1
        if p.round_number == 1:
            last_order = Constant.INITIAL_ORDER_T
        else:
            last_order = p.in_round(p.round_number - 1).order_t
        return dict(round_past=round_past, last_order=last_order)


# NOTE: dependent on treatment see suggestion or not
# order something - here should see all relevant data for ordering.
class OrderDecision(Page):
    # here specify what is shown to the user (variables from the Player class if form_model = 'player' or from the Group class if form_model='group')
    form_model = 'player'
    form_fields = ['order_t', 'chatLog']

    def vars_for_template(player):
        player.suggestedOptimum = OptimumCalculation.getOptimum(player)  # possible optimum calculator
        return {"optimum": player.suggestedOptimum, "suggestion_clicked": player.dssButtonClicked}

    @staticmethod
    def live_method(player: Player, data):
        return live_response(player, data)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.factory_optimum = OptimumCalculation.setFactoryOptimum(player)

        Calculations.getSupplyLinePostOrder(player)
        if player.round_number == C.NUM_ROUNDS:
            # if final round than play once more
            gameAction(player)


class FictionalRewards(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        return {"profit": player.turnover - (player.totalCostsBackorders + player.totalCostsInventory)}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.rewards = {
            'turnover': player.turnover,
            'costsInv': player.totalCostsInventory,
            'costsBackorders': player.totalCostsBackorders
        }


page_sequence = [Introduction, NextRound, Action, OrderDecision,
                 FictionalRewards]  # Like this also in the repetition the Introduction is repeated <