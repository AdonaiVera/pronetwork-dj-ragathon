# AGENTIC RAG-A-THON - Hackathon Project 🚀

## Inspiration
Exceptional networkers at tech events typically aim to meet around 30 people, hoping to make 10 high-quality connections in a few hours. For events like SF Tech Week, this means interacting with less than 20% of the attendees. Most people end up manually sorting through the attendee list and reaching out on LinkedIn, which is time-consuming. We wanted to change that by enabling users to better connect with the right people at events.

Inspired by **Generative Agents**, introduced by Stanford’s **Park, Joon Sung, et al.** in 2023 ([research paper](https://arxiv.org/abs/2304.03442)), we created a system to simulate interactions between event attendees and uncover key details that could spark deeper connections—giving users an edge before meeting in person.

## What It Does
**ProNetwork DJ** helps you find and connect with the most relevant people at an event by using advanced algorithms and simulations. Here's how it works:

- **Input**: You provide a description of the type of people you’re looking to meet.
- **Profile Matching**: The system narrows down the list of event attendees to relevant profiles.
- **Agent Simulation**: Digital clones of both you and the relevant profiles are created.
- **Simulated Conversations**: Conversations are simulated between your digital clone and the matches, extracting insights from these interactions.
- **Recommendations**: The system provides key talking points for when you meet these people at the event.

## How We Built It

- **Data Collection**:
  - Scraped the Luma app for attendee lists.
  - Gathered LinkedIn profiles to get comprehensive user data.

- **Data Processing**:
  - Created digital user profiles using an **agent-based approach**.
  - Vectorized the data with **LlamaIndex** and stored it in a **MongoDB** vector database.

- **Matching Algorithm**:
  - Implemented **Retrieval-Augmented Generation (RAG)**.
  - Used **cosine similarity** to identify the top three matches based on user preferences.

- **Interaction Simulation**:
  - Developed a multi-agent system (user agent, observation agent, reflection agent, planning agent, conversation agent).
  - Simulated conversations between the user agent and the match agents.
  - Extracted key insights and areas of focus for real-life meetings.

- **Additional Features**:
  - Built a pipeline to fetch and store more data in the vector database using **Pinecone**.


## How to Run
### 1. Clone the repository
```bash
git clone https://github.com/your-username/agentic-rag-a-thon.git
cd agentic-rag-a-thon
```

### 2. Install Dependencies
Make sure you have Python 3.9 or higher. Install dependencies from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory of the project and add your API keys and other required environment variables:

```bash
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=your_mongodb_uri
PINECONE_API_KEY=your_pinecone_api_key
TAVILY_API_KEY=your_tavini_api_key
CSV_FILE="data/guest_profiles_dataset.csv"
```

### 4. Run the App
Start the application using:
```bash
python app.py
```

Once the app is running, you can access the Gradio interface through the local link provided in the terminal or by accessing the remote link if you're sharing the app.

## Challenges We Faced
Implementing a simplified generative agent memory system proved to be more challenging than expected. This resulted in conversations between agents lacking the level of detail we hoped for. To overcome this temporarily, we injected targeted prompts and discussion topics to ensure we could still generate useful insights. Future iterations and access to more detailed data will improve the system.

## Accomplishments We’re Proud Of
- We’re proud of rethinking the networking process by using **simulation** to explore deeper connections.
- Building such an exciting project with a great team during the hackathon has been a major highlight.

## What We Learned
- **LlamaIndex** is a game-changer for vectorizing and processing data.
- We learned the importance of moving fast, iterating quickly, and ensuring simulated interactions are meaningful.

## What’s Next for ProNetwork DJ
- We aim to run more simulations to create parallel "what could happen" scenarios for networking events.
- We’re also interested in exploring the potential of using simulations in **sales**, to improve lead generation and matching.
- We plan to expand our data scraping efforts to include sources like **Google Scholar**, **news articles**, and other databases to create richer user profiles.

## Built With
- **gpt**
- **gradio**
- **llamaindex**
- **mistral**
- **mongodb**
- **pinecone**
- **python**

## Try It Out
- **GitHub Repo**: [Repository Link](#)
- **Live Demo**: [https://d2328564c0ac4cfb4c.gradio.live](https://d2328564c0ac4cfb4c.gradio.live)

## Authors
- **Adonai Vera**
- **Luis Silva Vargas**
- **Christos Magganas**

---

This project was built during the **AGENTIC RAG-A-THON**, a hackathon focused on using **RAG (Retrieval-Augmented Generation)** to solve real-world problems.