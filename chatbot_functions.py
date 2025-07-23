from localChatbot import Chatbot
from getDataForCbResponses import DataForCbResponses as DataSource

# this saves the answer option instances
answerOptionsInstances = []
# an instance of the chatbot
chatbotInstance = Chatbot.localChatbot.copy()

# deviation handeled or not
userInputNeedsHandeling = False

"""
Class Answer Options: 
Each user has an instance, with their id (subsession id (player subsession id == participant session id))
here the last key and resulting options are saved. 
"""


class AnswerOptions():
    # userIDinSession = ""
    userIDinGroup = ""
    lastKey = ""
    answerOptions = []
    userSuggestion = 0

    def __init__(self, player):
        # self.userIDinSession = player.id_in_subsession
        self.userIDinGroup = player.getId()
        self.lastKey = "start"
        self.answerOptions = [1, 2, 3]

    def updateLastKey(self, newKey):
        self.lastKey = newKey

    def updateOptions(self, lastKey):
        options = []

        if lastKey in chatbotInstance:
            if "retailer" in chatbotInstance[lastKey]:
                if self.userIDinGroup == 1:
                    chatbotOptions = chatbotInstance[lastKey]["retailer"]
                else:
                    chatbotOptions = chatbotInstance[lastKey]["factory"]
            else:
                chatbotOptions = chatbotInstance[lastKey]

            for i in chatbotOptions:
                if i == 0:
                    continue
                else:
                    options.append(i)

        self.answerOptions = options


