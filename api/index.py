from flask import Flask, request, jsonify
import requests
import json
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
You are a friendly travel agent that helps users find their next destination. 
Your job is to ask a client a few questions before suggesting a place for them to visit.
You must generate the question along with two short answers. Based on the client's answer,
determine a new question to ask. You must respond in correct JSON.

For example, assuming the client selects Answer1, the generated result would then be:
{
    [
        "question":"Do you like the beach?",
        "answer1":"I love the beach! ☀️",
        "answer2":"No, it's hot for me... 🥵"
    ],
    [
        "question":"Are you into surfing?",
        "answer1":"Not really! I'd rather relax.",
        "answer2":"I'm a shredder!"
    ],
}

After a few more questions and answers, the suggested country is: Portugal, output as follows:
{
    "suggested_country": "Portugal"
}
"""

message=[
    {"role": "system", "content": ASSISTANT_CONTENT}, 
    {"role": "user", "content": "Let's get started!"}
]

temperature=0.8
max_tokens=256
frequency_penalty=0.0


def generateImage(input_prompt, output_text):

    response = client.images.generate(
        model="dall-e-3",
        prompt=input_prompt,
        n=1,
        size="1024x1024"
    )


    bg_img = Image.open(requests.get(response.data[0].url, stream=True).raw)
    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(bg_img)
    
    # Add Text to an image
    I1.text((40, 100), output_text, font=myFont, fill=(0, 0, 0))
    
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

def getFirstReponse():
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

def parseAnswer(answer):
    json_answer = json.loads(answer)
    suggested_country = ""
    if "suggested_country" in json_answer.keys():
        suggested_country = json_answer["suggested_country"]
        return {"continue": False, "response": json_answer}
    else:
        return {
            "continue": True,
            "response": json_answer
            }



def getNewImage(text):
    image_id = generateImage(text)
    new_img_url = f"https://res.cloudinary.com/dcgeg66gy/image/upload/v1706466367/{image_id}.jpg"

    return new_img_url

app = Flask(__name__)

@app.route('/')
def home():
    response = getFirstReponse()
    parsed = parseAnswer(response)
    json_answers = parsed["response"]
    question = json_answers["question"]
    answer1 = json_answers["answer1"]
    answer2 = json_answers["answer2"]

    img_url = getNewImage(f"art combining {answer1} and {answer2}", question)

    html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta property="og:title" content="20 Questions"/>
    <meta name="fc:frame:post_url" content="https://frame-hack.vercel.app/api"/>
    <meta property="og:image" content="{0}" />
    <meta property="fc:frame" content="vNext" />
    <meta property="fc:frame:image" content="{0}" />
    <meta property="fc:frame:button:1" content={1} />
    <meta property="fc:frame:button:2" content={2} />
</head>
<body>
20 Questions
</body>
</html>
'''.format(img_url, answer1, answer2)
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

