import os

from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
)
from llama_index.llms.openai import OpenAI
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.utils.workflow import draw_all_possible_flows

from dotenv import load_dotenv, find_dotenv

from methods.agent_mongo import MongoDBHandler

collection_type="user_profile"
_ = load_dotenv(find_dotenv()) 

mongo_uri = os.environ['MONGO_URI'] 
API_KEY= os.environ['OPENAI_API_KEY']

#mongo_handler = MongoDBHandler(mongo_uri, API_KEY)

class PlanEvent(Event):
    """Write what this function do"""
    query: str
    observation: str
    reflection: str
    plan: str
    profile: str
    config: str
    
class ObservationEvent(Event):
    """Write what this function do"""
    query: str
    observation: str
    profile: str
    config: str

class ResponseEvent(Event):
    """Write what this function do"""
    query: str
    observation: str
    reflection: str
    plan: str
    response: str
    profile: str
    config: str

class ReflectionEvent(Event):
    """Write what this function do"""
    query: str
    observation: str
    reflection: str
    profile: str
    config: str
     
class llamaIndexHandler(Workflow):    
    @step
    async def observation_query(
        self, ctx: Context, ev: StartEvent 
    ) -> ObservationEvent:     
        _ = load_dotenv(find_dotenv()) 

        # Initialize the model         
        await ctx.set("llm", OpenAI(model=ev.llm_model, temperature=0.1, api_key=API_KEY))

        # we use a chat engine so it remembers previous interactions
        llm = OpenAI(temperature=0.0, model=ev.llm_model)
        await ctx.set(ev.config, SimpleChatEngine.from_defaults(llm=llm))
        
        # Improve the prompting.
        response = (await ctx.get("llm")).complete(
            f"""
            You receives the following message: {str(ev.query)}. 
            What you perceived on the message ?
            """
        )
        return ObservationEvent(query=ev.query, observation=str(response), profile=str(ev.profile), config=str(ev.config))
    
    @step
    async def reflection_query(
        self, ctx: Context, ev: ObservationEvent
    ) -> ReflectionEvent:
        # Now we take the result of the observation and reflect on it.
        reflection_response = (await ctx.get("llm")).complete(
            f"""
            Based on the message {ev.query} and the shared history, what are the key observations?
            Reflect on the meaning of the message in the context of their past experiences. 
            Consider emotional tone, intent, and any underlying themes.
          
            Observations: {ev.observation}.
            """
        )
        # Return ReflectionEvent for further handling
        return ReflectionEvent(query=ev.query, observation=ev.observation, reflection=str(reflection_response), profile=ev.profile, config=ev.config)

    @step
    async def plan_query(
        self, ctx: Context, ev: ReflectionEvent
    ) -> PlanEvent:
        # Further process the reflection response into a PlanEvent
        plan_response = (await ctx.get("llm")).complete(
            f"""

            Now, the agent considers how to respond. Based on the reflections and observations {ev.reflection} and {ev.observation}, 
            what are the possible response strategies? The response should be relevant 
            to their past experiences, addressing any unspoken concerns, needs, or connections.

            Base on the user query: {ev.query}  
            """
        )   
        return PlanEvent(query=ev.query, plan=str(plan_response), observation=ev.observation, reflection=ev.reflection, profile=ev.profile, config=ev.config)
    
    @step
    async def conversation(self, ctx: Context, ev: PlanEvent) -> StopEvent:
        
        # Retrieval here - Change it for RAG from user. 
        #documents = mongo_handler.retrieve_relevant_data(ev.query, "", "mentor_insights")

        #print("relevant documents: ", documents)

        # Use LLM to judge the best response
        print("Use config")
        print(ev.config)
        print(ev.profile)
        response = (await ctx.get(ev.config)).chat(
            f"""
            {ev.profile}

            You and I will have a conversation where I offer short but thoughtful insights, drawing from your profile and past experiences when it’s relevant. I’ll keep things concise but meaningful, ensuring every response feels personal and gives you something to think about. Let’s keep it light, clear, and helpful.
            """
        )

        return StopEvent(result=str(response))

class graphAgent():
    def __init__(self, user_id, config, profile, llm_model):
        """Initialize LangChain connection and OpenAI embedding generator."""

        self.model = llamaIndexHandler(timeout=120, verbose=True)
        self.profile=profile
        self.config=config
        self.llm_model=llm_model

        # Draw all possible flows
        draw_all_possible_flows(llamaIndexHandler, filename="multi_step_workflow.html")

    async def stream_graph_updates(self, user_input: str):
        try:        
            result_model = await self.model.run(
                query=user_input,
                profile=self.profile,
                config=self.config,
                llm_model=self.llm_model
            )
            
            return result_model 
        except Exception as e:
            print("[INFO] Error in graphAgent: ", e)
            return None