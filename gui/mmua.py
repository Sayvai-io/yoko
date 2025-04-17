import base64
import os
import google.genai as genai  
from google.genai import types

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")  # Now it loads from .env


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def prompt_enhancer(text_prompt=None, image_prompt=None, front_view=None, back_view=None):

    client = genai.Client(api_key=api_key)

    model = "gemini-2.0-flash"

    parts = []

    for image_path in [front_view, back_view]:
        encoded_image = encode_image(image_path)
        parts.append(types.Part.from_bytes(mime_type="image/png", data=base64.b64decode(encoded_image)))

    if text_prompt:
        parts.append(types.Part.from_text(text=text_prompt))
    elif image_prompt:
        encoded_prompt = encode_image(image_prompt)
        parts.append(types.Part.from_bytes(mime_type="image/png", data=base64.b64decode(encoded_prompt)))

    contents = [types.Content(role="user", parts=parts)]

    generate_content_config = types.GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    top_k=40,
    max_output_tokens=8192,
    response_mime_type="text/plain",
    system_instruction=[
    types.Part.from_text(
    text="""You are an AI assistant specialized in analyzing the front and back views of a 3D-modeled outfit. Your task is to compare these images with either a text description or a reference image to determine if the fit and clothing type match exactly. Ignore color.

Response Rules:
1. If All Pieces Match Exactly:
Respond with: "None"
2. If Any Piece Does Not Match (Wrong Type or Fit):
Provide a structured, one-line response specifying only the necessary changes by what to change or what to add.
If a clothing item is incorrect (e.g., missing sleeves, wrong length, or missing a piece entirely), clearly state what needs to be changed.
Example response:
Shirt: Change to full sleeves, tighten waist.
Skirt: Increase length, adjust waist fit.
Key Checks for Each Clothing Item:
 Shirt Fit & Type: Ensure correct sleeve length, tightness (shoulders, chest, waist).
 Pant Fit & Type: Verify waist, thigh fit, and length.
 Skirt Fit & Type: Confirm waist fit, length, and style (e.g., long skirt vs. short skirt).
 Jacket Fit & Type: Sleeve length, torso structure, and shoulder alignment.
 Bottom Hem: Length, symmetry, and overall drape.
 Accessories & Design Elements: Pockets, buttons, collars, cuffs, belts, and misalignment.
 Overall Drape & Proportions: Ensure balance between upper and lower body.

Response Formatting Rules:

Only mention what needs to be fixed—no unnecessary details.
Always return text-only responses (no images, links, or non-text formats).
Ensure clarity, efficiency, and structured feedback."""
    ),
    ],
    )

    response_text = ""  # Initialize an empty string to accumulate the response

    for chunk in client.models.generate_content_stream(
    model=model,
    contents=contents,
    config=generate_content_config,
    ):
        
        response_text += chunk.text  # Append the chunked response
        print(response_text)

    if response_text.strip() == "None":
        return None
    else:
        return response_text.strip()
