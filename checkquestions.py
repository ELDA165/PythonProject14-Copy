
class CheckQuestions():
    def checkForComprehensionErrors(player, values):  ##right now: can always continue and repeat the page as often as they want.
        error_messages = dict()
        controlQuestionErrors = 0

        for field_name in values:
            if not field_name.startswith('AC'):
                if values[field_name] < 0: # value would be 1 if correct answer is set
                    controlQuestionErrors += 1
                    error_messages[field_name] = "Wrong answer for " + str(field_name)

        player.participant.comprehension += controlQuestionErrors

        if controlQuestionErrors > 0: # if errors were made
            player.participant.attempt += 1 # how many attempts were made
            return error_messages

        return None


    def checkForACErrors(player ,values):
        acQuestionErrors = 0

        for field_name in values:
            if field_name.startswith('AC'):
                if values[field_name] < 0: # value would be 1 if correct answer is set
                    acQuestionErrors += 1

        player.participant.AC += acQuestionErrors

