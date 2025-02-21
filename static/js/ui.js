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
    }

    clearInput() {
        this.userInput.value = '';
        this.updateCharCount();
        this.appendMessage('Message cleared.', 'warning-message');
    }

    appendMessage(message, type, scroll = true, messageId = null) {
        console.log('Appending message:', { message, type, messageId });
        
        // Ensure chat container is visible
        if (!this.chatContainer.classList.contains('visible')) {
            this.showChatContainer();
        }

        // Create message element
        const messageDiv = createElement('div', `message ${type} animate-in`);
        messageDiv.innerHTML = formatMessage(message);
        console.log('Message HTML:', messageDiv.innerHTML);
        
        if (messageId) {
            messageDiv.setAttribute('data-message-id', messageId);
        }
        
        if (type === 'user-message') {
            messageDiv.setAttribute('data-timestamp', new Date().toISOString());
        }

        // Check if message contains an SMS number and show toast
        if (type === 'bot-message' && message.includes('SMS')) {
            const match = message.match(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/);
            if (match) {
                this.showToast(`SMS number copied: ${match[0]}`);
            }
        }
        
        // Add context indicator for bot messages that use context
        if (type === 'bot-message' && messageId) {
            const contextIndicator = createElement('div', 'context-indicator');
            contextIndicator.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2Z"/>
                    <path d="M8 12L12 16L16 12"/>
                    <path d="M12 8L12 16"/>
                </svg>
                <span class="tooltip">Using conversation context</span>
            `;
            messageDiv.appendChild(contextIndicator);
            
            // Add click handler to show related messages
            messageDiv.addEventListener('click', () => this.highlightRelatedMessages(messageId));
        }
        
        // Ensure chatBox exists and is accessible
        if (!this.chatBox) {
            console.error('Chat box element not found');
            return;
        }
        
        // Add message to chat box
        this.chatBox.appendChild(messageDiv);
        console.log('Message added to chat box');
        
        // Scroll if needed
        if (scroll) {
            scrollToBottom(this.chatBox);
        }
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
        const loadingDiv = createElement('div', 'loading');
        loadingDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="animate-spin">
                    <path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                JANE is thinking
                <div style="display: inline-flex; align-items: center;">
                    <div class="typing-dot animate-typing"></div>
                    <div class="typing-dot animate-typing" style="animation-delay: 0.2s"></div>
                    <div class="typing-dot animate-typing" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        this.chatBox.appendChild(loadingDiv);
        scrollToBottom(this.chatBox);
        return loadingDiv;
    }

    showLoadingMore() {
        const loadingDiv = createElement('div', 'loading loading-more');
        loadingDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="animate-spin">
                    <path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
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
            
            // Force a reflow before adding the visible class
            void this.chatContainer.offsetHeight;
            
            // Add visible class to trigger transition
            this.chatContainer.classList.add('visible');
            
            // Update other elements
            this.header.classList.add('animate-header-compact', 'compact');
            this.header.querySelector('.subtitle').classList.add('animate-subtitle-fade');
            this.inputSection.classList.add('with-chat');
            this.examplePrompts.classList.add('hidden');
            
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
