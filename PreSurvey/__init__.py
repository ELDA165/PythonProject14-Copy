# PreSurvey/__init__.py

from pathlib import Path
from otree.api import *    # gives you models, widgets, BaseConstants, etc.

# 1) locate your project root so we can find _static exactly
BASE_DIR = Path(__file__).resolve().parent.parent
_SURVEY_DIR = BASE_DIR / '_static' / 'global' / 'surveyItems'

# 2) helper to load your Att2Blue.txt file
def _load_txt(filename):
    file_path = _SURVEY_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Couldn’t find survey file: {file_path}")
    return [
        line.strip()
        for line in file_path.read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]

# 3) your data container
class Surveys:
    # load the exact file you have on disk
    att2blueFile = _load_txt('Att2Blue.txt')

    # define 7‑point Likert internally
    SevenPtLikertChoiceValues = list(range(1, 8))
    SvPtLikertChoicesLabels = [
        "Strongly disagree",
        "Somewhat disagree",
        "Slightly disagree",
        "Neither agree nor disagree",
        "Slightly agree",
        "Somewhat agree",
        "Strongly agree",
    ]

# 4) oTree boilerplate
author = "Viviana M. Oberhofer viviana.oberhofer@uibk.ac.at"
doc = "PreSurvey"

class C(BaseConstants):
    NAME_IN_URL = 'presurvey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

# 5) dynamically build one IntegerField per question, with choices
class Player(BasePlayer):
    for idx, question in enumerate(Surveys.att2blueFile):
        locals()[f'att2blue{idx}'] = models.IntegerField(
            label=question,
            choices=list(zip(
                Surveys.SevenPtLikertChoiceValues,
                Surveys.SvPtLikertChoicesLabels
            )),
            widget=widgets.RadioSelectHorizontal()
        )
    # remove the loop variables so they don't linger as non‑model attrs:
    del idx, question

class preSurveyP1(Page):
    form_model = 'player'
    form_fields = [f'att2blue{i}' for i in range(len(Surveys.att2blueFile))]

    def vars_for_template(self):
        return {
            'colSpan': len(Surveys.SevenPtLikertChoiceValues),
            'choices': Surveys.SvPtLikertChoicesLabels,
        }

page_sequence = [preSurveyP1]
