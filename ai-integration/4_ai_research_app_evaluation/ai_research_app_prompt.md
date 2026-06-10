# System Prompt for AI Research Web App Agent

Build a comprehensive Next.js (App Router) web application MVP called "AILens" that acts as an AI research digest and intelligent assistant.

```xml
<guidelines>
    1. Tech Stack: Strictly use Next.js (TypeScript), Prisma ORM, Vercel Postgres, Vercel Cron Jobs, and NextAuth.js. Use `next-intl` for English internationalization.
    2. Architecture: Implement Server Actions for data mutations and API routes for interacting with the Anthropic Claude API (using Vercel AI SDK).
    3. Data Source: The app must fetch daily articles from the `https://arxiv.org/list/cs.AI/` RSS feed or API.
    4. Database Schema: Articles must be logged with `publishedDate`, `title`, `abstract`, `url`, `themeArea`, and `hashtags`.
    5. Theming & Tagging: Articles must be categorized into primary themes ("Web Development", "Software Development", "Data Science", "Other"). Hashtags should be specific topics (e.g., #LLM, #FrontendAI).
    6. Personalization: Implement a feature where the user can input their project context (e.g., "I develop TikTok copy for pets") and the AI will generate specific "Use Cases" for the fetched article based on that context.
    7. User Features: Implement NextAuth.js for user profiles. Users can "favorite/like" publications, download the original PDF, and view their saved list.
    8. AI Chat: Integrate a lightweight chat interface on the article page where the user can ask questions about the paper for simple explanations.
</guidelines>
```

<process_steps>
Step 1: Database Setup. Define the Prisma schema (`schema.prisma`) including User, Account, Session, and Article models. Ensure you include necessary foreign key constraints, indexes, and a 'locale' field for i18n.
Step 2: Article Fetching & Processing Logic. Write the Vercel Cron Job logic (`/api/cron/fetch-articles/route.ts`) to pull from arXiv and pass the abstracts through the Claude API to generate themes, tags, and simplified summaries. Include granular error handling, retry logic, and distributed locks to prevent duplicate cron executions.
Step 3: Frontend Views. Develop the main feed page, the specific article details page, and the user profile (favorites) page. Ensure UI supports EN language.
Step 4: AI Context & Chat. Implement the component and API route for the AI Chat and the "Contextual Use Case" generator.
Step 5: Mermaid Schema & Prompt Generation. Ensure the Claude API call for article processing outputs a Mermaid.js schema of the paper's core idea and 3 practical prompt examples based on the conclusion. Provide explicit escaping rules and validation details for parsing Claude API responses safely.
</process_steps>

<formatting_rules>
When writing the Claude API processing logic, instruct Claude to respond strictly using the JSON format below to ensure our app can easily parse the structured data. Do not allow conversational filler in the output.

<example_json_output>
{
  "themeArea": "Web Development",
  "hashtags": ["#AI", "#WebDev", "#Frontend"],
  "simplifiedExplanation": "This paper explains how to make websites load faster using predictive AI.",
  "mermaidSchema": "graph TD;\n A[User clicks] --> B[AI predicts next action];\n B --> C[Preloads data];",
  "promptExamples": [
    "Write a function that implements predictive preloading based on user hover state."
  ]
}
</example_json_output>
</formatting_rules>

Execute the process steps sequentially and provide the code implementation for the MVP.
