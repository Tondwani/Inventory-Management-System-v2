import json
import re

import pyttsx3
import speech_recognition as sr
from fuzzywuzzy import fuzz
from product_manager_representation import ProductManagerRepresentation


class InventoryChatbot:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.product_manager = ProductManagerRepresentation()
        self.load_data()

    def load_data(self):
        # Load data from JSON files
        with open('product_data.json', 'r') as f:
            self.product_data = json.load(f)
        # Load other data (employee, category, etc.) similarly

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return ""

    def speak(self, text):
        print(f"Chatbot: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def process_command(self, command):
        if "product" in command:
            return self.handle_product_query(command)
        # Add handlers for other types of queries (employee, category, etc.)
        else:
            return "I'm sorry, I don't understand that command. Can you please try again?"

    def handle_product_query(self, command):
        if "list methods" in command or "what can you do" in command:
            methods = self.product_manager.get_method_names()
            return f"I can perform the following operations with products: {', '.join(methods)}"
        
        if "add product" in command:
            return self.product_manager.get_method_description("add_product")
        
        if "edit product" in command:
            return self.product_manager.get_method_description("edit_product")
        
        if "delete product" in command:
            return self.product_manager.get_method_description("delete_product")
        
        if "search product" in command:
            return self.product_manager.get_method_description("search_product")
        
        if "export products" in command:
            return self.product_manager.get_method_description("export_to_csv")
        
        if "product information" in command:
            columns = self.product_manager.get_database_columns()
            return f"Product information includes: {', '.join(columns)}"

        # Add more specific handlers for other product-related queries

        return "I'm sorry, I don't understand that product-related command. Can you please try again?"

    def run(self):
        self.speak("Hello! I'm your inventory management assistant. How can I help you?")
        while True:
            command = self.listen()
            if command:
                if "exit" in command or "quit" in command:
                    self.speak("Goodbye!")
                    break
                response = self.process_command(command)
                self.speak(response)

def launch_chatbot():
    chatbot = InventoryChatbot()
    chatbot.run()

if __name__ == "__main__":
    launch_chatbot()