import { ui } from './ui.js';
import { chat } from './chat.js';

class App {
    constructor() {
        this.ui = ui;
        this.chat = chat;
        this.init();
    }

    init() {
        // Add global handlers for buttons
        window.sendMessage = () => {
            console.log('Send button clicked');
            const event = new CustomEvent('send-message');
            document.dispatchEvent(event);
        };
        
        window.clearChat = () => chat.clearChat();

        // Add example prompt handlers
        window.setPrompt = (text) => {
            ui.setInputValue(text);
            ui.userInput.focus();
        };

        // Add Enter key handler
        document.getElementById('userInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('Enter key pressed');
                window.sendMessage();
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
