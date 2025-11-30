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