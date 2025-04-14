from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, QUrl
from datetime import datetime
from pathlib import Path
import json

class HtmlManager():

    def __init__(self, window):
        self.bubblesToCreate = []
        self.isJsTaskRunning = False
        self.chat_area = QWebEngineView(window)

        # Define the base URL with the absolute project directory path
        project_dir = Path(__file__).resolve().parent
        base_url = QUrl.fromLocalFile(str(project_dir) + "/")

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
                overflow-wrap: break-word;
            }
            .message img {
                max-width: 100%;
                max-height: 100%;
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
        """, base_url)
        # Add this inside chat-container if you want to test images :
        # <div class="message-container left">
        #     <div class="sender">Bastien Marthe</div>
        #     <div class="message"><img src="img/isc-logo.png"></div>
        #     <div class="timestamp">02/04/2025</div>
        # </div>
        self.chat_area.reload()

    def addMessageBubble(self, sender, msg, left=True, addToList=True):
        if addToList:
            self.bubblesToCreate.append({"sender": sender, "msg": msg, "left": left})

        if self.isJsTaskRunning == False:
            print("no js task running")
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
                print("js task launched")
                # Run JavaScript after a slight delay to ensure proper state
                self.chat_area.page().runJavaScript(js_script)
                print("js task finished")
                self.isJsTaskRunning = False
                # delete the bubble that has been created from the list and creates the other ones if there are any
                del self.bubblesToCreate[0]
                if len(self.bubblesToCreate) != 0:
                    self.addMessageBubble(
                        self.bubblesToCreate[0]["sender"],
                        self.bubblesToCreate[0]["msg"],
                        left=self.bubblesToCreate[0]["left"],
                        addToList=False)

            # Always run this from the Qt main thread
            print("timer launched")
            QTimer.singleShot(0, lambda: QTimer.singleShot(100, run_js_with_delay))