import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from torch.optim import AdamW

# Load the Flan-T5 model and tokenizer
tokenizer = T5Tokenizer.from_pretrained('google/flan-t5-large', legacy=False)
model = T5ForConditionalGeneration.from_pretrained('google/flan-t5-large')

# Define optimizer (AdamW is typically used for transformer models)
optimizer = AdamW(model.parameters(), lr=5e-5)

# Define loss function (cross-entropy is suitable for text generation tasks)
loss_fn = torch.nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)

# Predefined greetings
greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening", "howdy"]

# Predefined emotional responses (add more if necessary)
emotion_keywords = {
    'happy': ['happy', 'joyful', 'excited', 'glad', 'cheerful'],
    'sad': ['sad', 'unhappy', 'down', 'depressed', 'gloomy'],
    'angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed'],
    'fearful': ['fear', 'scared', 'nervous', 'worried', 'afraid'],
    'surprised': ['surprised', 'shocked', 'amazed', 'astonished', 'startled'],
}
def summarization_data(values):
    # Convert the input values into a string (assuming values is a dict or list)
    input_text = ' '.join([f"{key}: {value}" for key, value in values.items()])
    
    # Prepare the input for the Flan-T5 model
    input_ids = tokenizer("summarize: " + input_text, return_tensors="pt").input_ids
    
    # Generate a summary using the Flan-T5 model
    outputs = model.generate(input_ids, max_length=150, num_beams=4, early_stopping=True)
    
    # Decode the generated summary
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return summary


# Function for answering questions using T5 model
def get_answer(question):
    input_text = f"answer question: {question}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(inputs.input_ids, max_length=150, num_beams=5, early_stopping=True)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

# Function for generating text using T5 model
def generate_text(prompt, min_length=50, max_length=1024):
    """
    Generates text using the T5 model.
    
    Parameters:
        prompt (str): The input prompt for text generation.
        min_length (int): The minimum length of the generated text. Default is 50.
        max_length (int): The maximum length of the generated text. Default is 1024.
    """
    input_text = f"generate text: {prompt}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
    
    # Generate text with customizable min and max length
    outputs = model.generate(
        inputs.input_ids, 
        max_length=max_length, 
        min_length=min_length, 
        num_beams=5,
        early_stopping=True,
        no_repeat_ngram_size=3,
    )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text

# Function to train the model (with backpropagation)
def train_model(input_texts, target_texts, epochs=3):
    # Switch the model to training mode
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        
        for i in range(len(input_texts)):
            # Tokenize inputs and targets
            inputs = tokenizer(input_texts[i], return_tensors="pt", truncation=True, max_length=512)
            targets = tokenizer(target_texts[i], return_tensors="pt", truncation=True, max_length=512)

            # Clear previous gradients
            optimizer.zero_grad()

            # Forward pass: get model outputs
            outputs = model(input_ids=inputs.input_ids, labels=targets.input_ids)
            
            # Compute loss (using the model's built-in cross-entropy loss)
            loss = outputs.loss
            total_loss += loss.item()

            # Backward pass (compute gradients)
            loss.backward()

            # Step: Update model parameters based on gradients
            optimizer.step()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(input_texts)}")

# Function to check if the input is a greeting
def is_greeting(text):
    return text.lower().strip() in greetings

# Function to detect emotions in text and respond accordingly
def detect_emotion(text):
    text = text.lower()
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text for keyword in keywords):
            return f"I sense that you're feeling {emotion}. How can I help you with that?"
    return None  # No emotion detected

# Unified function to decide what to do: Q&A, text generation, training, or emotion response
def get_chat(input_text, task_type="qna", target_text=None, min_length=50, max_length=1024):
    # Check if the input is a greeting
    if is_greeting(input_text):
        return "Hello! How can I assist you today?"

    # Check for emotional content in the input
    emotion_response = detect_emotion(input_text)
    if emotion_response:
        return emotion_response

    if task_type == "qna":
        return get_answer(input_text)
    elif task_type == "generation":
        return generate_text(input_text, min_length, max_length)
    elif task_type == "train":
        if target_text is None:
            return "Target text is required for training."
        train_model([input_text], [target_text])
        return "Training complete."
    else:
        return "Invalid task type. Please specify 'qna', 'generation', or 'train'."

# Example for training the model
if __name__ == "__main__":
    # Example training data (input and target text)
    input_texts = ["What is the stock market?", "Explain the fundamentals of AI."]
    target_texts = [
        "The stock market is a platform where stocks and securities are bought and sold.",
        "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of performing tasks that typically require human intelligence."
    ]
    
    # Train the model (use task_type="train")
    print(get_chat(input_texts[0], task_type="train", target_text=target_texts[0]))
    
    # Example generation after training
    prompt = "What is the stock market?"
    print("Generated text: ", get_chat(prompt, task_type="generation", min_length=50, max_length=200))

    # Test greeting input
    greeting_input = "hello"
    print(get_chat(greeting_input, task_type="qna"))
    
    # Test emotional input
    emotional_input = "I'm feeling really happy today!"
    print(get_chat(emotional_input, task_type="qna"))
