import google.generativeai as genai
import pandas as pd
import os
import time

def read_text_file(file_path):
    # Function to read the content of a text file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return ""

def ask_llm(content, questions):
    # Function to ask the LLM model questions and get the answers
    genai.configure(api_key="AIzaSyBYotb1Lw7e6WOTZOawf4JrQ7G0dqWkJCU")
    model = genai.GenerativeModel("gemini-2.0-flash")
    row = []
    for question in questions: # Getting each question from the array and asking the model
        # Giving the prompt that should be asked to the model
        prompt = f"""
        Given the following company information:{content}
        Answer the following question :{question}
        """
        try:
            response = model.generate_content(prompt)
            # Check if the response is valid and not blocked
            if response and hasattr(response, 'candidates'):
                row.append(response.text.strip() if response.text else "No valid response.")
            else:
                row.append("Response blocked or no valid output.")
        except ValueError as e:
            if "finish_reason" in str(e):
                row.append("Response blocked due to copyrighted content.")
            else:
                row.append(f"Error: {e}")
        except Exception as e:
            row.append(f"Unexpected error: {e}")
        time.sleep(4)  # Adding delay to avoid quota limit
    return row

def save_to_excel(all_answers, questions, output_file): # Function to save the extracted answers to an Excel file
    df = pd.DataFrame(all_answers, columns=questions)
    df.to_excel(output_file, index=False)
    print(f"Answers saved to {output_file}")

def main():
    input_folder = "website_contents"  # Folder containing scraped website content
    output_file = "company_info.xlsx" #File to save the extracted company information from LLM model
    questions = [
        "What is the company's mission statement or core values?",
        "What products or services does the company offer?",
        "When was the company founded, and who were the founders?",
        "Where is the company's headquarters located?",
        "Who are the key executives or leadership team members?",
        "Has the company received any notable awards or recognitions?"
    ]
    
    all_answers = []
    
    for filename in os.listdir(input_folder):#loop to read each file in the folder
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            content = read_text_file(file_path)#reading the content of the file
            
            if not content:
                print(f"Skipping {filename} due to empty content.")
                continue
            
            answers = ask_llm(content, questions)
            all_answers.append(answers)
            
            print(f"Processed {filename}")
            time.sleep(5)  # Adding delay between file processing to avoid hitting quota limits
    
    if all_answers:
        save_to_excel(all_answers, questions, output_file)
    else:
        print("No valid content to save.")

if __name__ == "__main__":
    main()
