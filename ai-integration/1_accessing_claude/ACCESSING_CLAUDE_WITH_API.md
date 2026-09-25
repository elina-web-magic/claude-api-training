# Accessing Claude with the API

When building applications with Claude, understanding the complete request lifecycle helps you make better architectural decisions and debug issues more effectively. Let's walk through what happens from the moment a user clicks "send" in your chat interface to when Claude's response appears on screen.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623274%2F03_-_001_-_Accessing_the_API_01.1748623274598.png)

---

## The Five-Step Request Flow

Every interaction with Claude follows a predictable pattern with five distinct phases: request to server, request to Anthropic API, model processing, response to server, and response to client.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623275%2F03_-_001_-_Accessing_the_API_03.1748623275310.png)

---

## Why You Need a Server

You should never make requests to the Anthropic API directly from client-side code. Here's why:

- API requests require a secret API key for authentication  
- Exposing this key in client code creates a serious security vulnerability  
- Anyone could extract the key and make unauthorized requests

Instead, your web or mobile app sends requests to your own server, which then communicates with the Anthropic API using the securely stored key.

---

## Making API Requests

When your server contacts the Anthropic API, you can use either an official SDK or make plain HTTP requests. Anthropic provides SDKs for Python, TypeScript, JavaScript, Go, and Ruby.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623276%2F03_-_001_-_Accessing_the_API_05.1748623276722.png)  
Every request must include these essential fields:

- API Key - Identifies your request to Anthropic  
- Model - Name of the model to use (like "claude-3-sonnet")  
- Messages - List containing the user's input text  
- Max Tokens - Limit for how many tokens Claude can generate

---

## Inside Claude's Processing

Once Anthropic receives your request, Claude processes it through four main stages: tokenization, embedding, contextualization, and generation.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623277%2F03_-_001_-_Accessing_the_API_08.1748623277503.png)

### Tokenization

Claude first breaks your input text into smaller chunks called tokens. These can be whole words, parts of words, spaces, or symbols. For simplicity, think of each word as one token.

### Embedding

Each token gets converted into an embedding - a long list of numbers that represents all possible meanings of that word. Think of embeddings as numerical definitions that capture semantic relationships.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623278%2F03_-_001_-_Accessing_the_API_10.1748623278148.png)  
Words often have multiple meanings. For example, "quantum" could refer to:

- A discrete unit of physical quantity (physics)  
- Quantum mechanics or quantum physics concepts  
- Something extremely small or subatomic  
- Quantum computing applications

### Contextualization

Claude refines each embedding based on surrounding words to determine the most likely meaning in context. This process adjusts the numerical representations to highlight the appropriate definition.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623278%2F03_-_001_-_Accessing_the_API_11.1748623278717.png)

### Generation

The contextualized embeddings pass through an output layer that calculates probabilities for each possible next word. Claude doesn't always pick the highest probability word - it uses a mix of probability and controlled randomness to create natural, varied responses.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623279%2F03_-_001_-_Accessing_the_API_13.1748623279317.png)  
After selecting each word, Claude adds it to the sequence and repeats the entire process for the next word.

---

## When Claude Stops Generating

After each token, Claude checks several conditions to decide whether to continue:

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623280%2F03_-_001_-_Accessing_the_API_15.1748623279963.png)

- Max tokens reached - Has it hit the limit you specified?  
- Natural ending - Did it generate an end-of-sequence token?  
- Stop sequence - Did it encounter a predefined stop phrase?

---

## The API Response

When generation completes, the API sends back a structured response containing:

- Message - The generated text  
- Usage - Count of input and output tokens  
- Stop Reason - Why generation ended

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623281%2F03_-_001_-_Accessing_the_API_17.1748623281653.png)  
Your server receives this response and forwards the generated text back to your client application, where it appears in the user interface.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623282%2F03_-_001_-_Accessing_the_API_19.1748623282180.png)

---

## Key Takeaways

Understanding this flow helps you:

