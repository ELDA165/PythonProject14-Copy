from otree.api import *

class Surveys():
    SvPtLikertChoicesLabels = [ "Strongly disagree", "Disagree", "Somewhat disagree", "Neither agree nor disagree", "Somewhat agree", "Agree","Strongly agree"]
    SevenPtLikertChoiceValues = [1,2,3,4,5,6,7]


    att2blueFile = open("_static/global/survey_items/Att2Blue.txt", "r").readlines()

    qAtt2Blue = [None] * len(att2blueFile)
    for i, line in enumerate(att2blueFile):
        qAtt2Blue[i]=models.IntegerField(widget= widgets.RadioSelectHorizontal,
                                         label=line.strip(),
                                         choices=SevenPtLikertChoiceValues)
