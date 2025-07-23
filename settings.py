from os import environ
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0)
SESSION_CONFIGS = [

    #dict(
       # name='beerExp_H_C',
        #display_name='beer experiment H-C condition',
       # num_demo_participants=3,
       # PLAYERS_PER_GROUP = None,
       # game='H-C',
        #app_sequence=['Consent', 'ToolWarmUpTask_H_C',  'beerExp_H_C', 'End']
   # ),



    dict(
        name='beerexp_GlobalChat', 
        display_name='beer experiment H-H global chat condition', 
        num_demo_participants=6,
        PLAYERS_PER_GROUP=2,
        game='H-H',
        #app_sequence=['beerExp_GlobalChat']
        app_sequence=['Consent', 'PreSurvey', 'TaskInstructions', 'ToolWarmUpTask_H_H', 'beerExp_H_H', 'End'] #['Consent', 'PreSurvey', 'TaskInstructions', 'ToolWarmUpTask', 'beerExp_H_H', 'PostSurvey', 'End']
    ),
]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False # if true then rounds automatically, if false use currency
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = ['treatment','game','AC', 'comprehension', 'attempt', 'role', 'roleID', 'rewards']
SESSION_FIELDS = []
ROOMS = []

SECRET_KEY = 'dev_key_change_this'


# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

##for production mode:
# need username & password so others can't start sessions

#DEBUG = False if environ.get('OTREE_PRODUCTION') not in {None, '', '0'} else True




#INSTALLED_APPS = ['otree']

