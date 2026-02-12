import os
import anthropic
import streamlit as st
from tavily import TavilyClient
import json
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Newsletter Research Agent",
    page_icon="📰",
    layout="wide"
)

# Tool definitions
tools = [
    {
        "name": "search_recent_content",
        "description": "Search for recent articles, papers, blog posts on a topic from the last 30 days",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for finding recent content"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "analyze_trending_discussions",
        "description": "Search for trending discussions and debates about a topic on social media and forums",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to analyze for trending discussions"
                }
            },
            "required": ["topic"]
        }
    }
]

def search_recent_content(query, max_results=10):
    """Search for recent content using Tavily API"""
    try:
        tavily = TavilyClient(api_key=os.environ.get("TAVILY_KEY"))
        results = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_domains=["arxiv.org", "medium.com", "substack.com", "dev.to", "hackernoon.com"]
        )
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching: {str(e)}"

def analyze_trending_discussions(topic):
    """Analyze trending discussions about a topic"""
    try:
        tavily = TavilyClient(api_key=os.environ.get("TAVILY_KEY"))
        results = tavily.search(
            query=f"{topic} discussion debate trending",
            search_depth="advanced",
            max_results=8
        )
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error analyzing discussions: {str(e)}"

def process_tool_call(tool_name, tool_input):
    """Execute the appropriate tool based on the tool name"""
    if tool_name == "search_recent_content":
        return search_recent_content(**tool_input)
    elif tool_name == "analyze_trending_discussions":
        return analyze_trending_discussions(**tool_input)
    else:
        return f"Unknown tool: {tool_name}"

def run_agent(topic):
    """Run the research agent with Claude"""
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_KEY"))
        
        messages = [{
            "role": "user",
            "content": f"""Research this topic for a technical newsletter: {topic}

Your task is to:
1. Find 5-7 most relevant recent articles, papers, or blog posts (prioritize last 30 days)
2. Identify what's being debated or is controversial about this topic
3. Suggest what angle hasn't been covered yet or is underexplored
4. Propose 3 everyday analogies that could explain this technical topic to a general audience

Format your final response as a research brief with clear sections."""
        }]
        
        # Agent loop (max 5 iterations to prevent infinite loops)
        for iteration in range(5):
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                tools=tools,
                messages=messages
            )
            
            # Check if agent is done
            if response.stop_reason == "end_turn":
                # Extract text from response
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                return final_text
            
            # Process tool calls
            if response.stop_reason == "tool_use":
                # Add assistant's response to messages
                messages.append({"role": "assistant", "content": response.content})
                
                # Execute each tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_result = process_tool_call(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result
                        })
                
                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                return f"Agent stopped unexpectedly: {response.stop_reason}"
        
        return "Agent reached maximum iterations without completing the task."
    
    except Exception as e:
        return f"Error running agent: {str(e)}"

# Streamlit UI
st.title("📰 Newsletter Research Agent")
st.markdown("**Research assistant for technical newsletter writing**")
st.markdown("---")

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input(
        "What topic should I research?",
        placeholder="e.g., 'vector databases', 'AI agent frameworks', 'edge computing trends 2025'"
    )
with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    research_button = st.button("🔍 Research", type="primary", use_container_width=True)

# Display instructions
with st.expander("ℹ️ How it works"):
    st.markdown("""
    This agent autonomously:
    1. **Searches** recent technical content (last 30 days)
    2. **Analyzes** trending discussions and debates
    3. **Identifies** underexplored angles
    4. **Suggests** everyday analogies for technical concepts
    
    Built with Claude Sonnet 4.5, Tavily Search API, and Streamlit.
    """)

# Research execution
if research_button and topic:
    with st.spinner(f"🤖 Agent researching '{topic}'... This may take 30-60 seconds"):
        result = run_agent(topic)
        
        st.markdown("---")
        st.subheader("📋 Research Brief")
        st.markdown(result)
        
        # Download option
        st.download_button(
            label="📥 Download Research Brief",
            data=result,
            file_name=f"research_{topic.replace(' ', '_')}.md",
            mime="text/markdown"
        )

elif research_button and not topic:
    st.warning("Please enter a topic to research")

# Footer
st.markdown("---")
st.caption("Built by Irsa Ashraf • Deployed on Render • Powered by Claude & Tavily")
