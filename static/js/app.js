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

        // Add click handlers for example prompts
        document.querySelectorAll('.prompt-button').forEach(button => {
            button.addEventListener('click', () => {
                const promptText = button.querySelector('span').textContent;
                ui.setPrompt(promptText);
                // Trigger send message after setting prompt
                window.sendMessage();
            });
        });

        // Add Enter key handler
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('Enter key pressed');
                window.sendMessage();
            }
        });

        // Add form submit handler
        document.getElementById('chat-form').addEventListener('submit', (e) => {
            e.preventDefault();
            window.sendMessage();
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