class Chatbot_Functions():
    """
    Function called by __init__py.live_response
    Method to get a chatbot response:
    handels the input and extracts the expected string and returns it.

    """

    def getResponse(userInput, player):
        global userInputNeedsHandeling
        userInput = int(userInput)
        answerOpt = Chatbot_Functions.getAnswerOptionsInstance(player)

        # if last key was requiring a user input, then userInputRequest was sent and now needs to be dealt with
        if (answerOpt.lastKey == "deviate" or answerOpt.lastKey == "userEstimate") and userInputNeedsHandeling == True:
            botResponseKey = Chatbot_Functions.requestUserInput(answerOpt, userInput)
            response = Chatbot_Functions.getBotResponse(botResponseKey, answerOpt, player)
            userInputNeedsHandeling = False

        else:
            botResponseKey = Chatbot_Functions.identifyUserInput(userInput, answerOpt)
            # check if a user input is needed. if is alternativeKey is not "" but is userInputRequest
            alternativeKey = Chatbot_Functions.checkIfUserInputNeeded(botResponseKey, answerOpt)
            if alternativeKey != "":
                # needs user input thus sends userInputRequest as key through without changing answerOpt.
                response = Chatbot_Functions.getBotResponse(alternativeKey, answerOpt, player)
                userInputNeedsHandeling = True
            else:
                response = Chatbot_Functions.getBotResponse(botResponseKey, answerOpt, player)
        return response

    """
    Method sets the users input as their suggestion and returns the last key 
    function called if user input has alreadybeen requested.
    """

    def requestUserInput(answerOpt, userInput):
        # case 2: last key == deviate or userEstimate -> this needs to before identifyUserInput
        # then should have gotten userInputRequest and the user input is their suggestion value

        # here botresponse key already was deviate or userInput - is saved in answerOpt.

        # 1st set userinput as suggestion
        answerOpt.userSuggestion = userInput
        # 2nd hand over to get response.
        return answerOpt.lastKey

    """
    Method checks if Botresponse key retreived now equals deviate or userEstimate.
    If they do then instead the indentifyUserInput is requested to be used as a key instead of the actual key. 
    """

    def checkIfUserInputNeeded(botResponseKey, answerOpt):
        # case 1: bot response key == "deviate" or "userEstimate"  -> this needs to be post identifyUserInput
        # then set last key to deviate or userEstimate
        # and send response: userInputRequest
        if botResponseKey == "deviate" or botResponseKey == "userEstimate":
            # if it is the response Key then the last key is already set and the options are set already.
            # only need to hand back the different key.
            return "userInputRequest"
        else:
            return ""

    """
    Method to get the right instance of the answer option class

    If no instance for a player exists a new one is created and added to the list. 
    """

    def getAnswerOptionsInstance(player):
        global answerOptionsInstances
        if answerOptionsInstances == []:
            option = AnswerOptions(player)
            answerOptionsInstances.append(option)
            return option

        for opt in answerOptionsInstances:
            if opt.userIDinGroup == player.getId():
                return opt

        option = AnswerOptions(player)
        answerOptionsInstances.append(option)
        return option

    """
    method to get the new key for the new response based on the users input
    the user's input is checked if viable (a.k.a. an options)
    if it is then based on the last key and the user input the new key is extracted and returned. 

    This also updates the new key as the last key and new options
    """

    def identifyUserInput(userInput, answerOpt):
        if userInput in answerOpt.answerOptions:
            if Chatbot_Functions.__checkForRoleSpecificResponse(answerOpt.lastKey):
                role = Chatbot_Functions.__getRoleName(answerOpt.userIDinGroup)
                botResponseKey = chatbotInstance[answerOpt.lastKey][role][userInput]
            else:
                botResponseKey = chatbotInstance[answerOpt.lastKey][userInput]
        else:
            botResponseKey = "error"

        Chatbot_Functions.updateAnswerOptions(botResponseKey, answerOpt)
        print(
            f"current key: {botResponseKey} updated Last key.{answerOpt.lastKey} ,new options {answerOpt.answerOptions} ")
        return botResponseKey

    """update last key"""

    def updateAnswerOptions(newKey, answerOpt):
        answerOpt.updateLastKey(newKey)
        answerOpt.updateOptions(newKey)

    """Method to return the string based on the Key.

      If answer is role-specific then the specific answer is returned.  """

    def getBotResponse(botResponseKey, answerOpt, player):

        if Chatbot_Functions.__checkForRoleSpecificResponse(botResponseKey):
            response = Chatbot_Functions.__getRoleSpecificResponse(botResponseKey, player, answerOpt)
        else:
            if botResponseKey == "suggestion":
                values = DataSource.calculations(botResponseKey, player, answerOpt)
                response = chatbotInstance[botResponseKey][0].format(*values)
            else:
                response = chatbotInstance[botResponseKey][0]

        return response

    """
    When closing the chat we want to reset the conversation to start at the beginning. 
    Thus here it is just removed. 

    Alternative implementation if does not work: set last key= "start" and oupdate the options. 
    """

    def reset(player):
        global answerOptionsInstances
        answerOpt = Chatbot_Functions.getAnswerOptionsInstance(player)
        answerOptionsInstances.remove(answerOpt)

    def __getRoleName(player_id):
        if player_id == 1:
            return "retailer"
        else:
            return "factory"

    """
    Method to check if a rolespecific response is needed
    returns a boolean 
    """

    def __checkForRoleSpecificResponse(key):
        return key in ["explainGeneral", "explain", "userEstimate", "deviate"]

    """
    Method, returns the response as string, to the botResponseKey, for rolespecific responses. 
    """

    def __getRoleSpecificResponse(botResponseKey, player, answerOpt):
        values = DataSource.calculations(botResponseKey, player, answerOpt)
        role = Chatbot_Functions.__getRoleName(player.getId())

        if botResponseKey in ["explainGeneral", "explain"]:
            response = chatbotInstance[botResponseKey][role][0].format(*values)

        elif botResponseKey in ["userEstimate", "deviate"]:
            difference = Chatbot_Functions.__getMoreLessEqualThanOptimum(answerOpt.userSuggestion,
                                                                         player.suggestedOptimum)
            response = chatbotInstance[botResponseKey][role][0][difference].format(*values)

        return response

    """
    Method checks if user suggestion is more less or equal to the optimum.
    Returns string.
    """

    def __getMoreLessEqualThanOptimum(userSuggestion, optimum):
        if userSuggestion > optimum:
            return "more"
        elif userSuggestion < optimum:
            return "less"
        else:
            return "equal"