import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise Exception("GEMINI_API_KEY not found in .env")
    
    # Generate Gemini client
    client = genai.Client(api_key=api_key)

    # Use argparser to extract question from command argument
    parser = argparse.ArgumentParser(description="Simon Code")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Store chat conversation
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    user_prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0, tools=[available_functions])
    )
    
    if response.usage_metadata == None:
        raise Exception(RuntimeError)
    
    if args.verbose:
        print(f"Response: {response}")
        print(f"System prompt: {system_prompt}")
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(f"Function calls:\n{response.function_calls}")
        print(f"Response text:\n- {response.text}")
    else:
        if response.function_calls is not None:
            for function_call in response.function_calls:
                print(f"Calling function: {function_call.name}({function_call.args})")
        elif response.function_calls is None:
            print(f"- {response.text}")


if __name__ == "__main__":
    main()
