import { ui } from './ui.js';
import { chat } from './chat.js';

class App {
    constructor() {
        this.ui = ui;
        this.chat = chat;
        this.init();
        this.showToast();
    }

    init() {
        // Add button click handlers
        document.querySelector('button[onclick="sendMessage()"]')
            .onclick = () => {
                this.chat.sendMessage();
            };
        
        document.querySelector('button[onclick="clearChat()"]')
            .onclick = () => this.chat.clearChat();

        // Add example prompt handlers
        window.setPrompt = (text) => {
            this.ui.setPrompt(text);
            this.chat.sendMessage();
        };
    }

    showToast() {
        // Show toast notification if not shown before
        if (!localStorage.getItem('smsToastShown')) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `
                <p>Text JANE at <strong>850-498-1386</strong></p>
                <button onclick="this.parentElement.remove(); localStorage.setItem('smsToastShown', 'true')">&times;</button>
            `;
            document.body.appendChild(toast);
            
            // Auto-hide after 10 seconds
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                    localStorage.setItem('smsToastShown', 'true');
                }
            }, 10000);
        }
    }

}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
