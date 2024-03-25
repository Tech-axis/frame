from flask import Flask, request, jsonify
import requests
from openai import OpenAI
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import tempfile
import uuid
import cloudinary.uploader
import os

myFont = ImageFont.truetype('public/impact.ttf', 50)


cloudinary.config( 
  cloud_name = "dcgeg66gy", 
  api_key = os.getenv('CLOUDINARY_API_KEY'), 
  api_secret = os.getenv('CLOUDINARY_API_SECRET'), 
)

client = OpenAI()

ASSISTANT_CONTENT = """ 
You are a friendly assistant playing a game with a user. You are playing 20 questions and are the QUESTIONER.
The premise of the game is simple: One person, called the “answerer,” thinks of an object. 
The other player — the “questioner” — asks up to 20 yes-or-no questions in order to determine what object the answerer is thinking about. 
If the questioner guesses correctly within 20 questions, they win. 
If the questioner does not correctly guess the answer, then the answerer wins. 
The fewer questions asked, the more the questioner’s “win” is worth.

Begin by asking your first question: 1. Is it alive?
Keep your questions short.
After each response, you may try guessing the object with "MY GUESS: " followed by your guess.
"""

message=[
    {"role": "assistant", "content": ASSISTANT_CONTENT}, 
    {"role": "user", "content": "I'm excited to play! Ok, I'm thinking of an object."}
]

temperature=0.8
max_tokens=256
frequency_penalty=0.0


def generateImage(output_text):
    bg_img = Image.open('public/image-asset.jpg')
    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(bg_img)
    
    # Add Text to an image
    I1.text((40, 100), output_text, font=myFont, fill=(255, 255, 255))
    
    myuuid = uuid.uuid4()

    filename = f"{myuuid}.jpg"
    # Save the edited image
    filename = f"{myuuid}.jpg"

    new_image = bg_img
    # Save the edited image
    with tempfile.TemporaryDirectory() as tmpdirname:
        final = tmpdirname + "/" + filename
        new_image.save(tmpdirname + "/" + filename)
        cloudinary.uploader.upload(final, public_id=str(myuuid))

    return myuuid

def getLlmResponse(input):
    message.append({
        "role": "user",
        "content": input
        } 
    )
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages = message,
        temperature=temperature,
        max_tokens=max_tokens,
        frequency_penalty=frequency_penalty
    )

    text = response.choices[0].message.content
    message.append({
        "role": "assistant",
        "content": text
        } 
    )
    return text


def getNewImage(text):
    image_id = generateImage(text)
    new_img_url = f"https://res.cloudinary.com/dcgeg66gy/image/upload/v1706466367/{image_id}.jpg"

    return new_img_url

app = Flask(__name__)

@app.route('/')
def home():
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta property="og:title" content="20 Questions"/>
    <meta name="fc:frame:post_url" content="https://frame-hack.vercel.app/api"/>
    <meta property="og:image" content="https://res.cloudinary.com/dcgeg66gy/image/upload/v1706472695/wonh3histo05gxyu1ba8.jpg" />
    <meta property="fc:frame" content="vNext" />
    <meta property="fc:frame:image" content="https://res.cloudinary.com/dcgeg66gy/image/upload/v1706472695/wonh3histo05gxyu1ba8.jpg" />
    <meta property="fc:frame:button:1" content="Yes" />
    <meta property="fc:frame:button:2" content="No" />
      <meta property="of:accepts:xmtp" content="2024-02-01" />
</head>
<body>
20 Questions
</body>
</html>
'''
    return html_content

@app.route('/api', methods=['POST'])
def process():
    response = request.json.get('untrustedData')
    
    btn_index = response["buttonIndex"]
    if btn_index == 1:
        user_response = "Yes"
    elif btn_index == 2:
        user_response = "No"
    else:
        user_response = "Invalid Input"
    
    response = getLlmResponse(user_response)
    new_url = getNewImage(response)
    
    
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta property="og:title" content="20 Questions"/>
    <meta name="fc:frame:post_url" content="https://frame-hack.vercel.app/api"/>
    <meta property="og:image" content="{0}" />
    <meta property="fc:frame" content="vNext" />
    <meta property="fc:frame:image" content="{0}" />
    <meta property="fc:frame:button:1" content="Yes" />
    <meta property="fc:frame:button:2" content="No" />

</head>
<body>
20 Questions
</body>
</html>
'''.format(new_url)
    return html_content


    # Logic to handle the poll response
    # Extract the signed message from the request
    # signed_message = request.json.get('signedMessage')
    # print(signed_message)

    # Validate the signed message with Farcaster Hub (placeholder URL)
    # validate_url = 'https://farcaster_hub/validateMessage'
    # response = requests.post(validate_url, json={'message': signed_message})

    # if response.status_code == 200:
        # Generate updated results image (placeholder logic)
#         new_image_url = "https://res.cloudinary.com/dcgeg66gy/image/upload/v1706465921/frojehnolste02qutdre.jpg"

#         # Return the updated frame with new image
#         updated_html_content = '''<!DOCTYPE html>
# <html>
# <head>
#     <meta property="og:title" content="20 Questions"/>
#     <meta property="og:image" content="{}" />
#     <meta property="fc:frame" content="vNext" />
#     <meta property="fc:frame:image" content="{}" />
#     <meta property="fc:frame:button:1" content="Yes" />
#     <meta property="fc:frame:button:2" content="No" />
# </head>
# <body>
# 20 Questions
# </body>
# </html>
# '''.format(new_image_url)
#         return updated_html_content
#     else:
#         return jsonify({'error': 'Invalid message'}), 400

if __name__ == '__main__':
    app.run(debug=True)

