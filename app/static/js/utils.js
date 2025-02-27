/**
 * Utility functions for JANE chat application
 */

export const formatMessage = (message) => {
    if (!message) {
        console.error('Empty message received in formatMessage');
        return '';
    }
    console.log('Formatting message:', message);
    
    // Handle code blocks first to prevent interference with other formatting
    let formatted = message.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => 
        `<pre><code class="language-${lang || 'plaintext'}">${code.trim()}</code></pre>`
    );
    
    // Handle headers (### Step N: Title)
    formatted = formatted.replace(/### (.*)\n/g, '<h3>$1</h3>\n');
    formatted = formatted.replace(/#### (.*)\n/g, '<h4>$1</h4>\n');
    
    // Handle bullet points
    formatted = formatted.replace(/^- (.*)/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    // Handle bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Split into paragraphs (handling both \n\n and single \n)
    const paragraphs = formatted
        .split(/\n{2,}/)
        .map(block => block.trim())
        .filter(block => block.length > 0)
        .map(block => {
            // Don't wrap pre, ul, h3, or h4 elements in p tags
            if (block.startsWith('<pre>') || 
                block.startsWith('<ul>') || 
                block.startsWith('<h3>') || 
                block.startsWith('<h4>')) {
                return block;
            }
            return `<p>${block}</p>`;
        });
    
    formatted = paragraphs.join('\n');
    
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

export const createElement = (tag, options = {}) => {
    const element = document.createElement(tag);
    if (options.className) element.className = options.className;
    if (options.innerHTML) element.innerHTML = options.innerHTML;
    if (options.textContent) element.textContent = options.textContent;
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
