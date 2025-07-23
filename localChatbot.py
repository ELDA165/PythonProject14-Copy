#python library: {"key" : "value", }


#f strings:
""""d = {
          # no f here
  "message": "Hi There, {0}"
}

print(d["message"].format("Dave"))
"""
class Chatbot(): #need one input saving.stuffy
    localChatbot = {
        "start": {
            0: "Hello. If you want a suggestion what to order, I am here to help. <br/> <br/> Just enter one of the following numbers:<br/>(1) No, thanks.<br/>(2) Tell me how much to order!<br/>(3) Explain how I should order the order quantity!",
            1: "end",
            2: "suggestion",
            3: "explainGeneral",
          },
        "end": {
            0: "Ok, if you need anything else, just type (1).",
            1: "start",
          },
        "suggestion": {
            0: """Based on my calculations I suggest to order {0}. <br/><br/>
            How can I help you next? <br/>
            (1) Explain why.<br/>
            (2) What if you deviate from my suggestion?<br/>
            (3) Nothing else.""" ,
            1: "explain",
            2: "deviate",
            3: "end",
          },
        "explainGeneral": {
            "retailer": {
                0: """For the consideration of how much to order, take into account your past demand: <br/>
                  <table> 
                    <tr> 
                      <th>Round</th>
                      <th>Past Demand</th>
                    </tr> 
                      <td>{0}</td>
                      <td>{3}</td>
                    </tr>
                    </tr> 
                      <td>{1}</td>
                      <td>{4}</td>
                    </tr>
                    </tr> 
                      <td>{2}</td>
                      <td>{5}</td>
                    </tr>
                    <tr>
                      <th>Average Past Demand</th>
                      <td> {6}</td>
                    </tr>
                  </table><br/>
                  Also consider your past orders:<br/>
                  You have ordered {7} 3 periods ago, {8} 2  periods ago, and {9} last period, and your inventory is {10}. 
                  Also consider that the customers demand is constant at 4.
                  <br/> <br/> 
                  How can I help you next?<br/>
                  (1) How much should I order? <br/>
                  (2) What happens if I order ...? <br/>
                  (3) Nothing else. 
                  """,
                  1: "suggestion",
                  2: "userEstimate",
                  3: "end",
            },
            "factory": {
                0: """For the consideration of how much to order, take into account your incoming demand: 
                <table> 
                    <tr> 
                      <th>Round</th>
                      <th>Past Demand</th>
                    </tr> 
                      <td>{0}</td>
                      <td>{3}</td>
                    </tr>
                    </tr> 
                      <td>{1}</td>
                      <td>{4}</td>
                    </tr>
                    </tr> 
                      <td>{2}</td>
                      <td>{5}</td>
                    </tr>
                    <tr>
                      <th>Average Past Demand</th>
                      <td> {6}</td>
                    </tr>
                </table><br/>
                Also consider your past orders. You have ordered {7} 2  periods ago, and {8} last period, and your inventory is {9}.
                <br/> <br/> 
                How can I help you next?<br/>
                (1) How much should I order? <br/>
                (2) What happens if I order ...? <br/>
                (3) Nothing else. """,
                1: "suggestion",
                2: "userEstimate",
                3: "end",
            }
        },
        "explain": {
            "retailer": {
                0: """As you are the retailer, this means everything you order will take {0} periods until you receive it. 
                As you have ordered {1} 3 periods ago, {2} 2  periods ago, and {3} last period, and your inventory is {4}. You should order {5}. 
                This is based on your customers' demand, which is constant at 4. 
                Thus, your target level to have in the supply line and inventory is {6}. 
                If you sum up your past orders and inventory, you get {7}. The difference to your target level is {8}. Thus you should order {5}. 
                <br/> If you enter 1, you will come to the end and can start this chat again.""",
                1: "end",
            },
            "factory": {
                0: """You are the factory, thus everything you produce, takes {0} periods to reach your inventory.
                As you have ordered {1} 2 periods ago, {2} last period, and your inventory is {3}. You should order {4}.
                This is based on the average retailer's demand {5}. 
                Thus, your target level to have in production and inventory is {6}. 
                If you sum up your past orders and inventory, you get {7}. The difference to your target level is {8}. Thus you should order {4}.
                <br/> If you enter 1, you will come to the end and can start this chat again.""",
                1: "end",
            }
        },
        "userEstimate": {
            "retailer" : {
                0: {
                    "more": """Please take into consideration the following list: 
                            <table> 
                              <tr> 
                                <th>Round</th>
                                <th>Past Demand</th>
                              </tr> 
                                <td>{0}</td>
                                <td>{1}</td>
                                <td>{2}</td>
                              </tr>
                              </tr> 
                                <td>{3}</td>
                                <td>{4}</td>
                                <td>{5}</td>
                              </tr>
                            </table><br/> 
                            This table shows you what will happen assuming you order {6} now. <br/> 
                            Assuming the factory can meet your demands, you will receive that order in {7} periods. As the demand is constant, you will increase your inventory in {7} periods by {8} items. <br/> 
                            This means your costs will increase by {9} of additional costs in period {7}.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) How much should I order? <br/>
                            (2) What happens if I order ...? <br/>
                            (3) Nothing else. """,
                    "less": """Please take into consideration the following list: 
                            <table> 
                              <tr> 
                                <th>Round</th>
                                <th>Past Demand</th>

                              </tr> 
                                <td>{0}</td>
                                <td>{1}</td>
                                <td>{2}</td>
                              </tr>
                              </tr> 
                                <td>{3}</td>
                                <td>{4}</td>
                                <td>{5}</td>
                              </tr>

                            </table><br/> 
                            This table shows you what will happen assuming you order {6} now. Assuming the factory can meet your demands, you will receive that order in {7} periods. As the demand is  constant, you will only be able to meet {8} %% of the demand, meaning you will have a backorder of {9} items. <br/> 
                            This means your costs will increase by {10} of additional costs in period {7}.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) How much should I order? <br/>
                            (2) What happens if I order ...? <br/>
                            (3) Nothing else. """,
                    "equal":  """This is exactly the amount I would recommend to order.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) How much should I order? <br/>
                            (2) What happens if I order ...? <br/>
                            (3) Nothing else. """,
                },
                1: "suggestion",
                2: "userEstimate",
                3: "end",
            },
            "factory" : {
                0:{
                    "more": """Please take into consideration the following list: 
                            <table> 
                              <tr> 
                                <th>Round</th>
                                <th>Past Demand</th>
                              </tr> 
                                <td>{0}</td>
                                <td>{1}</td>
                                <td>{2}</td>
                              </tr>
                              </tr> 
                                <td>{3}</td>
                                <td>{4}</td>
                                <td>{5}</td>
                              </tr>

                            </table><br/> 
                            This table shows you what will happen assuming you produce {6} now. <br/> 
                            This will mean you will receive these products in {7} periods. <br/> 
                            If the retailer's demand remains the same on average, then your inventory increased in {7} periods by {8} items. <br/> 
                            This means your costs will increase by {9} of additional costs in period {7}.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) How much should I order? <br/>
                            (2) What happens if I order ...? <br/>
                            (3) Nothing else. """,
                    "less": """Please take into consideration the following list: 
                            <table> 
                              <tr> 
                                <th>Round</th>
                                <th>Past Demand</th>
                              </tr> 
                                <td>{0}</td>
                                <td>{1}</td>
                                <td>{2}</td>
                              </tr>
                              </tr> 
                                <td>{3}</td>
                                <td>{4}</td>
                                <td>{5}</td>
                              </tr>
                            </table><br/> 
                            This table shows you what will happen assuming you produce {6} now.<br/> 
                            This will mean you will receive these products in {7} periods. If the retailer's demand remains the same on average, you will only be able to meet {8} %% of the demand. <br/>  
                            Meaning you will have a backorder of {9} items. This means your costs will increase by {10} of additional costs in period {7}.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) How much should I order? <br/>
                            (2) What happens if I order ...? <br/>
                            (3) Nothing else. """,
                    "equal":  """This is exactly the amount I would recommend to order.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) How much should I order? <br/>
                            (2) What happens if I order ...? <br/>
                            (3) Nothing else. """,
                },
                1: "suggestion",
                2: "userEstimate",
                3: "end",
            },

        },
        "deviate": {
            "retailer" : {
                0: {
                    "more":  """If you deviate and order more than I suggested, than the factory has to produce more products.<br/>
                    Assuming that the factory produces your complete order, you will receive {0} in {1} periods and will have an additional inventory of {2}. This means your costs for
                    keeping products in the inventory will increase by €0.50 per item per period. Summing to {3} for additional costs in {1} periods. <br/>
                    If you do not order less in the following periods, these costs will accumulate over the next periods. Remember the customers' demand is constant, thus, will not increase.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) Explain why? <br/>
                            (2) What happens if I order ... ? <br/>
                            (3) Nothing else.""",
                    "less": """If you deviate and order less than I suggested, then the customers' demands cannot be met in {1} periods. Assuming that the factory produces your complete order, you will receive {0} in {1} periods.<br/>
                    As the customers' demand remains constant, their demand will be {2} in this period. Thus, you will have backorders of {3} until you can meet the demands. This means your costs for backorders will increase by €1,00 per
                    item per period. Summing to {4} for additional costs period {1}. If you do not order more in the following periods, these costs will accumulate over the next periods. <br/>
                    Remember the customers' demand is constant thus, will not decrease.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) Explain why? <br/>
                            (2) What happens if I order ... ? <br/>
                            (3) Nothing else.""",
                    "equal": """You did not not deviate at all from my suggestion. I would recommend to order {0}. <br/> <br/> 
                            How can I help you next?<br/>
                            (1) Explain why? <br/>
                            (2) What happens if I order ... ? <br/>
                            (3) Nothing else. """,
                },
                1: "explain",
                2: "deviate",
                3: "end",
            },
            "factory" : {
                0:{
                    "more": """If you deviate and order more than I suggested, than you will receive {0} produced products in {1} periods. <br/> 
                    If the retailer's demand remains at {2} then and will have an additional inventory of {3}. This means your costs for keeping products in the inventory will increase by €0.50 per item per period. <br/> 
                    Summing to {4} for additional costs in {1} periods. If you do not produce less in the following periods, these costs will accumulate over the next periods.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) Explain why? <br/>
                            (2) What happens if I order ... ? <br/>
                            (3) Nothing else. """ ,
                    "less": """If you deviate and order less than I suggested, then you will receive {0} in {1} periods. If the retailer's demand remains at {2} then you will not be able to meet all their demand and have backorders of {3}. <br/> 
                    This means your costs for backorders will increase by €1,00 per item per period. Summing to {4} for additional costs in {1} periods. If you do not order more in the following periods, these costs will accumulate over the next periods.<br/> <br/> 
                            How can I help you next?<br/>
                            (1) Explain why? <br/>
                            (2) What happens if I order ... ? <br/>
                            (3) Nothing else. """,
                    "equal": """You did not not deviate at all from my suggestion. I would recommend to order {0}. <br/> <br/> 
                            How can I help you next?<br/>
                            (1) Explain why? <br/>
                            (2) What happens if I order ... ? <br/>
                            (3) Nothing else. """,
                },
                1: "explain",
                2: "deviate",
                3: "end",
            },
        },
        "userInputRequest": {
            0: "Please enter your suggested value:" ,
        },
        "error": {
            0: "Sorry, but I did not understand this. Please enter one of the numbers described above without entering any other character. To restart please enter (1)",
            1: "start",
        }
    }