- Design secure architectures that protect your API keys  
- Set appropriate token limits for your use case  
- Handle different stop reasons in your application logic  
- Debug issues by understanding where they might occur in the pipeline

Don't worry about memorizing every detail - the goal is familiarizing yourself with the terminology and overall process you'll encounter when working with Claude's API.

---

## Getting an API key

In the next video we will be making a request to the Anthropic API. To do so, you will need a secret API key. This guide will walk you through the process of creating an API key.

### Step One: Navigate to the Anthropic API Console

In your browser, navigate to [https://console.anthropic.com/](https://console.anthropic.com/) and log in to your Anthropic account. You'll then see a page like this:

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846091%2FScreenshot+2025-06-13+at+2.20.45%E2%80%AFPM.1749846091092.png)

### Step Two: Click the 'Get API Keys' button

This button can be found towards the top right of the main dashboard page.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846107%2FScreenshot+2025-06-13+at+2.21.16%E2%80%AFPM.1749846106943.png)

### Step Three: Click the 'Create Key' button

At the top right of the page, find the 'Create Key' button and click it.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846149%2FScreenshot+2025-06-13+at+2.22.10%E2%80%AFPM.1749846149203.png)

### Step Four: Enter a workspace and name for your key

Create the key in workspace 'Default' and enter a name for your key. This name is used to help you identify the keys you generate. Let's use a name of 'Anthropic Course'.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846167%2FScreenshot+2025-06-13+at+2.22.14%E2%80%AFPM.1749846166954.png)

### Step Five: Copy the Key

Your API key will then be displayed in a pop up window. Copy this key and hold onto it - we will use it in the next video. This key will only be displayed once, so make sure you copy it!

If you accidentally close the window, delete the old key and generate it again.

---

## Making a request

Making your first request to the Anthropic API is straightforward once you understand the basic setup and structure. This guide walks through the essential steps to get Claude responding to your prompts using Python.

### Setting Up Your Environment

Before making any API calls, you need to install the required packages and configure your API key securely.

First, install the necessary dependencies in your Jupyter notebook:

```bash
%pip install anthropic python-dotenv```Next, create a **.env** file in the same directory as your notebook to store your API key securely:```env
ANTHROPIC_API_KEY="your-api-key-here"```This approach keeps your API key out of your code and prevents accidentally committing it to version control. Always add **.env** to your **.gitignore** file.

Load the environment variables and create your API client:```python
from dotenv import load_dotenv  
load_dotenv()

from anthropic import Anthropic

client = Anthropic()

model = "claude-sonnet-4-0"```---

## The Create Function

The core of making API requests is the **client.messages.create()** function. This function requires three key parameters:

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623269%2F03_-_003_-_Making_a_Request_09.1748623269461.png)

- model - The name of the Claude model you want to use  
- max_tokens - A safety limit on response length (not a target)  
- messages - The conversation history you're sending to Claude

The **max_tokens** parameter acts as a safety mechanism. If you set it to 1000, Claude will stop generating after 1000 tokens even if it has more to say. Claude doesn't try to reach this limit - it just writes what it thinks is appropriate and stops if it hits the maximum.

### Understanding Messages

Messages represent the conversation between you and Claude, similar to a chat application. There are two types of messages:

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623270%2F03_-_003_-_Making_a_Request_13.1748623270369.png)

- User messages - Content you want to send to Claude (written by humans)  
- Assistant messages - Responses that Claude has generated

Each message is a dictionary with a **role** (either "user" or "assistant") and **content** (the actual text).

---

## Making Your First Request

