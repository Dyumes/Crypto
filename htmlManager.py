from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer
from datetime import datetime
from time import sleep
import json

class HtmlManager():

    def __init__(self, window):
        self.bubblesToCreate = []
        self.isJsTaskRunning = False
        self.chat_area = QWebEngineView(window)
        self.chat_area.setHtml("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                height: 100%;
                background-color: #f0f2f5;
            }
            .chat-container {
                width: 100%;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .message-container {
                max-width: 80%;
                display: flex;
                flex-direction: column;
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                position: relative;
                margin: 20px, 10px, 0px, 10px;
            }
            .message-container.left {
                align-self: flex-start;
                background: #e4e6eb;
                color: black;
            }
            .message-container.right {
                align-self: flex-end;
                background: #0084ff;
                color: white;
            }
            .sender {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .message {
                margin-bottom: 5px;
            }
            .timestamp {
                font-size: 12px;
                opacity: 0.8;
                text-align: right;
            }
            </style>
        </head>
        <body>
            <div id="chat" class="chat-container"></div>
        </body>
        </html>
        """)

    def addMessageBubble(self, sender, msg, left=True, addToList=True):
        if addToList:
            self.bubblesToCreate.append({"sender": sender, "msg": msg, "left": left})

        if self.isJsTaskRunning == False:
            self.isJsTaskRunning = True
            # Ensure chat_area.page() exists
            if not self.chat_area.page():
                print("Error: chat_area.page() is None")
                return

            # HTML content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bubble = f"""
                <div class="sender">{sender}</div>
                <div class="message">{msg}</div>
                <div class="timestamp">{timestamp}</div>
            """
            # Message alignment
            alignment_class = "left" if left else "right"

            # JavaScript to insert the message safely
            js_script = f"""
                (function() {{
                    var chat = document.getElementById('chat');
                    if (!chat) {{
                        return;
                    }}

                    var container = document.createElement('div');
                    container.classList.add('message-container', '{alignment_class}');
                    container.innerHTML = {json.dumps(bubble)};
                    chat.appendChild(container);
                    window.scrollTo(0, document.body.scrollHeight);

                    return "Success";
                }})();
            """

            def run_js_with_delay():
                # Run JavaScript after a slight delay to ensure proper state
                self.chat_area.page().runJavaScript(js_script)
                self.isJsTaskRunning = False
                # delete the bubble that has been created from the list and creates the other ones if there are any
                del self.bubblesToCreate[0]
                if len(self.bubblesToCreate) != 0:
                    self.addMessageBubble(
                        self.bubblesToCreate[0]["sender"],
                        self.bubblesToCreate[0]["msg"],
                        left=self.bubblesToCreate[0]["left"],
                        addToList=False)

            # Run the JS script with a slight delay to prevent overlap
            QTimer.singleShot(100, run_js_with_delay)  # 100ms delay