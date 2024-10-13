import os
import pinecone
from sentence_transformers import SentenceTransformer
from llama_index.core.workflow import step, Context, Workflow, Event, StartEvent, StopEvent
from llama_index.llms.openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

from dotenv import load_dotenv, find_dotenv
from methods.agent_scrapper import extract_linkedin_profile
from methods.agent_openai import get_profile
from methods.agent_mongo import MongoDBHandler

from llama_index.core.chat_engine import SimpleChatEngine

# Initialize environment variables
_ = load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
mongo_uri = os.environ['MONGO_URI'] 
collection_type="user_experience_rag"
mongo_handler = MongoDBHandler(mongo_uri, OPENAI_API_KEY)
# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "user-profile"

# Check if the index exists, and create it if not
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'  
        )
    )

# Use the index
index = pc.Index(index_name)

# Initialize SentenceTransformer for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def save_profile_to_pinecone(linkedin, profile_id):
    """Saves all relevant LinkedIn data into Pinecone as vector embeddings for a specific user."""
    try:
        # Add all relevant metadata for future retrieval and filtering
        print("STORE IN PINECONE")
        cleaned_docs = []

        linkedin_data=linkedin['response']

        # Job title and summary
        cleaned_docs.append(f"My actual job is {linkedin_data['job_title'] if 'job_title' in linkedin_data else 'Unavailable'}")
        cleaned_docs.append(linkedin_data['summary'] if 'summary' in linkedin_data else 'No summary available')

        # Skills
        skills = linkedin_data['skills'] if 'skills' in linkedin_data else ''
        cleaned_docs.append(f"My skills are {skills if skills else 'No skills listed'}")

        # Location
        location_data = linkedin_data['location'] if 'location' in linkedin_data else {}
        location_city = location_data['city'] if 'city' in location_data else 'Unknown city'
        location_country = location_data['country'] if 'country' in location_data else 'Unknown country'
        cleaned_docs.append(f"I'm based in {location_city}, {location_country}")

        # Company
        company_data = linkedin_data['company'] if 'company' in linkedin_data else {}
        company_name = company_data['name'] if 'name' in company_data else 'Unknown company'
        cleaned_docs.append(f"I work at {company_name}")

        # Education details
        education_details = linkedin_data['education'] if 'education' in linkedin_data else []
        if education_details:
            education_str = "I've studied at the following institutions:"
            for edu in education_details:
                school_data = edu['school'] if 'school' in edu else {}
                school_name = school_data['name'] if 'name' in school_data else 'Unknown school'
                degree = edu['degree_name'] if 'degree_name' in edu else 'No degree listed'
                field_of_study = ', '.join(edu['field_of_study']) if 'field_of_study' in edu else 'No field of study listed'
                start_year = edu['date']['start']['year'] if 'date' in edu and 'start' in edu['date'] and 'year' in edu['date']['start'] else 'Unknown start year'
                end_year = edu['date']['end']['year'] if 'date' in edu and 'end' in edu['date'] and 'year' in edu['date']['end'] else 'Unknown end year'
                education_str += f"\n- {school_name}, {degree} in {field_of_study} ({start_year} - {end_year})"
            cleaned_docs.append(education_str)

        # Work experience details
        work_experience_details = linkedin_data['work_experience'] if 'work_experience' in linkedin_data else []
        if work_experience_details:
            work_str = "My work experience includes:"
            for exp in work_experience_details:
                company_data = exp['company'] if 'company' in exp else {}
                company_name = company_data['name'] if 'name' in company_data else 'Unknown company'
                profile_position = exp['profile_positions'][0] if 'profile_positions' in exp and exp['profile_positions'] else {}
                title = profile_position['title'] if 'title' in profile_position else 'No title'
                work_str += f"\n- {title} at {company_name}"
            cleaned_docs.append(work_str)

        # Languages details
        languages_details = linkedin_data['languages']['supported_locales'] if 'languages' in linkedin_data and 'supported_locales' in linkedin_data['languages'] else []
        if languages_details:
            languages_str = "I speak the following languages:"
            for lang in languages_details:
                language = lang['language'] if 'language' in lang else 'Unknown language'
                country = lang['country'] if 'country' in lang else 'Unknown country'
                languages_str += f"\n- {language} (from {country})"
            cleaned_docs.append(languages_str)

        for doc in cleaned_docs:
            mongo_handler.save_text_experience(profile_id, doc, collection_type)
    except Exception as e:
        print("[INFO] Error saving profile to Pinecone: ", e)