Here's a complete example of making a request to Claude:```python
message = client.messages.create(  
    model=model,  
    max_tokens=1000,  
    messages=[  
        {  
            "role": "user",  
            "content": "What is quantum computing? Answer in one sentence"  
        }  
    ]
)```When you run this code, Claude will process your request and return a response object containing the generated text along with metadata about the request.

### Extracting the Response

The response object contains a lot of information, but you usually just want the generated text. Access it using:```python
message.content[0].text```This gives you clean, readable output like: "Quantum computing is a type of computation that leverages quantum mechanics principles like superposition and entanglement to process information using quantum bits (qubits), potentially solving certain complex problems exponentially faster than classical computers."

With these basics in place, you can start experimenting with different prompts and building more complex interactions with Claude.

---

## Multi-Turn conversations

When working with the Anthropic API and Claude, there's a crucial concept you need to understand: Claude doesn't store any of your conversation history. Each request you make is completely independent, with no memory of previous exchanges.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623270%2F03_-_004_-_Multi-Turn_Conversations_01.1748623269971.png)  
This means if you want to have a multi-turn conversation where Claude remembers context from earlier messages, you need to handle the conversation state yourself.

### The Problem with Stateless Conversations

Let's say you ask Claude "What is quantum computing?" and get a good response. Then you follow up with "Write another sentence" - Claude has no idea what you're referring to. It will write a sentence about something completely random because it has no memory of the quantum computing discussion.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623270%2F03_-_004_-_Multi-Turn_Conversations_02.1748623270625.png)

### How Multi-Turn Conversations Work

To maintain conversation context, you need to do two things:

- Manually maintain a list of all messages in your code  
- Send the complete message history with every request

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623271%2F03_-_004_-_Multi-Turn_Conversations_05.1748623271251.png)  
Here's the flow that actually works:

1. Send your initial user message to Claude  
2. Take Claude's response and add it to your message list as an assistant message  
3. Add your follow-up question as another user message  
4. Send the entire conversation history to Claude

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623271%2F03_-_004_-_Multi-Turn_Conversations_08.1748623271832.png)

### Building Helper Functions

To make conversation management easier, you can create three helper functions:```python
def add_user_message(messages, text):  
    user_message = {"role": "user", "content": text}  
    messages.append(user_message)

def add_assistant_message(messages, text):  
    assistant_message = {"role": "assistant", "content": text}  
    messages.append(assistant_message)

def chat(messages):  
    message = client.messages.create(  
        model=model,  
        max_tokens=1000,  
        messages=messages,  
    )

    return message.content[0].text```### Putting It All Together

Here's how you use these functions to maintain a conversation:

\# Start with an empty message list  
messages = []

\# Add the initial user question  
add_user_message(messages, "Define quantum computing in one sentence")

\# Get Claude's response  
answer = chat(messages)

\# Add Claude's response to the conversation history  
add_assistant_message(messages, answer)

\# Add a follow-up question  
add_user_message(messages, "Write another sentence")

\# Get the follow-up response with full context

final_answer = chat(messages)

Now Claude will understand that "Write another sentence" refers to expanding on the quantum computing definition, because you've provided the complete conversation context.

These helper functions will be useful throughout your work with Claude, making it much easier to build applications that can maintain meaningful conversations over multiple exchanges.

---

## System prompts

System prompts are a powerful way to customize how Claude responds to user input. Instead of getting generic answers, you can shape Claude's tone, style, and approach to match your specific use case.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623273%2F03_-_006_-_System_Prompts_00.1748623272065.png)

### Why System Prompts Matter

Consider building a math tutor chatbot. When a student asks "How do I solve 5x \+ 2 = 3 for x?", you want Claude to act like a real tutor, not just spit out the answer. A good math tutor should:

- Initially give hints rather than complete solutions  
- Patiently walk students through problems step by step  
- Show solutions for similar problems as examples

You definitely don't want Claude to:

- Immediately give direct answers  
- Tell students to just use a calculator

### How System Prompts Work

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623273%2F03_-_006_-_System_Prompts_05.1748623273817.png)  
System prompts provide Claude with guidance on how to respond. You define them as plain strings and pass them into the create function call. The key benefits are:

- System prompts provide Claude guidance on how to respond  
- Claude will try to respond in the same way someone in the specified role would respond  
- Helps keep Claude on task

Here's the basic structure:```python
system_prompt = """  
You are a patient math tutor.  
Do not directly answer a student's questions.  
Guide them to a solution step by step.  
"""

