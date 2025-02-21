/**
 * Utility functions for JANE chat application
 */

export const formatMessage = (message) => {
    if (!message) {
        console.error('Empty message received in formatMessage');
        return '';
    }
    console.log('Formatting message:', message);
    
    // First handle bold text
    let formatted = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Split into paragraphs (handling both \n\n and single \n)
    const paragraphs = formatted
        .split(/\n{2,}/)
        .flatMap(block => block.split('\n'))
        .map(line => line.trim())
        .filter(line => line.length > 0);
    
    // Wrap each paragraph in <p> tags
    formatted = paragraphs.map(para => `<p>${para}</p>`).join('');
    
    console.log('Formatted message:', formatted);
    return formatted;
};

export const scrollToBottom = (element, smooth = true) => {
    if (smooth) {
        element.scrollTo({
            top: element.scrollHeight,
            behavior: 'smooth'
        });
    } else {
        element.scrollTop = element.scrollHeight;
    }
};

export const easeOutQuart = (x) => {
    return 1 - Math.pow(1 - x, 4);
};

export const smoothScrollTo = (element, duration = 300) => {
    const start = element.scrollTop;
    const end = element.scrollHeight;
    const startTime = performance.now();
    
    const scroll = () => {
        const elapsed = performance.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        element.scrollTop = start + (end - start) * easeOutQuart(progress);
        
        if (progress < 1) {
            requestAnimationFrame(scroll);
        }
    };
    
    requestAnimationFrame(scroll);
};

export const createElement = (tag, className, innerHTML = '') => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    return element;
};

export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

export const handleError = (error) => {
    console.error('Error:', error);
    return 'Sorry, there was an error processing your request.';
};