# Define the custom event for chat
class ChatEvent(Event):
    query: str
    profile_url: str  
    config: dict
    dynamic_profile: str
    chat_engine: SimpleChatEngine
     
class llamaIndexHandler(Workflow):    
    @step
    async def start_chat(self, ctx: Context, ev: StartEvent) -> ChatEvent:
        """Start the chat workflow by producing a ChatEvent."""
        # Produce the ChatEvent from StartChatEvent input data
        return ChatEvent(
            query=ev.query,
            profile_url=ev.profile_url,
            config=ev.config,
            dynamic_profile=ev.dynamic_profile,
            chat_engine=ev.chat_engine
        )
    
    @step
    async def conversation(self, ctx: Context, ev: ChatEvent) -> StopEvent:
        """Process the chat conversation."""
        # Generate an embedding for the query
        print("start here xxx")
        query_embedding = model.encode(ev.query).tolist()

        profile_experience = mongo_handler.retrieve_relevant_data(ev.query, ev.profile_url, "user_experience_rag")       
        all_content_rag = ' '.join(item['content'] for item in profile_experience)

        print("start here")
        print(ev.chat_engine)
        print("done")
        response = ev.chat_engine.stream_chat(
            f"""
            {ev.dynamic_profile}

            Let’s keep it casual and conversational, responding in a friendly and relatable way. Use your knowledge, and if necessary, feel free to bring in any additional information you know from external sources (RAG). Keep the responses short, like you’re chatting with a friend.
            
            User input: {ev.query}

            Additional information: {all_content_rag}
            """
        )

        print(response)
        return StopEvent(result=str(response))
    
    
class graphAgent():
    def __init__(self, user_id, profile_url, config):
        self.model=llamaIndexHandler(timeout=120, verbose=True)
        self.profile_url=profile_url
        self.config=config 

        # Initialize LLM once based on the configuration
        if self.config['model_type'] == 'openai':
            self.llm = OpenAI(temperature=0.0, model=self.config['model_name'], api_key=OPENAI_API_KEY)
        elif self.config['model_type'] == 'mistral':
            self.llm = OpenAI(temperature=0.0, model=self.config['model_name'], api_key=OPENAI_API_KEY)


        # Fetch dynamic profile from LinkedIn 
        dynamic_profile_linkedin = extract_linkedin_profile(self.profile_url)
        self.dynamic_profile=get_profile(dynamic_profile_linkedin)

        SYSTEM_PROFILE=f"""
            {self.dynamic_profile}

            Let’s keep it casual and conversational, responding in a friendly and relatable way. Use your knowledge, and if necessary, feel free to bring in any additional information you know from external sources (RAG). Keep the responses short, like you’re chatting with a friend.
            """
        
        self.chat_engine = SimpleChatEngine.from_defaults(
            llm=self.llm,
            system_prompt=SYSTEM_PROFILE
        )

        # Check if the profile already exists in Pinecone
        search_result = index.fetch(ids=[str(self.profile_url)])

        # Check if the profile already exist in MongoDB
        check_data = mongo_handler.retrieve_relevant_data("general info", self.profile_url, "user_experience_rag")

        if check_data==[]:
            save_profile_to_pinecone(dynamic_profile_linkedin, self.profile_url)


    def stream_graph_updates(self, user_input: str):
        """Process the chat conversation."""
        response=""
        try:
            # Generate an embedding for the query
            profile_experience = mongo_handler.retrieve_relevant_data(user_input, self.profile_url, "user_experience_rag")       
            all_content_rag = ' '.join(item['content'] for item in profile_experience)

            response = self.chat_engine.chat(F"User input: {user_input}, Additional information about you: {all_content_rag}")
        except Exception as e:
            print("[INFO] Error in conversation_chat: ", e)

        return str(response)
        