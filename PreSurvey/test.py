# PreSurvey/__init__.py

from pathlib import Path
from otree.api import *

# 1) Where your project root lives (so we can find _static)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2) Absolute path to the folder containing your .txt files
_SURVEY_DIR = BASE_DIR / '_static' / 'global' / 'surveyItems'


# 3) Helper to load any survey text file from that folder
def _load_txt(filename):
    file_path = _SURVEY_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Couldn’t find survey file: {file_path}")
    # Read non‑blank lines, strip trailing whitespace
    return [line.strip() for line in file_path.read_text(encoding='utf-8').splitlines() if line.strip()]


# 4) Your survey data class
class Surveys:
    # loads “_static/global/surveyItems/att2blueFile.txt”
    att2blueFile = _load_txt('Att2Blue.txt')

    # example Likert definitions
    SevenPtLikertChoiceValues = [1, 2, 3, 4, 5, 6, 7]
    SvPtLikertChoicesLabels = [
        "Strongly disagree",
        "Somewhat disagree",
        "Slightly disagree",
        "Neither agree nor disagree",
        "Slightly agree",
        "Somewhat agree",
        "Strongly agree",
    ]


# 5) Your oTree constants and models
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

class Player(BasePlayer):
    # Dynamically create a StringField per survey question
    for idx, question in enumerate(Surveys.att2blueFile):
        locals()[f'att2blue{idx}'] = models.StringField(label=question)

class preSurveyP1(Page):
    form_model = 'player'
    form_fields = [f'att2blue{i}' for i in range(len(Surveys.att2blueFile))]

    def vars_for_template(self):
        return {
            'colSpan': len(Surveys.SevenPtLikertChoiceValues),
            'choices': Surveys.SvPtLikertChoicesLabels,
        }

page_sequence = [preSurveyP1]
