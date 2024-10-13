import gradio as gr
from methods.agent_mongo import MongoDBHandler
from methods.agent_openai import get_profile, fit_profile, find_insights
import json
import requests
import base64
import os 
from io import BytesIO
from PIL import Image
import time
from dotenv import load_dotenv, find_dotenv
from methods.agent_llama_index import graphAgent


collection_type="user_profile"
_ = load_dotenv(find_dotenv()) 

mongo_uri = os.environ['MONGO_URI'] 
openai_api_key= os.environ['OPENAI_API_KEY']


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

mongo_handler = MongoDBHandler(mongo_uri, openai_api_key)

# Sample function to generate three responses
def generate_responses(user_input):
    # Retrieve user profile experience from MongoDB
    profile_experience = mongo_handler.retrieve_relevant_data(user_input, "", "user_profile")

    # Generate responses for each profile
    responses=[]
    nCount=0
    for profile in profile_experience:
        nCount+=1
        agent_response = fit_profile(user_input, profile['profile'])

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
            "image": image,
            "agent_profile": agent_response.profile_agent
        })

    
    # Return all 15 values separately for Gradio output
    return (
        responses[1]["image"], responses[1]["name"], responses[1]["description"], responses[1]["why_match"], responses[1]["intro"], responses[1]["linkedin"],responses[1]["agent_profile"], 
        responses[0]["image"], responses[0]["name"], responses[0]["description"], responses[0]["why_match"], responses[0]["intro"], responses[0]["linkedin"],responses[0]["agent_profile"],
        responses[2]["image"], responses[2]["name"], responses[2]["description"], responses[2]["why_match"], responses[2]["intro"], responses[2]["linkedin"],responses[2]["agent_profile"]
    )

def simulate_chat(linkedin_1, linkedin_2, category, chat_history):
    # Ensure chat_history is initialized
    if chat_history is None:
        chat_history = []

    # Initialize graphAgent with OpenAI GPT-4
    config_openai = {
        "model_type": "openai",
        "model_name": "gpt-4o"
    }
    
    agent_openai = graphAgent(user_id="user_1", profile_url=linkedin_1, config=config_openai)

    # Initialize graphAgent with Mistral
    config_openai_o1 = {
        "model_type": "openai",
        "model_name": "gpt-4o"
    }

    agent_mistral = graphAgent(user_id="user_2", profile_url=linkedin_2, config=config_openai_o1)

    # Simulate autonomous loop
    response_2=f"Hi, Lets talk about your {category}, what is the most exciting thing you have done in this area?"

    
    for i in range(5):  # Simulate a 50-round conversation
        response_1=agent_openai.stream_graph_updates(response_2)
        chat_history.append((response_1, None)) 
        yield chat_history, ""
        response_2=agent_mistral.stream_graph_updates(response_1)
        chat_history.append((None, response_2))     

        yield chat_history, ""

        if i==4:
            print("Chat simulation completed!")
            response=find_insights(chat_history)
            chat_history.append((str(response), None)) 
            yield chat_history, response
        

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
            agent_profile_1 = gr.Textbox(label="Agent Profile 1")
        
        with gr.Column():
            gr.Markdown("<h3 style='text-align: center;'>🔍 Expert 2</h3>")
            img_2 = gr.Image(label="Image 2")
            name_2 = gr.Textbox(label="Name 2")
            desc_2 = gr.Textbox(label="Description 2")
            match_2 = gr.Textbox(label="Why this is a good match")
            intro_2 = gr.Textbox(label="Intro to start conversation")
            linkedin_2 = gr.Textbox(label="LinkedIn Profile")
            agent_profile_2 = gr.Textbox(label="Agent Profile 2")
        
        with gr.Column():
            gr.Markdown("<h3 style='text-align: center;'>🔍 Expert 3</h3>")
            img_3 = gr.Image(label="Image 3")
            name_3 = gr.Textbox(label="Name 3")
            desc_3 = gr.Textbox(label="Description 3")
            match_3 = gr.Textbox(label="Why this is a good match")
            intro_3 = gr.Textbox(label="Intro to start conversation")
            linkedin_3 = gr.Textbox(label="LinkedIn Profile")
            agent_profile_3 = gr.Textbox(label="Agent Profile 3")

    # Add your linkedIn profile
    linkedin_profile = linkedin_profile = gr.Textbox(label="Enter your LinkedIn profile")

    # Dropdown to select category (industry, academic, hobbies)
    category_dropdown = gr.Dropdown(choices=["industry", "academic", "hobbies"], 
                                    label="Select Category", 
                                    value="industry")
    
    # Simulated chat section
    with gr.Row():
        with gr.Column():
            gr.Markdown("<h3 style='text-align: center;'>💬 Simulated Chat</h3>")
            chatbox = gr.Chatbot(label="Pro-Network DJ", avatar_images=['figure/user.png', 'figure/sha.png'])

    # Button to start the autonomous simulation
    simulate_btn = gr.Button("Start Simulated Chat 🚀")
    
    # Define the action when the button is clicked
    generate_btn.click(fn=generate_responses, 
                       inputs=user_input, 
                       outputs=[img_1, name_1, desc_1, match_1, intro_1, linkedin_1, agent_profile_1,
                                img_2, name_2, desc_2, match_2, intro_2, linkedin_2, agent_profile_2,
                                img_3, name_3, desc_3, match_3, intro_3, linkedin_3, agent_profile_3])
    
    # Define the action when the button is clicked
    final_insights_textbox = gr.Textbox(label="Final Insights", placeholder="Insights will be displayed here after the chat.")

    # Here we have to add the text inputs to the simulate_chat function
    simulate_btn.click(fn=simulate_chat,
        inputs=[linkedin_profile, linkedin_1, category_dropdown], 
        outputs=[chatbox, final_insights_textbox])
    



# Launch the app
demo.launch(share=True)
