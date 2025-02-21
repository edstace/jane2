import { ui } from './ui.js';
import { chat } from './chat.js';

class App {
    constructor() {
        this.ui = ui;
        this.chat = chat;
        this.init();
    }

    init() {
        // Add button click handlers
        document.querySelector('button[onclick="sendMessage()"]')
            .onclick = () => this.chat.sendMessage();
        
        document.querySelector('button[onclick="clearChat()"]')
            .onclick = () => this.chat.clearChat();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
