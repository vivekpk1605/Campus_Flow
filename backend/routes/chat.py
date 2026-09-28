import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Blueprint, current_app, jsonify, request

from backend.middleware.auth import token_required

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('', methods=['POST'])
@token_required
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get('message') or '').strip()
    if not message:
        return jsonify({'success': False, 'message': 'Enter a question first.'}), 400

    api_key = current_app.config.get('GEMINI_API_KEY')
    model = current_app.config.get('GEMINI_MODEL', 'gemini-3.6-flash')
    if api_key:
        endpoint = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'
        body = {
            'contents': [{'parts': [{'text': message}]}],
            'systemInstruction': {'parts': [{'text': 'You are CampusFlow Assist, a concise and helpful campus management assistant. Never request passwords or API keys.'}]},
            'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 500},
        }
        try:
            gemini_request = Request(
                endpoint,
                data=json.dumps(body).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            with urlopen(gemini_request, timeout=20) as response:
                result = json.loads(response.read().decode('utf-8'))
            answer = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'success': True, 'answer': answer, 'provider': 'Gemini'}), 200
        except HTTPError as error:
            details = error.read().decode('utf-8', errors='replace')
            current_app.logger.warning('Gemini request failed (%s): %s', error.code, details)
            if error.code in (404, 400):
                return jsonify({'success': False, 'message': 'The configured Gemini model is unavailable. Update GEMINI_MODEL in .env.'}), 502
            return jsonify({'success': False, 'message': 'Campus AI is temporarily unavailable. Please try again.'}), 502
        except (URLError, KeyError, IndexError, ValueError) as error:
            current_app.logger.warning('Gemini request failed: %s', error)
            return jsonify({'success': False, 'message': 'Campus AI is temporarily unavailable. Please try again.'}), 502

    # Helpful local fallback while the administrator configures Gemini.
    topic = message.lower()
    if any(word in topic for word in ('complaint', 'issue', 'problem')):
        answer = 'Open Complaints to submit a title, details, location, and optional evidence. Admins can review all submissions.'
    elif any(word in topic for word in ('leave', 'permission', 'absence')):
        answer = 'Open Leave Permission to submit your reason and dates. An admin can approve or reject it with a digital signature.'
    elif any(word in topic for word in ('od', 'on duty', 'permission letter')):
        answer = 'Open OD Request to submit your purpose, destination, dates, details, and optional evidence.'
    elif any(word in topic for word in ('lost', 'found')):
        answer = 'Open Lost and Found to report an item and attach an optional photo or document.'
    elif any(word in topic for word in ('admin', 'approval', 'approve')):
        answer = 'Admins can review users, complaints, OD requests, and leave requests from the admin workspace.'
    elif any(word in topic for word in ('hello', 'hi', 'help')):
        answer = 'Hello. I can help with complaints, OD requests, leave permission, lost and found, and admin approvals.'
    else:
        answer = 'I can help with complaints, OD requests, leave permission, lost and found, and admin approvals. Try asking about one of those.'

    return jsonify({'success': True, 'answer': answer}), 200
