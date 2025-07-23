from otree.api import *
from surveyItems import *




author = "Viviana M. Oberhofer viviana.oberhofer@uibk.ac.at"

doc = """
PreSurvey
"""


class C(BaseConstants):
    NAME_IN_URL = 'presurvey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    for i in range(len(Surveys.att2blueFile)):
        exec("att2blue%d = Surveys.qAtt2Blue[i]" % i)
        del i

    # PAGES


class preSurveyP1(Page):
    all_fields = list()

    for i in range(len(Surveys.att2blueFile)):
        all_fields.append("att2blue%d" % i)

    form_model = "player"
    form_fields = all_fields

    def vars_for_template(self):
        return {
            "colSpan": len(Surveys.SevenPtLikertChoiceValues),
            "choices": Surveys.SvPtLikertChoicesLabels
        }


page_sequence = [
    preSurveyP1
]