client.messages.create(  
    model=model,  
    messages=messages,  
    max_tokens=1000,  
    system=system_prompt
)```### Seeing the Difference

Without a system prompt, Claude gives a complete step-by-step solution immediately. This might be helpful, but it doesn't encourage the student to think through the problem themselves.

With the math tutor system prompt, Claude's response changes dramatically. Instead of providing the full solution, Claude asks guiding questions like "What do you think would be a good first step to isolate x? Consider what operation we might need to perform on both sides to start moving terms around."

### Building a Flexible Chat Function

Rather than hard-coding system prompts, you can make your chat function more reusable by accepting system prompts as parameters:```python
def chat(messages, system=None):  
    params = {  
        "model": model,  
        "max_tokens": 1000,  
        "messages": messages,  
    }  

    if system:  
        params["system"] = system  
      
    message = client.messages.create(**params)

    return message.content[0].text```This approach handles an important detail: Claude's API doesn't accept **system=None**, so you need to conditionally include the system parameter only when it's provided.

Now you can call your chat function with or without a system prompt:

\# Without system prompt  
answer = chat(messages)

\# With system prompt  
system = """  
You are a patient math tutor.  
Do not directly answer a student's questions.  
Guide them to a solution step by step.  
"""

answer = chat(messages, system=system)

System prompts are essential for creating AI applications that behave consistently and appropriately for their intended purpose. They transform generic AI responses into specialized, role-appropriate interactions.

---

## Temperature

Temperature is a powerful parameter that controls how predictable or creative Claude's responses will be. Understanding how to use it effectively can dramatically improve your AI applications.

### How Claude Generates Text

Before diving into temperature, it helps to understand Claude's text generation process. When you send Claude a prompt like "What do you think?", it goes through three key steps:

- Tokenization - Breaking your input into smaller chunks  
- Prediction - Calculating probabilities for possible next words  
- Sampling - Choosing a token based on those probabilities

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623338%2F03_-_008_-_Temperature_00.1748623338635.png)  
In this example, Claude might assign a 30% probability to "about", 20% to "would", 10% to "of", and so on. The model then selects one token and repeats this entire process to build complete sentences.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623339%2F03_-_008_-_Temperature_05.1748623339740.png)

### What Temperature Does

Temperature is a decimal value between 0 and 1 that directly influences these selection probabilities. It's like adjusting the "creativity dial" on Claude's responses.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623340%2F03_-_008_-_Temperature_06.1748623340446.png)  
At low temperatures (near 0), Claude becomes very deterministic - it almost always picks the highest probability token. At high temperatures (near 1), Claude distributes probability more evenly across options, leading to more varied and creative outputs.

### Interactive Temperature Demo

You can see temperature in action with Claude's interactive demo. Watch how the probability distribution changes as you adjust the temperature slider:

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623341%2F03_-_008_-_Temperature_07.1748623341049.png)  
At temperature 0.0, "about" gets 100% probability - completely deterministic. At temperature 1.0, probabilities spread more evenly across all possible tokens, introducing randomness and creativity.

### Choosing the Right Temperature

Different tasks call for different temperature ranges:

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623341%2F03_-_008_-_Temperature_10.1748623341732.png)

### Low Temperature (0.0 - 0.3)

- Factual responses  
- Coding assistance  
- Data extraction  
- Content moderation

### Medium Temperature (0.4 - 0.7)

- Summarization  
- Educational content  
- Problem-solving  
- Creative writing with constraints

### High Temperature (0.8 - 1.0)

- Brainstorming  
- Creative writing  
- Marketing content  
- Joke generation

### Implementing Temperature in Code

Adding temperature support to your chat function is straightforward. Here's how to modify your existing function:```python
def chat(messages, system=None, temperature=1.0):  
    params = {  
        "model": model,  
        "max_tokens": 1000,  
        "messages": messages,  
        "temperature": temperature  
    }  

    if system:  
        params["system"] = system  
      
    message = client.messages.create(**params)

    return message.content[0].text```The key changes are adding **temperature=1.0** as a parameter and including **"temperature": temperature** in the params dictionary.

### Testing Temperature Effects

To see temperature in action, try generating movie ideas with different settings:

\# Low temperature - more predictable  
answer = chat(messages, temperature=0.0)

\# High temperature - more creative  

answer = chat(messages, temperature=1.0)

At temperature 0.0, you might consistently get responses like "A time-traveling archaeologist must prevent ancient artifacts from being stolen." At temperature 1.0, you'll see much more variety in themes, characters, and plot elements.

### Key Takeaways

Remember that temperature doesn't guarantee different outputs - it just changes the probability of getting them. Even at high temperatures, Claude might occasionally produce similar responses. The key is matching your temperature choice to your specific use case:

- Need consistent, factual responses? Use low temperature  
- Want creative brainstorming? Dial up the temperature  
- Somewhere in between? Medium temperatures work well for most general tasks

Temperature is one of the most practical parameters you can adjust to fine-tune Claude's behavior for your specific needs.

---

## Structured data

When you need Claude to generate structured data like JSON, Python code, or bulleted lists, you'll often run into a common problem: Claude wants to be helpful and add explanatory text around your content. While this is usually great, sometimes you need just the raw data with nothing else.

Consider building a web app that generates AWS EventBridge rules. Users enter a description, click generate, and expect to see clean JSON they can immediately copy and use. If Claude returns the JSON wrapped in markdown code blocks with explanatory text, users can't simply copy the entire response - they have to manually select just the JSON portion.

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623326%2F03_-_011_-_Structured_Data_02.1748623325858.png)

---

## The Problem with Default Responses

By default, when you ask Claude to generate JSON, you might get something like this:

\`\`\`json  
{  
  "source": ["aws.ec2"],  
  "detail-type": ["EC2 Instance State-change Notification"],  
  "detail": {  
    "state": ["running"]  
  }  
}  
\`\`\`This rule captures EC2 instance state changes when instances start running.

The JSON is correct, but it's wrapped in markdown formatting and includes explanatory text. For a web app where users need to copy the raw JSON, this creates friction in the user experience.

---

## The Solution: Assistant Message Prefilling \+ Stop Sequences

You can combine assistant message prefilling with stop sequences to get exactly the content you want. Here's how it works:

messages = []

add_user_message(messages, "Generate a very short event bridge rule as json")  
add_assistant_message(messages, "\`\`\`json")

text = chat(messages, stop_sequences=["\`\`\`"])

This technique works by:

1. The user message tells Claude what to generate  
2. The prefilled assistant message makes Claude think it already started a markdown code block  
3. Claude continues by writing just the JSON content  
4. When Claude tries to close the code block with **\`\`\`**, the stop sequence immediately ends generation

![image](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623327%2F03_-_011_-_Structured_Data_15.1748623326804.png)  
The result is clean JSON with no extra formatting:

{  
  "source": ["aws.ec2"],  
  "detail-type": ["EC2 Instance State-change Notification"],  
  "detail": {  
    "state": ["running"]  
  }

}

### Processing the Response

You might notice some extra newline characters in the response. These are easy to handle:

import json

\# Clean up and parse the JSON

clean_json = json.loads(text.strip())

### Beyond JSON

This technique isn't limited to JSON generation. Use it anytime you need structured data without commentary:

- Python code snippets  
- Bulleted lists  
- CSV data  
- Any formatted content where you want just the content, not explanations

The key is identifying what Claude naturally wants to wrap your content in, then using that as your prefill and stop sequence. For code, it's usually markdown code blocks. For lists, it might be different formatting markers.

This approach gives you precise control over Claude's output format, making it much easier to integrate AI-generated content into applications where clean, structured data is essential.
