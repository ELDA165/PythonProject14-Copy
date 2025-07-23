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
from functions_H_H import *
from localChatbot import Chatbot
from chatbot_functions import Chatbot_Functions
from conversationLogging import Log
from django.utils.html import mark_safe

c = cu

doc = "here should be the app description"


class C(BaseConstants):
    NAME_IN_URL = 'pretest_beer_exp_H_H'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3

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

    # chat data log
    chatLog = models.LongStringField(blank=True)
    # input data for gpt
    msg = models.LongStringField(blank=True)
    dssButtonClicked = models.BooleanField(initial=False)

    def role(self):
        if self.id_in_group == 1:
            return 'Retailer'
        if self.id_in_group == 2:
            return 'Factory'

    def getId(self):
        return self.id_in_group

    def leadTime(self):
        if self.id_in_group == 1:
            return C.LEAD_TIME_ORDER_R2F + C.LEAD_TIME_DELIVERY_F2R
        else:
            return C.LEAD_TIME_PRODUCTION

    def leadtimeDelivery(self):
        if self.id_in_group == 1:
            return C.LEAD_TIME_DELIVERY_F2R
        else:
            return

    def leadtimeOrder(self):
        if self.id_in_group == 1:
            return C.LEAD_TIME_ORDER_R2F
        else:
            return

    def leadtimeProduction(self):
        if self.id_in_group == 2:
            return C.LEAD_TIME_PRODUCTION
        else:
            return

    def initTargetInventory(self):
        if self.id_in_group == 1:
            return C.INITIAL_TARGET_INVENTORY_RETAILER
        else:
            return C.INITIAL_TARGET_INVENTORY_FACTORY


# FUNCTIONS
###### randomization / treatments:
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
def gameAction(g: Group):
    Shipment.getShipment(g, C.LEAD_TIME_DELIVERY_F2R, C.LEAD_TIME_PRODUCTION)
    FulfillDemand.fulfillShipment(g, C.LEAD_TIME_ORDER_R2F)
    Calculations.getSupplyLinePreOrder(g, C.LEAD_TIME_DELIVERY_F2R, C.LEAD_TIME_ORDER_R2F, C.LEAD_TIME_PRODUCTION)


##PAGES
class Introduction(Page):  # TODO: this will be the start page - instructions seperate etc.
    # Display on Introduction page the instructions.
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    # initate the values with the constants - only if round 1


class IntroductionSynchronisation(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        InitFunctions.getDataForFirstRound(group)

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    # set beginning of round - values from previous round & demand & receive shipment & fulfill order


class GetDataFromPreviousRound(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        InitFunctions.getDataFromPreviousRound(group)

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number != 1


class ActionWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        gameAction(group)


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
        player.suggestedOptimum = OptimumCalculation.getOptimum(player, C.INITIAL_TARGET_INVENTORY_RETAILER,
                                                                C.INITIAL_TARGET_INVENTORY_FACTORY)  # possible optimum calculator
        return {"optimum": player.suggestedOptimum, "suggestion_clicked": player.dssButtonClicked}

    @staticmethod
    def live_method(player: Player, data):
        return live_response(player, data)


# place the order
class OrderWaitPage(WaitPage):
    body_text = 'Waiting for other participants to contribute.'

    # after_all_players_arrive: this can only be done on WaitPages and is to update the variables. this executes for a whole group
    @staticmethod
    def after_all_players_arrive(group: Group):
        Calculations.getSupplyLinePostOrder(group)
        Calculations.getTargetInventory(group)


class EndToolWarmup(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Introduction, IntroductionSynchronisation, GetDataFromPreviousRound, ActionWaitPage, Action,
                 OrderDecision, OrderWaitPage,
                 EndToolWarmup]  # Like this also in the repetition the Introduction is repeated <  """Test3, Test2, Test,"""