from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, QUrl, QObject, pyqtSignal
from datetime import datetime
from pathlib import Path
import json

class HtmlManager(QObject):
    """
    Manages the chat interface display using QWebEngineView.
    Handles message bubbles with proper threading and queuing.
    """
    
    # Signal to safely add messages from non-main threads
    add_message_signal = pyqtSignal(dict)

    def __init__(self, window):
        """
        Initializes the chat interface.
        
        Args:
            window: The parent QWidget window
        """
        super().__init__()
        
        # Message queue and execution state
        self.bubblesToCreate = []      # Queue of pending messages
        self.isJsTaskRunning = False   # Prevents concurrent JavaScript execution
        
        # Initialize WebEngine view
        self.chat_area = QWebEngineView(window)
        
        # =============================================
        # HTML/CSS Setup
        # =============================================
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
                margin: 0;
                padding: 10px;
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
                margin: 10px;
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
        
        # Connect signal to message handler
        self.add_message_signal.connect(self._process_message_queue)
        self.chat_area.reload()

    # =============================================
    # Public Interface
    # =============================================
    def addMessageBubble(self, sender, msg, left=True, addToList=True):
        """
        Adds a message bubble to the chat interface.
        
        Args:
            sender: Name of the message sender
            msg: Message content (HTML-safe)
            left: True for left-aligned (received), False for right-aligned (sent)
            addToList: Whether to queue the message or process immediately
        """
        if addToList:
            self.bubblesToCreate.append({
                "sender": sender,
                "msg": msg,
                "left": left
            })

        # Trigger message processing
        self.add_message_signal.emit({})

    # =============================================
    # Message Processing
    # =============================================
    def _process_message_queue(self):
        """Processes the next message in the queue if not already running."""
        if not self.bubblesToCreate or self.isJsTaskRunning:
            return

        self.isJsTaskRunning = True
        message = self.bubblesToCreate.pop(0)

        # Generate message HTML
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bubble = f"""
            <div class="sender">{message['sender']}</div>
            <div class="message">{message['msg']}</div>
            <div class="timestamp">{timestamp}</div>
        """
        alignment_class = "left" if message['left'] else "right"

        # JavaScript to inject the message
        js_script = f"""
            (function() {{
                var chat = document.getElementById('chat');
                if (!chat) {{
                    console.error('Chat container not found');
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

        def handle_js_result(result):
            """Callback after JavaScript execution completes"""
            self.isJsTaskRunning = False
            if self.bubblesToCreate:
                # Process next message after slight delay
                QTimer.singleShot(0, self._process_message_queue)

        # Execute the JavaScript
        self.chat_area.page().runJavaScript(js_script, handle_js_result)