import { createElement, formatMessage, scrollToBottom } from './utils.js';
// Use global marked instance
const { marked } = window;

export class UI {
    constructor() {
        this.chatBox = document.getElementById('chat-messages');
        this.chatContainer = document.querySelector('.chat-container');
        this.header = document.querySelector('.header');
        this.userInput = document.getElementById('user-input');
        this.inputSection = document.querySelector('.input-section');
        this.examplePrompts = document.querySelector('.example-prompts');
        this.mainContent = document.querySelector('.main-content');
        
        this.setupEventListeners();
    }

    setPrompt(text) {
        this.userInput.value = text;
        this.userInput.focus();
    }

    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.clearChat();
            }
        });

        // Input handlers
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleEnterPress();
            }
        });

        // New Chat button handler
        const newChatBtn = document.getElementById('new-chat-btn');
        newChatBtn.addEventListener('click', () => {
            if (this.chatBox.children.length > 0) {
                this.showWarning(
                    'Are you sure you want to start a new chat? This will clear your current conversation.',
                    () => this.clearChat(), // On confirm
                    () => {} // On cancel (do nothing)
                );
            } else {
                this.clearChat();
            }
        });
    }

    clearChat() {
        this.chatBox.innerHTML = '';
        this.userInput.value = '';
        
        // Remove chat state classes
        document.body.classList.remove('with-chat');
        this.chatContainer.classList.remove('visible');
        
        // Show example prompts with a slight delay to allow for transitions
        setTimeout(() => {
            this.examplePrompts.classList.remove('hidden');
            // Force a reflow to ensure the transition works
            void this.examplePrompts.offsetHeight;
            this.examplePrompts.style.opacity = '1';
            this.examplePrompts.style.visibility = 'visible';
        }, 300);
    }

    clearInput() {
        this.userInput.value = '';
        this.appendMessage('Message cleared.', 'warning-message');
    }

    appendMessage(message, type, scroll = true, messageId = null) {
        console.log('Appending message:', { message, type, messageId });
        
        // Ensure chat container is visible and force a reflow
        if (!this.chatContainer.classList.contains('visible')) {
            this.showChatContainer();
            void this.chatContainer.offsetHeight;
        }

        const messageDiv = createElement('div', {
            className: `message ${type} ${type === 'warning-message' ? 'warning-highlight' : ''}`,
            id: messageId ? `message-${messageId}` : null
        });

        // Create message content with markdown rendering and icon for warnings
        const messageContent = createElement('div', {
            className: 'message-content'
        });

        if (type === 'warning-message') {
            // Choose appropriate icon based on message content
            let iconClass = 'fa-circle-info';
            if (message.toLowerCase().includes('confirm') || message.includes('?')) {
                iconClass = 'fa-circle-question';
            } else if (message.toLowerCase().includes('warning') || message.toLowerCase().includes('caution')) {
                iconClass = 'fa-triangle-exclamation';
            } else if (message.toLowerCase().includes('error') || message.toLowerCase().includes('failed')) {
                iconClass = 'fa-circle-exclamation';
            }

            const icon = createElement('i', {
                className: `warning-icon fa-solid ${iconClass}`
            });
            messageContent.appendChild(icon);
        }

        const textContent = createElement('div', {
            innerHTML: window.marked.parse(message)
        });
        messageContent.appendChild(textContent);

        // Add copy button for non-loading messages
        const copyButton = createElement('button', {
            className: 'copy-button',
            innerHTML: `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M8 4v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7.242a2 2 0 0 0-.602-1.43L16.083 2.57A2 2 0 0 0 14.685 2H10a2 2 0 0 0-2 2z" stroke-width="2"/>
                    <path d="M16 18v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h2" stroke-width="2"/>
                </svg>
                <span>Copy</span>
            `,
            title: 'Copy message'
        });

        copyButton.addEventListener('click', (e) => {
            e.stopPropagation();
            navigator.clipboard.writeText(message).then(() => {
                copyButton.classList.add('copied');
                copyButton.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M20 6L9 17l-5-5" stroke-width="2"/>
                    </svg>
                    <span>Copied!</span>
                `;
                setTimeout(() => {
                    copyButton.classList.remove('copied');
                    copyButton.innerHTML = `
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M8 4v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7.242a2 2 0 0 0-.602-1.43L16.083 2.57A2 2 0 0 0 14.685 2H10a2 2 0 0 0-2 2z" stroke-width="2"/>
                            <path d="M16 18v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h2" stroke-width="2"/>
                        </svg>
                        <span>Copy</span>
                    `;
                }, 2000);
            });
        });

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(copyButton);
        this.chatBox.appendChild(messageDiv);

        if (scroll) {
            if (type === 'warning-message') {
                // Ensure warning is visible in viewport
                messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                // Add fade-in animation
                setTimeout(() => {
                    messageDiv.classList.add('warning-fade-in');
                }, 0);
            } else {
                scrollToBottom(this.chatBox);
            }
        }

        return messageDiv;
    }

    highlightRelatedMessages(messageId) {
        // Remove previous highlights
        this.chatBox.querySelectorAll('.message.highlighted').forEach(msg => {
            msg.classList.remove('highlighted');
        });
        
        // Add highlight to clicked message and its context
        const messages = this.chatBox.querySelectorAll('.message[data-message-id]');
        messages.forEach(msg => {
            if (msg.dataset.messageId === messageId) {
                msg.classList.add('highlighted');
                // Scroll into view if needed
                msg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }

    showLoading() {
        const loadingDiv = createElement('div', {
            className: 'typing-indicator',
            innerHTML: `
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            `
        });
        this.chatBox.appendChild(loadingDiv);
        // Force a reflow to trigger animation
        void loadingDiv.offsetHeight;
        loadingDiv.classList.add('visible');
        scrollToBottom(this.chatBox);
        return loadingDiv;
    }

    showLoadingMore() {
        const loadingDiv = createElement('div', 'loading loading-more');
        loadingDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="animate-spin">
                    <path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2Z"/>
                </svg>
                Loading more messages...
            </div>
        `;
        this.chatBox.insertBefore(loadingDiv, this.chatBox.firstChild);
        return loadingDiv;
    }

    hideLoadingMore() {
        const loadingMore = this.chatBox.querySelector('.loading-more');
        if (loadingMore) {
            loadingMore.remove();
        }
    }

    showError(message) {
        const errorDiv = createElement('div', 'message warning-message animate-in');
        errorDiv.textContent = message;
        this.chatBox.appendChild(errorDiv);
        scrollToBottom(this.chatBox);
        
        // Auto-remove error after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    showChatContainer() {
        if (!this.chatContainer.classList.contains('visible')) {
            console.log('Showing chat container');
            
            // Add with-chat class to body immediately
            document.body.classList.add('with-chat');
            
            // Hide example prompts immediately
            this.examplePrompts.classList.add('hidden');
            this.examplePrompts.style.opacity = '0';
            this.examplePrompts.style.visibility = 'hidden';
            
            // Force a reflow
            void this.chatContainer.offsetHeight;
            
            // Show chat container and main content
            this.chatContainer.classList.add('visible');
            this.mainContent.classList.add('visible');
            
            console.log('Chat container shown');
        }
    }

    clearChat() {
        this.chatBox.innerHTML = '';
        this.userInput.value = '';
        
        // Remove chat state classes
        document.body.classList.remove('with-chat');
        this.chatContainer.classList.remove('visible');
        this.mainContent.classList.remove('visible');
        
        // Show example prompts with a slight delay to allow for transitions
        setTimeout(() => {
            this.examplePrompts.classList.remove('hidden');
            // Force a reflow to ensure the transition works
            void this.examplePrompts.offsetHeight;
            this.examplePrompts.style.opacity = '1';
            this.examplePrompts.style.visibility = 'visible';
        }, 300);
    }

    getInputValue() {
        return this.userInput.value;
    }

    setInputValue(value) {
        this.userInput.value = value;
    }

    handleEnterPress() {
        const event = new CustomEvent('send-message');
        document.dispatchEvent(event);
    }

    showWarning(message, onConfirm, onCancel) {
        const warningDiv = createElement('div', {
            className: 'message warning-message warning-highlight'
        });

        const messageContent = createElement('div', {
            className: 'message-content'
        });

        const icon = createElement('i', {
            className: 'warning-icon fa-solid fa-circle-question'
        });

        const textContent = createElement('div', {
            innerHTML: message
        });

        messageContent.appendChild(icon);
        messageContent.appendChild(textContent);

        const actionsDiv = createElement('div', {
            className: 'warning-actions',
            innerHTML: `
                <button class="confirm-button">Yes, proceed</button>
                <button class="cancel-button">No, cancel</button>
            `
        });

        warningDiv.appendChild(messageContent);
        warningDiv.appendChild(actionsDiv);

        const confirmButton = warningDiv.querySelector('.confirm-button');
        const cancelButton = warningDiv.querySelector('.cancel-button');

        confirmButton.addEventListener('click', () => {
            warningDiv.remove();
            onConfirm();
        });

        cancelButton.addEventListener('click', () => {
            warningDiv.remove();
            onCancel();
        });

        this.chatBox.appendChild(warningDiv);
        
        // Ensure warning is visible
        warningDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Add attention-grabbing animation
        setTimeout(() => {
            warningDiv.classList.add('warning-fade-in');
        }, 0);
    }
}

export const ui = new UI();
