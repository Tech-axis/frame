from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return 'Test!'

@app.route('/poll', methods=['GET'])
def poll_frame():
    # HTML content with Open Graph tags for the poll frame
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="fc:frame" content="vNext" />
        <meta property="fc:frame:image" content="https://generative-frame.vercel.app/api/image" />
        <meta property="fc:frame:button:1" content="Green" />
        <meta property="fc:frame:button:2" content="Blue" />
    </head>
    <body>
        Testing testing
    </body>
    </html>
    '''
    return html_content

@app.route('/poll', methods=['POST'])
def process_poll():
    # Logic to handle the poll response
    # Extract the signed message from the request
    signed_message = request.json.get('signedMessage')

    # Validate the signed message with Farcaster Hub (placeholder URL)
    validate_url = 'https://farcaster_hub/validateMessage'
    response = requests.post(validate_url, json={'message': signed_message})

    if response.status_code == 200:
        # Generate updated results image (placeholder logic)
        new_image_url = 'https://generative-frame.vercel.app/api/image'

        # Return the updated frame with new image
        updated_html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="fc:frame" content="vNext" />
            <meta property="fc:frame:image" content="{}" />
            <!-- Updated buttons/meta tags based on new poll results -->
        </head>
        <body>
            Updated Poll Frame Content
        </body>
        </html>
        '''.format(new_image_url)
        return updated_html_content
    else:
        return jsonify({'error': 'Invalid message'}), 400

if __name__ == '__main__':
    app.run(debug=True)

