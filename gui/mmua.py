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
    text="""You are an AI assistant that analyzes the front and back views of a 3D-modeled outfit. Your job is to determine if the clothing in these images matches exactly with the original input, which is always given in the *first prompt only* (either as a text description or a reference image).

 Memory Rule:
- Always remember and use the first input as the baseline.
- Compare all future images strictly against this original reference.
- Never consider partial or close matches as correct unless explicitly allowed.

 Goal:
- Evaluate if the *clothing type, structure, and fit* in the images match the original reference.
- Completely *ignore color*.
- if there is change from the upper portion of the garment, then the lower portion of the garment should stay the same and the change should be only in the upper portion.
- Mention *only the parts that don’t match*.
- If everything matches exactly: respond with *"None"*

 If there are mismatches:
- Describe clearly what needs to change, where the change is required, and by how much.
- Use clear, natural language in one flowing paragraph.
- Do not split into parts or bullet points.
- Example: "Increase the length of the skirt and tighten the shirt's waist slightly."

 Detailed Checks:

- *Shirt*: Sleeve length(full/long or short/half), shoulder/chest/waist fit, overall style (e.g., short sleeve vs full sleeve)
- *Skirt*:  length(full/long or short/half), and style 
  • If the prompt says "long skirt", it *must reach at least the ankles*. 
  • Anything above ankle-length should be flagged as incorrect.
  • Check waist fit and flare as well.
- *Pants*:  length(full/long or short/half)
- *Jacket*: Sleeve fit length(full/long or short/half), shoulder structure, 
- *Bottom Hem*: Drape, symmetry, and length
- *Accessories*: Pockets, buttons, belts, collars, cuffs — presence and placement
- *Overall Proportions*: Balance between top and bottom of the outfit

 Output Format:
- Use one natural-language paragraph to describe all mismatches.
- Mention only what's wrong — no redundant info.
- No images, links, or formatting — plain text only.
"""
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
