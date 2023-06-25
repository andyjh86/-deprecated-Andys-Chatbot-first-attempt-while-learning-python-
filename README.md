##################################################################

Keeping this here to remind myself how much I learned from doing this. This was well before Llamas based LLM's and quantasization was common.

I'm now working on a much better version using llama-cpp-python

##################################################################

The code uses a DialoGPT-medium model from the Hugging Face Transformers library to generate responses to user inputs. The model is stored locally on the machine and is loaded using the "from_pretrained" method. This method retrieves the model from the Hugging Face model hub if it is not found in the specified cache directory. The cache directory for both the tokenizer and the model are set to "C:/Zoo/tokenizer-cache" and "C:/Zoo/model-cache", respectively.

The code also saves the upvote and downvote counts for each bot response in a CSV file located at "C:/Zoo/Voting/votes.csv". If the file does not exist, it is created and initialized with a header row. If it does exist, the upvote and downvote counts are updated based on user feedback.

When the user enters a message and presses the "Get Response" button or hits Enter, the code calls the "get_response" function. This function takes the user's input and passes it to the model to generate a response. The response is then displayed in the conversation text widget. If the response has been previously downvoted, the code selects the next best response from a CSV file of previous responses. If there are no previous responses or if all of the responses have been downvoted, the code generates a fallback response.

The upvote and downvote buttons allow the user to rate the quality of the bot's response. If the user finds the response helpful or interesting, they can click the upvote button. Clicking the upvote button increments the upvote count associated with that response in the CSV file. Similarly, the user can click the downvote button if they find the response unhelpful or irrelevant. Clicking the downvote button adds the response to a set of downvoted responses and increments the downvote count associated with that response in the CSV file.

Overall, the upvote and downvote buttons provide a way for the chatbot to learn from user feedback and improve the quality of its responses over time.
