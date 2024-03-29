class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
          var textField = chatbox.querySelector('input');
          let text1 = textField.value
          if (text1 === "") {
            return;
          }

          let msg1 = { name: "User", message: text1 }
          this.messages.push(msg1);
          let endpoint = this.useFallback ? 'http://127.0.0.1:5000/fallback' : 'http://127.0.0.1:5000/predict';
          fetch(endpoint, {
              method: 'POST',
              body: JSON.stringify({ message: text1 }),
              mode: 'cors',
              headers: {
                'Content-Type': 'application/json'
              },
            })
            .then(r => r.json())
            .then(r => {
              let msg2 = { name: "Carol", message: r.answer };
              this.messages.push(msg2);
              this.updateChatText(chatbox)
              textField.value = ''
              if (msg2.message.startsWith('Desculpe')){
                this.useFallback = true;
                this.waitForUserInput(chatbox);
              } else {
                this.useFallback = false;
              }
            }).catch((error) => {
              console.error('Error:', error);
              this.updateChatText(chatbox)
              textField.value = ''
            });
    }

    waitForUserInput(chatbox) {
            var textField = chatbox.querySelector('input');
            textField.value = '';
            textField.placeholder = "Digite sua mensagem correta aqui e pressione Enter";
            const handleKeyDown = (event) => {
                if (event.key === 'Enter') {
                    let text2 = textField.value;
                    let msg3 = { name: "User", message: text2 }
                    this.messages.push(msg3);
                    let endpoint = this.useFallback ? 'http://127.0.0.1:5000/fallback' : 'http://127.0.0.1:5000/predict';
                    fetch(endpoint, {
                        method: 'POST',
                        body: JSON.stringify({ message: text2 }),
                        mode: 'cors',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                    })
                    .then(r1 => r1.json())
                    .then(r1 => {
                        let msg4 = { name: "Carol", message: r1.answer };
                        this.messages.push(msg4);
                        this.updateChatText(chatbox);
                        textField.value = '';
                        textField.placeholder = "Digite aqui..."
                        if (msg4.message.startsWith('Desculpe')){
                            this.useFallback = true;
                            this.waitForUserInput(chatbox);
                        } else {
                            this.useFallback = false;
                        }
                        textField.removeEventListener('keydown', handleKeyDown); // remove event listener
                    }).catch((error) => {
                        console.error('Error:', error);
                        this.updateChatText(chatbox);
                        textField.value = '';
                    })
                }
            };
            textField.addEventListener('keydown', handleKeyDown);
        }



    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Carol")
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
          });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}

fetch('/check_tutor')
    .then(response => response.json())
    .then(data => {
        if (data.is_tutor) {
            document.querySelector('.form-link').style.display = 'block';
        }
    });

const chatbox = new Chatbox();
chatbox.display();
