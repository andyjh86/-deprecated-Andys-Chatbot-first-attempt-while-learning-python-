import csv
import os.path
import tkinter as tk
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="C:/Zoo/tokenizer-cache", padding_side='left')
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir="C:/Zoo/model-cache")
chat_history_ids = torch.tensor([])
downvoted_responses = set()

def get_response(event=None):
    global chat_history_ids, downvoted_responses
    # Get the message from the entry box
    message = entry.get()
    # Insert the message in the text widget
    conversation.insert(tk.END, f"You: {message}\n")
    # Encode the user input
    input_ids = tokenizer.encode(message + tokenizer.eos_token, return_tensors="pt")
    # concatenate new user input with chat history (if there is)
    bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1) if len(chat_history_ids) > 0 else input_ids

    # generate a bot response with filter
    attempts = 5
    response_scores = []
    for attempt in range(attempts):
        temperature = 0.75 + attempt * 0.1
        chat_history_ids = model.generate(
            bot_input_ids,
            max_length=1000,
            do_sample=True,
            top_k=100,
            temperature=temperature,
            pad_token_id=tokenizer.eos_token_id
        )
        # print the output
        response_text = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        if response_text not in downvoted_responses:
            # Insert the response in the text widget
            conversation.insert(tk.END, f"Bot: {response_text}\n")
            response_scores.append([response_text, attempt, 0])
            break
    else:
        # No acceptable response, select the one with lowest downvotes
        response_scores = []
        for response in downvoted_responses:
            score = [response, attempts, 0]
            with open("C:/Zoo/Voting/votes.csv", 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[:2] == [message, response]:
                        upvotes = int(row[2])
                        downvotes = int(row[3])
                        score[2] = downvotes
                        break
            response_scores.append(score)
        response_scores.sort(key=lambda s: (s[1], s[2]))
        response_text = response_scores[0][0]
        # Insert the response in the text widget
        conversation.insert(tk.END, f"Bot: {response_text} (using fallback)\n")

    # Clear the entry box
    entry.delete(0, tk.END)
    # Move the view to the end of the text widget
    conversation.see(tk.END)

    # Save and load upvotes for the bot's responses
    voting_file = "C:/Zoo/Voting/votes.csv"
    response = [message, response_text]
    if os.path.isfile(voting_file):
        with open(voting_file, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            for row in rows:
                if row[:2] == response:
                    upvotes = int(row[2])
                    downvotes = int(row[3])
                    break
            else:
                upvotes = 0
                downvotes = 0
    else:
        upvotes = 0
        downvotes = 0
        with open(voting_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Input', 'Response', 'Upvotes', 'Downvotes'])

    def write_votes(rows):
        with open(voting_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Input', 'Response', 'Upvotes', 'Downvotes'])
            writer.writerows(rows)

    def on_upvote():
        with open(voting_file, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            for i, row in enumerate(rows):
                if row[:2] == response:
                    rows[i][2] = str(int(rows[i][2]) + 1)
                    write_votes(rows)
                    break
            else:
                rows.append([message, response_text, '1', '0'])
                write_votes(rows)

    def on_downvote():
        downvoted_responses.add(response_text)
        with open(voting_file, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            for i, row in enumerate(rows):
                if row[:2] == response:
                    rows[i][3] = str(int(rows[i][3]) + 1)
                    write_votes(rows)
                    break
            else:
                rows.append([message, response_text, '0', '1'])
                write_votes(rows)

    # Update the upvote and downvote button commands
    upvote_button.config(command=on_upvote)
    downvote_button.config(command=on_downvote)

    # Move the view to the end of the text widget
    conversation.see(tk.END)


 # Create the main window
root = tk.Tk()
root.geometry("600x450")
root.title("Andy's Chatbot GUI")

 # Create a Text widget to show the conversation history
conversation = tk.Text(root)
conversation.pack(expand=True, fill='both')

 # Create an entry box
entry = tk.Entry(root)
entry.pack()

# Create a button
button = tk.Button(root, text="Get Response", command=get_response)
button.pack()

# Create upvote and downvote buttons
upvote_button = tk.Button(root, text='Upvote')
upvote_button.pack(side='left')
downvote_button = tk.Button(root, text='Downvote')
downvote_button.pack(side='right')

 # bind the enter key to the entry box
root.bind('<Return>', get_response)

# Start the main event loop
root.mainloop()
