import gradio as gr
from methods.agent_mongo import MongoDBHandler
from methods.agent_openai import get_profile, fit_profile
import json
import requests
import base64
import os 
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) 

mongo_uri = os.environ['MONGO_URI'] 
openai_api_key= os.environ['OPENAI_API_KEY']
collection_type="user_profile"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

mongo_handler = MongoDBHandler(mongo_uri, openai_api_key)

# Sample function to generate three responses
def generate_responses(user_input):

    profile_experience = mongo_handler.retrieve_relevant_data(user_input, "", "user_profile")

    responses=[]

    nCount=0
    for profile in profile_experience:
        nCount+=1
        agent_response = fit_profile(user_input, profile)

        if profile['profile_pictrue'] is not None:

            # Decode Base64 to binary
            image_data = base64.b64decode(profile['profile_pictrue'])
            
            # Open image using PIL for Gradio
            image = Image.open(BytesIO(image_data))
        else:
            continue

            
        responses.append({
            "name": profile['user'],
            "description": profile['profile'],
            "why_match": agent_response.match,
            "intro": agent_response.intro,
            "linkedin": profile['linkedin_url'],
            "image": image 
        })
    

    # Return all 15 values separately for Gradio output
    return (
        responses[0]["image"], responses[0]["name"], responses[0]["description"], responses[0]["why_match"], responses[0]["intro"], responses[0]["linkedin"],
        responses[1]["image"], responses[1]["name"], responses[1]["description"], responses[1]["why_match"], responses[1]["intro"], responses[1]["linkedin"],
        responses[2]["image"], responses[2]["name"], responses[2]["description"], responses[2]["why_match"], responses[2]["intro"], responses[2]["linkedin"],
    )


# Create Gradio interface
with gr.Blocks(css=".title {color: white; text-align: center; background-color: #007BFF; padding: 10px; border-radius: 5px;}") as demo:
    # Page Title with Styling
    gr.Markdown("<h1 class='title'>🌟 Expert Finder App 🌟</h1>")

    # Textbox for user input
    user_input = gr.Textbox(label="Input your query", placeholder="Enter something to search for experts...")
    
    # Generate Button
    generate_btn = gr.Button("🔮 Generate Expert Matches", elem_id="generate_button")

    # Displaying the results in columns with improved styling
    with gr.Row():
        with gr.Column():
            gr.Markdown("<h3 style='text-align: center;'>🔍 Expert 1</h3>")
            img_1 = gr.Image(label="Image 1")
            name_1 = gr.Textbox(label="Name 1")
            desc_1 = gr.Textbox(label="Description 1")
            match_1 = gr.Textbox(label="Why this is a good match")
            intro_1 = gr.Textbox(label="Intro to start conversation")
            linkedin_1 = gr.Textbox(label="LinkedIn Profile")
        
        with gr.Column():
            gr.Markdown("<h3 style='text-align: center;'>🔍 Expert 2</h3>")
            img_2 = gr.Image(label="Image 2")
            name_2 = gr.Textbox(label="Name 2")
            desc_2 = gr.Textbox(label="Description 2")
            match_2 = gr.Textbox(label="Why this is a good match")
            intro_2 = gr.Textbox(label="Intro to start conversation")
            linkedin_2 = gr.Textbox(label="LinkedIn Profile")
        
        with gr.Column():
            gr.Markdown("<h3 style='text-align: center;'>🔍 Expert 3</h3>")
            img_3 = gr.Image(label="Image 3")
            name_3 = gr.Textbox(label="Name 3")
            desc_3 = gr.Textbox(label="Description 3")
            match_3 = gr.Textbox(label="Why this is a good match")
            intro_3 = gr.Textbox(label="Intro to start conversation")
            linkedin_3 = gr.Textbox(label="LinkedIn Profile")

   
    
    # Define the action when the button is clicked
    generate_btn.click(fn=generate_responses, 
                       inputs=user_input, 
                       outputs=[img_1, name_1, desc_1, match_1, intro_1, linkedin_1,
                                img_2, name_2, desc_2, match_2, intro_2, linkedin_2,
                                img_3, name_3, desc_3, match_3, intro_3, linkedin_3])

# Launch the app
demo.launch(share=True)
