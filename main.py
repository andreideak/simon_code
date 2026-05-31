import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function

def generate_content(client: genai.Client, messages: list[types.Content], verbose: bool) -> types.GenerateContentResponse:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0, tools=[available_functions])
    )
    
    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed")
    
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    return response


def main():
    # Use argparser to extract question from command argument
    parser = argparse.ArgumentParser(description="Simon Code")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise Exception("GEMINI_API_KEY not found in .env")
    
    # Generate Gemini client
    client = genai.Client(api_key=api_key)

    # Store chat conversation
    messages: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    # Limit agents loop executions to 20
    for _ in range(20):
        response = generate_content(client, messages, args.verbose)

        if not response.candidates:
            raise RuntimeError("Gemini API response contains no .candidates property (history)")
        for candidate in response.candidates:
            # Append response to messsages (chat history)
            messages.append(candidate.content)  
        
        if not response.function_calls:
            print(f"Final response: {response.text}")
            break
    
        function_responses: list[types.Part] = []
        for function_call in response.function_calls:
            result = call_function(function_call,args.verbose)
            if (
                not result.parts
                or not result.parts[0].function_response
                or not result.parts[0].function_response.response
            ): 
                raise RuntimeError(f"Empty function response for {function_call.name}")
            if args.verbose:
                print(f"-> {result.parts[0].function_response.response}") 
            function_responses.append(result.parts[0])
        # Append tool calls response to messages (chat history)
        messages.append(types.Content(role="user", parts=function_responses))
    else:
        print("Maximum iterations reached.")
        sys.exit(1)
             
        
            
        

if __name__ == "__main__":
    main()
