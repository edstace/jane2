from flask import Blueprint, render_template, send_from_directory, jsonify
from app.services.message_service import MessageService

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Serve home page"""
    return render_template('index.html')

@main.route('/terms_of_service')
def terms_of_service():
    """Serve terms of service page"""
    return render_template('terms_of_service.html')

@main.route('/privacy_policy')
def privacy_policy():
    """Serve privacy policy page"""
    return render_template('privacy_policy.html')

@main.route('/static/<path:path>')
def send_static(path):
    """Serve static files with caching headers"""
    response = send_from_directory('static', path)
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

@main.route('/clear-chat', methods=['POST'])
def clear_chat():
    """Clear all cached messages and responses"""
    try:
        MessageService.clear_history()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': f'Failed to clear chat history: {str(e)}'}), 500