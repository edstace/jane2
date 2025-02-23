import { ui } from './ui.js';
import { chat } from './chat.js';

// Initialize global functions first
window.sendMessage = () => {
    console.log('Send button clicked');
    const event = new CustomEvent('send-message');
    document.dispatchEvent(event);
};

class App {
    constructor() {
        this.ui = ui;
        this.chat = chat;
        this.init();
    }

    init() {
        
        window.clearChat = () => chat.clearChat();

        // Add example prompt handlers
        window.setPrompt = (text) => {
            ui.setInputValue(text);
            ui.userInput.focus();
        };

        // Add click handlers for example prompts
        document.querySelectorAll('.prompt-button').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const promptText = button.querySelector('span').textContent;
                ui.setPrompt(promptText);
                // Add a small delay before sending to ensure the input is set
                setTimeout(() => {
                    window.sendMessage();
                }, 50);
            });
        });

        // Add Enter key handler
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('Enter key pressed');
                window.sendMessage();
            }
        });

        // Add form submit handler
        document.getElementById('chat-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const event = new CustomEvent('send-message');
            document.dispatchEvent(event);
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
