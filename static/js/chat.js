import { ui } from './ui.js';
import { handleError } from './utils.js';
import { MessageHistory } from './message_history.js';

export class Chat {
    constructor() {
        this.pendingMessage = '';
        this.loading = false;
        this.history = new MessageHistory(20); // Keep last 20 messages for context
        this.setupEventListeners();
        this.showWelcomeMessage();
    }

    showWelcomeMessage() {
        ui.appendMessage(
            'Hello! I\'m JANE, your Job Assistance and Navigation Expert. How can I help you today?',
            'bot-message'
        );
    }

    saveHistory() {
        try {
            localStorage.setItem('chat_history', JSON.stringify(this.history.toJSON()));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    setupEventListeners() {
        document.addEventListener('send-message', () => {
            this.sendMessage();
        });
    }

    setupInfiniteScroll() {
        // Disable infinite scroll to prevent loading old messages
        return;
    }

    // Remove loadMoreMessages method since we're not using infinite scroll

    renderMessages() {
        const chatBox = document.getElementById('chatBox');
        chatBox.innerHTML = '';
        this.history.getMessages().forEach(msg => {
            ui.appendMessage(msg.content, msg.type, false, msg.id);
        });
    }

    async sendMessage(confirmed = false) {
        const message = confirmed ? this.pendingMessage : ui.getInputValue();
        
        if (message === '') return;
        
        try {
            if (!confirmed) {
                const msgId = this.history.addMessage(message, 'user-message').id;
                ui.appendMessage(message, 'user-message', true, msgId);
                this.pendingMessage = message;
                ui.setInputValue('');
            }
            
            const loadingDiv = ui.showLoading();
            const response = await this.sendToServer(message, confirmed);
            loadingDiv.remove();

            if (response.requiresConfirmation && !confirmed) {
                ui.showWarning(
                    response.warning,
                    () => this.sendMessage(true),
                    () => ui.clearInput()
                );
                return;
            }

            this.pendingMessage = '';
            
            if (response.warning) {
                const warningId = this.history.addMessage(response.warning, 'warning-message').id;
                ui.appendMessage(response.warning, 'warning-message', true, warningId);
            }
            if (response.response) {
                const botMsgId = this.history.addMessage(response.response, 'bot-message').id;
                ui.appendMessage(response.response, 'bot-message', true, botMsgId);
            }
            
            // Save updated history
            this.saveHistory();
        } catch (error) {
            ui.appendMessage(handleError(error), 'warning-message');
        }
    }

    async sendToServer(message, confirmed) {
        // Get context messages
        const context = this.history.getContextMessages(5).map(msg => ({
            role: msg.type === 'user-message' ? 'user' : 'assistant',
            content: msg.content
        }));
        // Get CSRF token from meta tag
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ 
                message, 
                confirmed,
                context,
                timestamp: new Date().toISOString()
            }),
            credentials: 'same-origin' // Required for CSRF
        });
        
        if (!response.ok) {
            if (response.status === 429) {
                throw new Error('Rate limit exceeded. Please wait before sending more messages.');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    async clearChat() {
        try {
            // Clear Redis cache
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            const response = await fetch('/clear-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error('Failed to clear chat history');
            }

            // Clear local state
            this.history.clear();
            localStorage.removeItem('chat_history');
            ui.clearChat();
            this.showWelcomeMessage();
        } catch (error) {
            console.error('Error clearing chat:', error);
            ui.showError('Failed to clear chat history');
        }
    }
}

// Initialize chat
export const chat = new Chat();

// Add global handlers for buttons
window.handleSendMessage = () => chat.sendMessage();
window.handleClearChat = () => chat.clearChat();
