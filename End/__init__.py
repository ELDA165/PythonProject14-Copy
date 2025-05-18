from otree.api import *


author = "Viviana M. Oberhofer viviana.oberhofer@uibk.ac.at"

doc = """
Consent Page
"""

class C(BaseConstants):
    NAME_IN_URL = 'end'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    roleId = models.IntegerField()
    game = models.StringField()
    treatment = models.IntegerField()
    roleName = models.StringField()




def creating_session(subsession : Subsession):
    for group in subsession.get_groups():
            for player in group.get_players():
                participant = player.participant
                player.game= participant.game
                player.treatment= participant.treatment
                player.roleId = participant.roleID
                player.roleName = participant.role



# PAGES
class end(Page):

    @staticmethod
    def vars_for_template(player: Player):
        turnover=  player.participant.rewards.get('turnover', 0)
        costsInv = player.participant.rewards.get('costsInv', 0)
        costsBackorders = player.participant.rewards.get('costsBackorders', 0)
        player.payoff = (turnover - (costsInv  + costsBackorders ))

        return {
            'turnover': turnover,
            'costsInv': costsInv,
            'costsBackorders': costsBackorders,
            'payoff' : player.payoff
        }



page_sequence = [
    end,
]