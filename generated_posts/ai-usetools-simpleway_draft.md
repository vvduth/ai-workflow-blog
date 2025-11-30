# Building an AI Agent with Tool-Calling Capability

## Introduction

Imagine an AI agent smart enough to fetch the weather, perform calculations, or assist you with everyday questions, all through a simple interaction. Today, we'll explore building such an AI agent using a specific tool: `get_temperature(city: str) -> float`. This tool allows our AI to fetch current temperatures for any given city. By the end of this post, you'll know how to integrate this tool with intelligent decision-making, allowing the AI to either use the tool or answer directly based on user input.

## The Simple Implementation

Let's start with a basic implementation:

```python
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from a .env file (such as API keys)
load_dotenv()

# Initialize the OpenAI client
client = OpenAI()   

def get_temperature(city: str) -> float:
    """
    Get the current temperature for a given city.
    """
    # This is a placeholder implementation
    return 25.0

def main():
    user_input = input("Your question: ")
    prompt = f"""
    You are a helpful assistant. Answer user's question in a friendly manner.
    
    You can also use tools if you feel like they help you provide a better answer.
    - get_temperature(city: str) -> float: Get the current temperature for a given city.
    
    If you want to use one of these tools, you should output the tool name and its arguments in the following format:
     tool_name: arg1, arg2,...
    
    For example, if the user asks "What is the current temperature in New York?", you should respond with:
        get_temperature: New York
    With that in mind, answer the user's question: 
    <user-question>{user_input}</user-question>
    
    If you requested a tool, please output ONLY the tool call (as shown above) and nothing else.
    """
    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
    )
    reply = response.output_text
    if reply.startswith("get_temperature:"):
        arg = reply.split("get_temperature:")[1].strip()
        temperature = get_temperature(arg)
        prompt = f"""
            You are a helpful assistant. Answer user's question in a friendly manner.
            Here is user question: 
            <user-question>{user_input}</user-question>
            You requested to use the get_temperature tool with argument: "{arg}"
            Here is the result from the tool: 
            The current temperature in {arg} is {temperature}°C.
        """
        response = client.responses.create(
            model="gpt-4o",
            input=prompt,
        )
        reply = response.output_text
        print(reply)
    else:
        print(reply)
    
if __name__ == "__main__":
    main()
```

This setup enables a basic AI interaction where the AI decides to call the `get_temperature` tool based on the input it receives.

## Enhancing with OpenAI Function Calling

To make our AI agent more versatile, we can utilize OpenAI's function-calling feature, which allows the agent to decide when to interact with different tools based on the conversation context.

### Understanding AI Function Calls

Function calls enable the AI to invoke specific functions during a conversation. This method not only enriches the AI's capabilities but also integrates smoothly with existing workflows. Here's how we set it up:

### Setup

- **available_functions**: A dictionary mapping available tool names to their corresponding Python functions.
- **messages array**: Keeps track of the conversation for context.
- **tools**: Describes the JSON schema for each tool.

#### Implementation

```python
import json

def get_temperature(city: str) -> float:
    # A simple placeholder to simulate temperature retrieval
    return 25.0

available_functions = {
    "get_temperature": get_temperature,
}

tools = [
    {
        "type": "function",
        "name": "get_temperature",
        "description": "Get the current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get the temperature for.",
                },
            },
            "additionalProperties": False,
            "required": ["city"],
        },
    }
]

def execute_tool_call(tool_call) -> str:
    """Execute a tool call and return the result."""
    fn_name = tool_call.name
    fn_args = json.loads(tool_call.arguments)

    if fn_name in available_functions:
        function_to_call = available_functions[fn_name]
        try: 
            return function_to_call(**fn_args)
        except Exception as e:
            return f"Error executing {fn_name}: {str(e)}"
    
    return f"Function {fn_name} not found."

def main():
    messages = [
        {
            "role": "developer",
            "content": "You are a helpful assistant. Answer user's question in a friendly manner. You can also use tools if you feel like they help you provide a better answer.",
        }
    ]
    while True:
        user_input = input("Your question (type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
            
        messages.append({"role": "user", "content": user_input})
        
        response = client.responses.create(
            model="gpt-4o",
            input=messages,
            tools=tools,
        )
        output = response.output[0]
        messages.append(output)  # Add to chat history
        
        if output.type != "function_call":
            print(response.output_text)
            continue
        tool_output = execute_tool_call(output)
        messages.append({
            "type": "function_call_output",
            "call_id": output.call_id,
            "output": str(tool_output),
        })
        response = client.responses.create(
            model="gpt-4o",
            input=messages,
        )
        print(response.output_text)
    
    print(messages)

if __name__ == "__main__":
    main()
```

## Conclusion

Try out this setup by running the code and asking questions like "What's the temperature in Tokyo?" Watch as the AI agent smartly uses the `get_temperature` tool to provide accurate results. This approach boosts the interactivity of AI agents and incorporates real-world functionalities seamlessly.