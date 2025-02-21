import { ui } from './ui.js';
import { chat } from './chat.js';

class App {
    constructor() {
        this.ui = ui;
        this.chat = chat;
        this.init();
        this.showSMSPopup();
    }

    init() {
        // Add button click handlers
        document.querySelector('button[onclick="sendMessage()"]')
            .onclick = () => this.chat.sendMessage();
        
        document.querySelector('button[onclick="clearChat()"]')
            .onclick = () => this.chat.clearChat();
    }

    showSMSPopup() {
        // Show SMS popup if not shown before
        if (!localStorage.getItem('smsPopupShown')) {
            const popup = document.createElement('div');
            popup.className = 'sms-popup';
            popup.innerHTML = `
                <div class="sms-popup-content">
                    <h3>Text JANE</h3>
                    <p>You can also text JANE at <strong>850-498-1386</strong></p>
                    <button onclick="this.parentElement.parentElement.remove(); localStorage.setItem('smsPopupShown', 'true')">Got it!</button>
                </div>
            `;
            document.body.appendChild(popup);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
