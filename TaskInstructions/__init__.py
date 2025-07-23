from otree.api import *
from checkquestions import CheckQuestions
from constant import *

author = "Viviana M. Oberhofer viviana.oberhofer@uibk.ac.at"

doc = """
Task TaskInstructions
"""


class C(BaseConstants):
    NAME_IN_URL = 'taskInstructions'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # here need some multiple choice questions to check that they read it : https://fileshare.uibk.ac.at/lib/fdfec4f0-b063-4866-8bd9-9c86ba2909f4/file/Instructions/models.py

    p1_tier = models.IntegerField(widget=widgets.RadioSelect,
                                  label="The supply chain has how many tiers?",
                                  choices=[
                                      [1, "2"],
                                      [-1, "3"],
                                      [-2, "4"]
                                  ])
    p1_RetFact = models.IntegerField(widget=widgets.RadioSelect,
                                     label="Which statement is true?",
                                     choices=[
                                         [-1, "The factory delivers products to the customer."],
                                         [1, "The retailer orders products from the factory."],
                                         [-2, "The customer orders products from the factory."],
                                         [-3, "The retailer delivers products to the factory."]
                                     ])

    p2_LT = models.IntegerField(widget=widgets.RadioSelect,
                                label="What is leadtime?",
                                choices=[
                                    [-1, "The time it takes for an order to arrive at an upper-tier."],
                                    [-2, "The time the factory needs to produce a product."],
                                    [1,
                                     "The time it takes for an order to arrive at an upper-tier or the delivery to arrive at a lower-tier."],
                                ])
    p2_Ret1 = models.IntegerField(widget=widgets.RadioSelect,
                                  label="How many periods does it take the retailer to receive a product from the factory?",
                                  choices=[
                                      [-1, Constant.LEAD_TIME_DELIVERY_F2R + 1],
                                      [1, Constant.LEAD_TIME_DELIVERY_F2R],
                                      [-2, Constant.LEAD_TIME_DELIVERY_F2R - 1],
                                      [-3, Constant.LEAD_TIME_DELIVERY_F2R + 2]
                                  ])
    p2_LT_RetFact = models.IntegerField(widget=widgets.RadioSelect,
                                        label="How many periods does it take for the retailer's order to arrive at the factory?",
                                        choices=[
                                            [1, Constant.LEAD_TIME_ORDER_R2F],
                                            [-1, Constant.LEAD_TIME_ORDER_R2F + 1],
                                            [-2, Constant.LEAD_TIME_ORDER_R2F - 1],
                                            [-3, Constant.LEAD_TIME_ORDER_R2F - 2]
                                        ])
    p2_Fact1 = models.IntegerField(widget=widgets.RadioSelect,
                                   label="How many periods does it take the factory to receive its order?",
                                   choices=[
                                       [-1, Constant.LEAD_TIME_PRODUCTION + 1],
                                       [1, Constant.LEAD_TIME_PRODUCTION],
                                       [-2, Constant.LEAD_TIME_PRODUCTION - 1],
                                       [-3, Constant.LEAD_TIME_PRODUCTION + 2]
                                   ])

    p3_InvStart = models.IntegerField(widget=widgets.RadioSelect,
                                      label="What is your inventory in the beginning?",
                                      choices=[
                                          [-1, Constant.INITIAL_INVENTORY + 1],
                                          [1, Constant.INITIAL_INVENTORY],
                                          [-2, Constant.INITIAL_INVENTORY + 2],
                                          [-3, Constant.INITIAL_INVENTORY + 3]
                                      ])
    p3_CostInv = models.IntegerField(widget=widgets.RadioSelect,
                                     label="What are the costs per item kept in your inventory per period?",
                                     choices=[
                                         [1, Constant.INVENTORY_COST_PER_UNIT],
                                         [-1, Constant.INVENTORY_COST_PER_UNIT + 1],
                                         [-2, Constant.INVENTORY_COST_PER_UNIT + 2],
                                         [-3, Constant.INVENTORY_COST_PER_UNIT + 3]
                                     ])
    p3_CostBlg = models.IntegerField(widget=widgets.RadioSelect,
                                     label="What are the costs per unfulfilled order item per period?",
                                     choices=[
                                         [1, Constant.BACKORDER_PENALTY_COST_PER_UNIT],
                                         [-1, Constant.BACKORDER_PENALTY_COST_PER_UNIT + 4],
                                         [-2, Constant.BACKORDER_PENALTY_COST_PER_UNIT + 2],
                                         [-3, Constant.BACKORDER_PENALTY_COST_PER_UNIT + 1]
                                     ])


class start(Page):
    pass


class Tier(Page):
    form_model = 'player'
    form_fields = ['p1_tier', 'p1_RetFact']

    # check form for errors
    @staticmethod
    def error_message(player,
                      values):  # standard otree function. # here count and change participant variables. if return something, then the participant cannot move on.
        val = CheckQuestions.checkForComprehensionErrors(player, values)
        if val is not None:
            return val


class TierDetail(Page):
    form_model = 'player'
    form_fields = ['p2_LT', 'p2_Ret1', 'p2_LT_RetFact', 'p2_Fact1']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            "LTR2F": Constant.LEAD_TIME_ORDER_R2F,
            "LTF2R": Constant.LEAD_TIME_DELIVERY_F2R,
            "LTProd": Constant.LEAD_TIME_PRODUCTION,
            "roleID": player.participant.roleID,
        }


class RoleDetail(Page):
    form_model = 'player'
    form_fields = ['p3_InvStart', 'p3_CostInv', 'p3_CostBlg']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'initInv': Constant.INITIAL_INVENTORY,
            'initBackl': Constant.INITIAL_BACKLOG_DEMANDS,
            'turnover': Constant.TURNOVER_PER_UNIT_DELIVERED,
            'costsInv': Constant.INVENTORY_COST_PER_UNIT,
            'costsBackl': Constant.BACKORDER_PENALTY_COST_PER_UNIT,
            'custDem': Constant.CONSTANT_CUSTOMER_DEMAND,
            'roleIdIs1': player.participant.roleID == 1,
            'gameIsHH': player.participant.game == 'H-H'
        }


class GuiGameAction(Page):
    pass


class GuiPlay(Page):
    pass


page_sequence = [
    start,
    Tier,
    TierDetail,
    RoleDetail,
    GuiGameAction,
    # GuiPlay
]