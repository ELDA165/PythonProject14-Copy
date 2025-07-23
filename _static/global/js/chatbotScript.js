let user_input = document.getElementById('user_input');
let chatMessages = document.getElementById('chatMessages');
let chatbotButton = document.getElementById('chatbot-button')
let chatContainer= document.getElementById('chatContainer');

chatbotButton.addEventListener('click', function(event) {
  if (chatContainer.style.display === 'block'){
    chatContainer.style.display = 'none';
    submit_Reset();
  } else {
    chatContainer.style.display = 'block';
    // setDss Button to true
    submit_ButtonClicked();
  }
});


user_input.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
      submit_msg();
  }
});

function submit_msg() {
  let messageElement = document.createElement('p');
  messageElement.classList.add('chatbotMessage', 'userInput');
  messageElement.textContent = user_input.value;
  chatMessages.appendChild(messageElement);
  //chatContainer.innerHTML += `<p class="chatbotMessage">${user_input.value}</p>`;

  //sent input to live_method
  liveSend({'user_input': user_input.value});
  //reset so that input box is empty
  user_input.value = '';

  //scroll to bottom of chat container
  chatMessages.scrollTop = chatContainer.scrollHeight;
  //add new css class so that user message has a different colour in box
  messageElement.classList.add('user-input-message');
}

function submit_ButtonClicked(){
  liveSend({'user_input': "clicked"});
}
function submit_Reset(){
  liveSend({'user_input': "reset"});
  //clear chatMessages:
  chatMessages.innerHTML = "";
  user_input = "";

  //show start message:
  const startMessage = document.createElement('p');
  startMessage.textContent = "Hello. If you want a suggestion what to order, I am here to help. <br/> <br/> Just enter one of the following numbers:<br/>(1) No, thanks.<br/>(2) Tell me how much to order!<br/>(3) Explain how I should order the order quantity!";
  startMessage.classList.add('start-message', 'chatbotResponse');

  //append start message to message container
  chatMessages.append(startMessage);

}

// list of chat messages as JSON dictionaries
var chatLogData = [];

// timestamp of page loading to determine when messages were sent
var timeBase = Date.now();

// adapting chat from oTree snippets page
var chat_input = document.getElementById('chat_input');

// function to log chat
function logChat(sender, chatText) {
  let timestamp = (Date.now() - timeBase) / 1000;

  // create dictionary for current message info
  var currentMsg = {
      sender: sender,
      text: chatText,
      timestamp: timestamp
  };

  // append chatLogData
  chatLogData.push(currentMsg);

  // write chatLog to input field
  document.getElementById('id_chatLog').value = JSON.stringify(chatLogData);
}


function liveRecv(data) {
  if (!data["bot_response"] || data["bot_response"].trim() === "") {
    return;
  }
  console.log(data, data["bot_response"])
  let messageElement = document.createElement('div');
  messageElement.classList.add('chatbotMessage', 'chatbotResponse');
  //messageElement.textContent = data["bot_response"];
  messageElement.innerHTML = data["bot_response"];
  chatMessages.appendChild(messageElement);
  //chatContainer.innerHTML += `<p class="chatbotMessage">${data["bot_response"]}</p>`;

  //scroll to bottom of chat container
  chatMessages.scrollTop = chatContainer.scrollHeight;

  // append chat log
  logChat('Bot', data)
}