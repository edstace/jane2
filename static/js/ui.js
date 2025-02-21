import { createElement, formatMessage, scrollToBottom } from './utils.js';

export class UI {
    constructor() {
        this.chatBox = document.getElementById('chatBox');
        this.chatContainer = document.getElementById('chatContainer');
        this.header = document.getElementById('header');
        this.userInput = document.getElementById('userInput');
        this.charCounter = document.querySelector('.char-counter');
        this.inputSection = document.querySelector('.input-section');
        this.examplePrompts = document.querySelector('.example-prompts');
        
        this.setupEventListeners();
        this.toastTimeout = null;
    }

    setPrompt(text) {
        this.userInput.value = text;
        this.updateCharCount();
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
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleEnterPress();
            }
        });

        this.userInput.addEventListener('input', () => {
            this.updateCharCount();
        });
    }

    updateCharCount() {
        this.charCounter.textContent = `${this.userInput.value.length}/500`;
    }

    clearChat() {
        this.chatBox.innerHTML = '';
        this.userInput.value = '';
        this.updateCharCount();
        
        // Remove chat state classes
        document.body.classList.remove('with-chat');
        this.chatContainer.classList.remove('visible');
        this.examplePrompts.classList.remove('hidden');
    }

    clearInput() {
        this.userInput.value = '';
        this.updateCharCount();
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
            className: `message ${type}`,
            id: messageId ? `message-${messageId}` : null
        });

        // Create message content with text directly
        const messageContent = createElement('div', {
            className: 'message-content',
            textContent: message
        });

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
            scrollToBottom(this.chatBox);
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
            
            // Reset any inline styles
            this.chatContainer.style.cssText = '';
            
            // Add with-chat class to body first to trigger layout changes
            document.body.classList.add('with-chat');
            
            // Force a reflow before adding the visible class
            void this.chatContainer.offsetHeight;
            
            // Add visible class to trigger transition
            requestAnimationFrame(() => {
                this.chatContainer.classList.add('visible');
                
                // Hide example prompts
                this.examplePrompts.classList.add('hidden');
            });
            
            console.log('Chat container shown');
        }
    }

    showToast(message) {
        // Remove existing toast if present
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.classList.add('animate-toast-out');
        }
        
        // Clear existing timeout
        if (this.toastTimeout) {
            clearTimeout(this.toastTimeout);
        }

        const toast = createElement('div', 'toast animate-toast-in');
        toast.innerHTML = `
            <p>${message}</p>
            <button onclick="this.parentElement.classList.add('animate-toast-out'); setTimeout(() => this.parentElement.remove(), 300)">×</button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-dismiss after 3 seconds
        this.toastTimeout = setTimeout(() => {
            toast.classList.add('animate-toast-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    showWarning(warning, onProceed, onCancel) {
        const warningDiv = createElement('div', 'message warning-message animate-in');
        warningDiv.innerHTML = `
            <div>${warning}</div>
            <button onclick="handleProceed()" style="background-color: var(--primary-color);">Proceed</button>
            <button onclick="handleCancel()" style="background-color: rgba(0,0,0,0.1); color: var(--text-primary);">Cancel</button>
        `;

        // Add event handlers
        const proceedBtn = warningDiv.querySelector('button:first-of-type');
        const cancelBtn = warningDiv.querySelector('button:last-of-type');
        
        proceedBtn.onclick = () => {
            warningDiv.remove();
            onProceed();
        };
        
        cancelBtn.onclick = () => {
            warningDiv.remove();
            onCancel();
        };

        this.chatBox.appendChild(warningDiv);
        scrollToBottom(this.chatBox);
    }

    getInputValue() {
        return this.userInput.value;
    }

    setInputValue(value) {
        this.userInput.value = value;
        this.updateCharCount();
    }

    handleEnterPress() {
        const event = new CustomEvent('send-message');
        document.dispatchEvent(event);
    }
}

export const ui = new UI();
