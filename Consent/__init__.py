from otree.api import *

author = "Viviana M. Oberhofer viviana.oberhofer@uibk.ac.at"

doc = """
Consent Page
"""


class C(BaseConstants):
    NAME_IN_URL = 'consent'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def initate_player(player):
        participant = player.participant
        participant.AC = 0
        participant.comprehension = 0
        participant.attempt = 0
        # participant.canContinue = True


def creating_session(subsession: Subsession):
    if subsession.session.config['game'] == 'H-H':
        createGroupMatrix(subsession)
    setTreatments(subsession)
    setRole(subsession)


def createGroupMatrix(subsession: Subsession):
    players = subsession.get_players()
    ppg = subsession.session.config['PLAYERS_PER_GROUP']
    matrix = []
    start = 0
    for i in range(0, len(players), ppg):
        matrix.append(players[start:start + ppg])
        start += ppg
    subsession.set_group_matrix(matrix)


def setTreatments(subsession: Subsession):
    import itertools
    treatments = itertools.cycle([1, 2, 3])  # 1: no, 2: static, 3: chatbot.
    for group in subsession.get_groups():
        if subsession.session.config['game'] == 'H-H':
            treatment = next(treatments)
            for player in group.get_players():
                participant = player.participant
                participant.game = subsession.session.config[
                    'game']  # maybe need this if have certain varying surveys.
                participant.treatment = treatment

        elif subsession.session.config['game'] == 'H-C':
            for player in group.get_players():
                treatment = next(treatments)
                participant = player.participant
                participant.game = subsession.session.config[
                    'game']  # maybe need this if have certain varying surveys.
                participant.treatment = treatment


def setRole(subsession: Subsession):
    for group in subsession.get_groups():
        for player in group.get_players():
            participant = player.participant
            if subsession.session.config['game'] == 'H-H':
                participant.roleID = player.id_in_group
                participant.role = role(player)
            elif subsession.session.config['game'] == 'H-C':
                participant.roleID = 1
                participant.role = 'Retailer'


def role(self):
    if self.id_in_group == 1:
        return 'Retailer'
    elif self.id_in_group == 2:
        return 'Factory'

    # PAGES


class consent(Page):
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        player.initate_player()


page_sequence = [
    consent,
]