from dotenv import load_dotenv
from openai import OpenAI
import json
load_dotenv()

client = OpenAI()   

def get_tempature(city: str) -> float:
    """
    Get the current temperature for a given city.
    """
    # Dummy implementation for illustration
    return 25.0
# keep track of  all the functions available to the model
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
if __name__ == "__main__":
    main()