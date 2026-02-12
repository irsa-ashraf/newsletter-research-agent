# Newsletter Research Agent

Research assistant agent that automates 90% of newsletter research, cutting research time from 2 hours to 15 minutes.

## What It Does

This autonomous AI agent:
- **Searches** recent technical content (prioritizes last 30 days)
- **Analyzes** trending discussions and debates
- **Identifies** underexplored angles for newsletter topics
- **Suggests** everyday analogies to explain technical concepts

## Architecture

- **LLM**: Claude Sonnet 4.5 (Anthropic API)
- **Search**: Tavily API for web search with focus on technical content
- **Framework**: Streamlit for UI
- **Deployment**: Render

### How the Agent Works

1. User inputs a research topic
2. Agent autonomously decides which tools to use:
   - `search_recent_content` - finds recent articles/papers
   - `analyze_trending_discussions` - identifies debates
3. Agent synthesizes findings into a structured research brief
4. Output includes: key articles, debate points, unique angles, and analogies


This is a portfolio project, but suggestions welcome! Open an issue or submit a PR.

**Note**: This agent is designed for research assistance. Always verify information from primary sources before publishing.