# IRC-ChatBot

## Description
Chat-bot name: silly-bot

The chatbot is designed to operate on the IRC (Internet Relay Chat) platform with the purpose of engaging in greeting conversations with users in a specified channel.Using sockets, we connected the bot to the IRC server. And nicknamed our bot silly-bot’. We then ran the script which enabled the bot to join the channel and sent commands and requests which gave appropriate responses.

## Implementation
To allow our script to connect to the irc chat application we used sockets. To handle the timeout for our application
The bot uses spacy (nlp) to break the command into tokens and determine if the command entered is a ‘Greeting’, a ‘Reply’ or an ‘Enquiry’.
Below is a set of greetings, inquiries and exit commands that the bot takes care of.

<img width="772" alt="Screenshot 2024-03-29 at 4 52 00 PM" src="https://github.com/MihikaNigam/IRC-ChatBot/assets/43610611/f78fd3af-81da-4dba-ad70-fa8731d507bc">
