import { ui } from './ui.js';
import { chat } from './chat.js';

class App {
    constructor() {
        this.ui = ui;
        this.chat = chat;
        this.init();
        this.showToast();
        this.setupChatVisibility();
    }

    init() {
        // Add button click handlers
        document.querySelector('button[onclick="sendMessage()"]')
            .onclick = () => {
                this.chat.sendMessage();
                this.showChatContainer();
            };
        
        document.querySelector('button[onclick="clearChat()"]')
            .onclick = () => this.chat.clearChat();
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

    setupChatVisibility() {
        // Hide chat container initially
        const chatContainer = document.querySelector('.chat-container');
        const welcomeContainer = document.querySelector('.welcome-container');
        const inputArea = document.querySelector('.input-area');
        
        // Show if there are existing messages
        if (document.querySelector('.message')) {
            welcomeContainer.style.display = 'none';
            this.showChatContainer();
        }
    }

    showChatContainer() {
        const chatContainer = document.querySelector('.chat-container');
        const welcomeContainer = document.querySelector('.welcome-container');
        const inputArea = document.querySelector('.input-area');
        const inputContainer = inputArea.querySelector('.input-container');
        
        // Fade out welcome screen
        welcomeContainer.style.opacity = '0';
        welcomeContainer.style.transition = 'opacity 0.3s ease';
        
        setTimeout(() => {
            welcomeContainer.style.display = 'none';
            
            // Show chat container
            chatContainer.style.display = 'flex';
            setTimeout(() => {
                chatContainer.classList.add('visible');
                inputContainer.classList.add('with-chat');
                inputArea.classList.add('with-chat');
            }, 50);
        }, 300);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
