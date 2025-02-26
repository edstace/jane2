/**
 * Manages conversation history and context for the chat application
 */
export class MessageHistory {
    constructor(maxMessages = 10) {
        this.messages = [];
        this.maxMessages = maxMessages;
        this.conversationId = null;
    }

    addMessage(content, type, timestamp = new Date().toISOString()) {
        const message = {
            content,
            type,
            timestamp,
            id: this.generateMessageId(),
            conversation_id: this.conversationId
        };

        this.messages.push(message);
        
        // Trim history if needed
        if (this.messages.length > this.maxMessages) {
            this.messages = this.messages.slice(-this.maxMessages);
        }

        return message;
    }

    getMessages(limit = null) {
        if (limit) {
            return this.messages.slice(-limit);
        }
        return [...this.messages];
    }

    getContextMessages(limit = 5) {
        return this.messages
            .filter(msg => msg.type === 'user-message' || msg.type === 'bot-message')
            .slice(-limit);
    }

    clear() {
        this.messages = [];
    }

    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getMessageById(id) {
        return this.messages.find(msg => msg.id === id);
    }

    getRelatedMessages(messageId, contextWindow = 2) {
        const index = this.messages.findIndex(msg => msg.id === messageId);
        if (index === -1) return [];

        const start = Math.max(0, index - contextWindow);
        const end = Math.min(this.messages.length, index + contextWindow + 1);
        
        return this.messages.slice(start, end);
    }

    toJSON() {
        return {
            messages: this.messages,
            maxMessages: this.maxMessages,
            conversationId: this.conversationId
        };
    }

    fromJSON(data) {
        this.messages = data.messages || [];
        this.maxMessages = data.maxMessages || 10;
        this.conversationId = data.conversationId || null;
    }
    
    setConversationId(id) {
        this.conversationId = id;
    }
    
    getConversationId() {
        return this.conversationId;
    }
}
