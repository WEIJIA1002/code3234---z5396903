import openai
import pandas as pd

# Set your OpenAI API key globally
OPENAI_API_KEY = "sk-proj-D6YTEewe0KCf88DmKIyoT3BlbkFJMX2rz39MUJ4J3OrbUDt6"
openai.api_key = OPENAI_API_KEY

def read_csv(file_path):
    """Read CSV file and return DataFrame."""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def generate_prompt(df, custom_prompt):
    """Generate a prompt for OpenAI based on user input."""
    sample_data = df.head(10).to_csv(index=False)  # Convert a sample of the data to text
    prompt = f"""
    Here is a sample of a CSV dataset:

    {sample_data}

    {custom_prompt}
    """
    return prompt

def analyze_csv_with_openai(file_path, custom_prompt):
    """Send CSV data to OpenAI API for analysis."""
    df = read_csv(file_path)
    if df is None:
        return "Failed to read CSV file."

    prompt = generate_prompt(df, custom_prompt)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-2024-04-09",  # You can use "gpt-3.5-turbo" if needed
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error in OpenAI API request: {e}"

if __name__ == "__main__":
    file_path = input("Enter the path to your CSV file: ")
    custom_prompt = input("Enter your custom analysis prompt: ")

    result = analyze_csv_with_openai(file_path, custom_prompt)
    print("\nAnalysis Result:\n")
    print(result)
