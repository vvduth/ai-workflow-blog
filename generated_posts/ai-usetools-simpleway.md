## Build an ai agent that use one tool:
* today we build a simple ai agent that can use one tool: get_tempature(city: str) -> float: Get the current temperature for a given city.
* the ai agent can decide when to use the tool and when to answer directly.

## the simple way:

```python
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()   

def get_tempature(city: str) -> float:
    """
    Get the current temperature for a given city.
    """
    # Dummy implementation for illustration
    return 25.0

def main():
    user_input = input("Your question: ")
    prompt = f"""
    you are a helpful assistant. Answer user's question in a friendly manner.
    
    You can also use tools if you feel like they help you provide a better answer.
    - get_tempature(city: str) -> float: Get the current temperature for a given city.
    
    If you want to use one of these tools, you should output the tool name and its areguments in the following format:
     tool_name: arg1, arg2,...
    
    For example, if the user asks "What is the current temperature in New York?", you should respond with:
        get_tempature: New York
    With that in mind, answer the user's question : 
    <user-question>{user_input}</user-question>
    
    if you requested a tool, please output ONLY the tool call (as shown above) and nothing else.
    """
    response = client.responses.create(
        model = "gpt-4o",
        input=prompt,
    )
    reply = response.output_text
    if reply.startswith("get_tempature:"):
        arg = reply.split("get_tempature:")[1].strip()
        temperature = get_tempature(arg)
        prompt = f"""
            Ypu are a helpful assistant. Answer user's question in a friendly manner.
            Here is user question: 
            <user-question>{user_input}</user-question>
            You requested to use the get_tempature tool with argument: "{arg}"
            Here is the result from the tool: 
            The current temperature in {arg} is {temperature}°C.
        """
        response = client.responses.create(
            model = "gpt-4o",
            input=prompt,
        )
        reply = response.output_text
        print(reply)
    else :
        print(reply)
    
if __name__ == "__main__":
    main()
```
this code implements a simple ai agent that can use the get_tempature tool. the agent first generates a response based on the user input. if the response indicates a tool call, the tool is executed, and the result is fed back into the agent to generate a final answer.

## get more cokplicated with open ai function calling:
many ai provider has built in support for function calling, which makes it easier to build ai agents that can use tools. the name and the way of implementation may vary, but the basic idea is the same: you define the functions (tools) that the ai can use, and the ai will decide when to call them based on the conversation context.

this proiject we will go with open ai function calling as an example.
dont mitake with function calling with the tool secttion support in open ai docs. Tools here refer to tools that are running on open ai server (So tools/functions written by the OpenAI developers.) this can be useful but is limited to the tools provided by open ai. in this project we will focus on building our own tools and integrating them with open ai function calling.
from the docs we can see we cann pass the tools as an arg into the chat completion create method. (they are all in the docs so i am not paste any code here.)

the value oif tools should be a list of tools/function descriptions in json schema format.

open ai support multiple tool calls in one conversation. the ai can decide when to call which tool based on the conversation context. ==> they is freakying dopeass and scary.

## back to our code: 
* so what to we need here? (what do I need to be exact =)) )
* I want to keep track o fthe message history so that the ai can make better decisions based on the conversation context.
* I want to add tools into the chat completion create method aka create a tools array with proper format.
* i want to handle the tool calls and execute the tools when the ai decides to use them.

so in short i will create:
- available_functions: a dict that maps function names to actual python functions. help with keep track of available tools.
- execute_tool_call(tool_call): a function that takes a tool call object, extracts the function
- messages array that will store the message history.
- tools var that hold the tool definitions in json schema format.
```python
  available_functions = {
    "get_tempature": get_tempature,
}
tools = [
    {
        "type": "function",
        "name": "get_tempature",
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
def execute_tool_call(tool_call) -> str | float:
    """ 
    execute a tool call and return the result
    """
    fn_name = tool_call.name
    fn_args = json.loads(tool_call.arguments)

    if fn_name in available_functions:
        function_to_call = available_functions[fn_name]
        try: 
            return function_to_call(**fn_args)
        except Exception as e:
            return f"Error executing {fn_name}: {str(e)}"
    
    return f"Function {fn_name} not found."
```

tweka the main function to use the messages array, tools var, and execute_tool_call function:
```python
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
        messages.append(output) # add to chat history to keep track of the conversation
        
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
            model='gpt-4o',
            input=messages,
        )
        print(response.output_text)
    
    print(messages)
```

run the code and test it out! you should be able to ask questions that require the get_tempature tool, and the ai agent will use the tool to provide accurate answers.

```bash
ducth@DucPC MINGW64 ~/git_repos/ai-workflow-blog (main)
$ uv run usetool.py
warning: `VIRTUAL_ENV=C:/Users/ducth/.virtualenvs/langchain-pdf-rxK5otlI` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
Your question (type 'exit' to quit): what can you do for me?
I can help with a lot of things! Here's a quick overview:

1. **Answer Questions:** I can provide information on a wide variety of topics, from historical events to scientific concepts.
2. **Weather Information:** I can fetch the current temperature for various locations.
....
If there's something specific you need, just let me know!
Your question (type 'exit' to quit): what is the temperature in helsinki?
The current temperature in Helsinki is 25°C. If you need more information, feel free to ask!
Your question (type 'exit' to quit): exit
[{'role': 'developer', 'content': "You are a helpful assistant. Answer user's question in a friendly manner. You can also use tools if you feel like they help you provide a better answer."}, {'role': 'user', 'content': 'what can you do for me?'}, ResponseOutputMessage(id='msg_0b6bba26b687a07200692c1f076ef88193b4a08598104b6511', content=[ResponseOutputText(annotations=[], text="I can help with a lot of things!...
```