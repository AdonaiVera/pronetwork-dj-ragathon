import openai
from openai import OpenAI
from pydantic import BaseModel

from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv()) 

mongo_uri = os.environ['MONGO_URI'] 
API_KEY= os.environ['OPENAI_API_KEY']
model = "gpt-4o" 

open_ai_client = OpenAI(api_key=API_KEY)

class InformationProfile(BaseModel):
    profile_user: str
    topic: str
    key_words: str  
    main_topic: str

def get_profile(profile_user):
    system_context = (
        """You are an assistant designed to summarize professional profiles and extract relevant research topics based on provided data. Follow a step-by-step reasoning process to ensure the accuracy and completeness of your output. Below is the user's information:
        
        {}

        Follow these steps to generate your response:
        1. Analyze the user's information to understand their background, expertise, and main areas of work.
        2. Summarize the user's professional profile in a clear and concise manner.
        3. Identify and suggest key areas of work or research interests based on the user's profile.
        4. Highlight specific key words that represent the user's main topics of interest.
        5. Categorize the main topics of work or research based on predefined fields (e.g., artificial_intelligence, reasoning, engineer, research).

        Output:
        profile_user: str -> Summary of the user's professional profile
        topic: str -> Main area of work or research interest
        key_words: str -> Keywords representing important concepts in the user's profile
        main_topic: str -> Global category of the user's main area of work or research

        Use a step-by-step approach to ensure the information is extracted accurately and comprehensively.
        """.format(str(profile_user))
    )

    messages=[
        {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": system_context
                }
            ]
        }
    ] 
    
    # Make the API call with structured output
    completion = open_ai_client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=InformationProfile,
    )

    # Extract the structured output
    return completion.choices[0].message.parsed



def find_insights(conversation, model=model):
    """
    Call OpenAI API to check if there is enough information about the user to suggest mentors.
    """
    system_context = (
        """You are an intelligent assistant designed to extract key insights from a conversation between two individuals based on their profiles and dialogue.

        Below is the conversation between the two users:
        
        {}

        Follow these steps to generate insights:

        Step 1: Analyze the Conversation
        - Identify key themes, topics, or areas of interest discussed by both users.
        - Detect any areas of agreement, shared experiences, or common goals.
        - Highlight any differences in perspectives, opinions, or approaches.

        Step 2: Extract Relevant Insights
        - Extract insights based on common professional or personal experiences.
        - Highlight any unique accomplishments, expertise, or skills that complement each other in the conversation.
        - Identify moments where the users align in terms of career progression, industries, or professional background.

        Step 3: Summarize Conversation Insights
        - Create a concise list of key insights, highlighting points of alignment, complementarity, and key takeaways from the conversation.
        - Each insight should be a short, direct statement reflecting the conversation between the two users.

        Output: Return a list of insights from the conversation.
        
        Example Output:
        - "Both users share a strong background in AI and entrepreneurship."
        - "User 1 focuses on vision and strategy, while User 2 excels in execution and technical implementation."
        - "Both users have complementary skills in leadership and product development."
        
        Only return the output as a list of insights.
        """.format(str(conversation))
    )

    response = open_ai_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": system_context,
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content

def get_profile(profile_user, model=model):
    """
    Call OpenAI API to check if there is enough information about the user to suggest mentors.
    """
    system_context = (
        """You are an intelligent assistant designed to create a dynamic digital replica of a person, based on the provided user profile information. Your task is to carefully analyze and summarize their identity, professional background, and communication style.

        Below is the user's information:
        
        {}

        Follow these steps to generate the user's digital profile:

        Step 1: Analyze Background and Expertise
        - Identify the user's main areas of expertise, professional experiences, and key accomplishments.
        - Extract relevant details from their education, work experience, skills, and areas of specialization.
        - Pay attention to any industries, companies, or roles that reflect the user's expertise.

        Step 2: Summarize Professional Profile
        - Concisely summarize the user's professional background, highlighting their expertise, industries, and career progression.
        - Ensure the summary captures key aspects of their work and professional identity.

        Step 3: Capture the User's Voice and Identity
        - Based on their background, infer the user's communication style, tone, and identity voice.
        - Consider how the user might present themselves in conversations, and their unique qualities (e.g., formal, visionary, technical, friendly).
        - Create a sentence that encapsulates the user's identity and communication style in the digital profile.

        Output: Generate a dynamic and concise representation of the user.
        
        Example Output:
        - "You are Ado, a visionary entrepreneur with a technical background, known for your innovative thinking and concise, strategic communication style."
        
        Only return the output as a string.
        """.format(str(profile_user))
    )

    response = open_ai_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": system_context,
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


class MatchProfile(BaseModel):
    match: str
    intro: str
    profile_agent: str

def fit_profile(search, profile_expected):
    system_context = """
   
    **search:** {search}

    **Expected Match Profile:** {profile_expected}

    ---

    **Your Task:** Provide two outputs by following these reasoning steps:

    ### Step 1: Analyze the Match
    - Compare the key attributes of the search and the profile (skills, interests, experiences).
    - Identify the common ground or complementing traits that make them a good match.

    ### Step 2: Generate a Short Explanation
    - Based on your analysis, write a concise explanation (1-2 sentences) of why these profiles are a good match.

    ### Step 3: Brainstorm an Intro Topic
    - Think about what topics or mutual interests could spark an engaging conversation.
    - Consider the expected match’s profile and what might resonate with them.

    ### Step 4: Write the main topic in common
    - Craft the last experience that can be used to start the conversation (Go to the most detailed possible.)

    ### Step 5: Create a profile of the agent
    - Based on the profile expected, generate a comprehensive profile for the agent, only use the profile information. The profile should include the agent's name, areas of expertise, and key strengths. Structure it in a way that reads naturally and provides context to the agent’s capabilities.
    Example: "You are Alex, an expert in artificial intelligence, data analysis, and machine learning. With extensive experience in predictive modeling and automation, you specialize in providing innovative solutions to complex data-driven challenges. Your strengths include strategic thinking, problem-solving, and technical leadership, enabling you to deliver actionable insights and guide businesses toward data-driven decision-making."

    **Outputs:**
    1. match: **Why This is a Good Match:** 
    2. intro: **Taking point detailled (Be more specific possible) to Start a Conversation:**'
    3. profile_agent: **Profile of the agent:**'
    """.format(search=search, profile_expected=profile_expected)

    messages=[
        {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": system_context
                }
            ]
        }
    ] 

    
    # Make the API call with structured output
    completion = open_ai_client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=MatchProfile,
    )

    # Extract the structured output
    return completion.choices[0].message.parsed