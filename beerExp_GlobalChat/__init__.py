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

c = cu

doc = "here should be the app description"


class C(BaseConstants):
    NAME_IN_URL = 'beer_exp_GlobalChat'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 7

    # cannot be 0 as otherwise the sequence would have to change (min = 1 )
    LEAD_TIME_ORDER_R2F = 2
    LEAD_TIME_DELIVERY_F2R = 2
    LEAD_TIME_PRODUCTION = 3

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
    suggestedOptimum = models.IntegerField()

    def role(self):
        if self.id_in_group == 1:
            return 'Retailer'
        if self.id_in_group == 2:
            return 'Factory'

        ##cannot put this in an extra file


class Message(ExtraModel):
    group = models.Link(Group)
    sender = models.Link(Player)
    text = models.StringField()


def to_dict(msg: Message):
    return dict(sender=msg.sender.id_in_group, text=msg.text)


# FUNCTIONS
###### randomization / treatments:
def creating_session(subsession: Subsession):
    import itertools
    treatments = itertools.cycle([1, 2])  # 1: global chat, 2:global chatbot
    for group in subsession.get_groups():
        treatment = next(treatments)
        for player in group.get_players():
            player.treatment = treatment
            # participant = player.participant
            # participant.treatment= treatment  # maybe need this if have certain varying surveys.


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
    form_fields = ['order_t']

    def vars_for_template(player):
        player.suggestedOptimum = OptimumCalculation.getOptimum(player, C.INITIAL_TARGET_INVENTORY_RETAILER,
                                                                C.INITIAL_TARGET_INVENTORY_FACTORY)  # possible optimum calculator
        return dict(optimum=player.suggestedOptimum)


# place the order
class OrderWaitPage(WaitPage):
    body_text = 'Waiting for other participants to contribute.'

    # after_all_players_arrive: this can only be done on WaitPages and is to update the variables. this executes for a whole group
    @staticmethod
    def after_all_players_arrive(group: Group):
        Calculations.getSupplyLinePostOrder(group)
        Calculations.getTargetInventory(group)


class Test(Page):
    @staticmethod
    def js_vars(player: Player):
        return dict(my_id=player.id_in_group)

    @staticmethod
    def live_method(player: Player, data):
        my_id = player.id_in_group
        group = player.group

        if 'text' in data:
            text = data['text']
            msg = Message.create(group=group, sender=player, text=text)
            return {0: [to_dict(msg)]}
        return {my_id: [to_dict(msg) for msg in Message.filter(group=group)]}


page_sequence = [Introduction, Test, IntroductionSynchronisation, GetDataFromPreviousRound, ActionWaitPage, Action,
                 OrderDecision, OrderWaitPage]  # Like this also in the repetition the Introduction is repeated <