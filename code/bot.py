import time
from fsmstate import State
import langsearch
import random
import socket
import sys
from stack import Stack
import spacy
import cricketsearch

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

server = "irc.libera.chat"
port = 6667
channel = "#CSC482"
nickname = "silly-bot"

greetings = ["hi", "hello", "heyo", "hey there!", "hola"]
second_outreach = ["excuse me, hello?", "I said HI!", "hellllloooooo!"]
exit_phrases = ["whatever", "ok, forget you",
                "screw you!", "whatever, fine. Don’t answer"]
replies = ["I’m great!", "I'm fine", "all is good", 'nothing much']
inquiry_replies = ["how about yourself?", "how about you?", "and yourself?"]
inquiries = ["how are you doing?", "how are you?",
             "how is it going?", "what’s happening?"]


class MyBot:

    def __init__(self, irc_connection):
        self.ircc = irc_connection
        self.state = State(curr_state='waiting', next_state='initialOutreach')
        self.sender = None
        self.stack = Stack()

    def handle_inventionQuery(self, sender, command):
        arr = command.split(' ')
        item = arr[2]
        place, year = langsearch.get_res(item)
        if place == None and year == None:
            self.send_message(sender, "Sorry I couldnt fetch that :( )")
        elif year == None:
            self.send_message(
                sender, f'{item} was invented in {place}')
        else:
            self.send_message(
                sender, f'{item} was invented in {place} in the year {year}')

    def send_message(self, sender, mssg):
        self.ircc.send(f"PRIVMSG {channel} :{sender}: {mssg}\r\n")

    def reset_bot(self):
        self.state = State('waiting', 'initialOutreach')
        self.sender = None
        self.ircc.reset_timer(15)
        self.stack.clear()

    def quit_bot(self, mssg):
        self.ircc.send(f"QUIT {channel} : {mssg}\r\n")

    def identify_text_type(self, text):
        doc = nlp(text.lower())
        if any(token.text in ['hello', 'hi', 'hey', 'hola', 'heyo', 'yes'] for token in doc):
            return 'Greeting'
        if any(token.text in ['good', 'bad', 'ok', 'great', 'fine', 'nothing'] for token in doc):
            return 'Reply'
        if any(token.text in ['what', 'how', 'where', 'who', 'why'] for token in doc):
            return 'Inquiry'
        return 'Other'

    def handle_greeting(self, sender, command):
        print(f'state rn: {self.state.current}')
        # user initiates
        if self.identify_text_type(command) == 'Greeting' and self.state.current == 'waiting' and self.state.next_state == 'initialOutreach':
            print('user Greeting')
            self.send_message(sender, "hi back!")
            self.state = State('outreachReply', 'inquiry')
        elif self.identify_text_type(command) == 'Inquiry' and self.state.current == 'outreachReply' and self.state.next_state == 'inquiry':
            print('User Inquired')
            self.send_message(sender, random.choice(replies))
            self.send_message(sender, random.choice(inquiry_replies))
            self.state = State('inquiry', 'inquiryReply')
        elif self.identify_text_type(command) == 'Reply' and self.state.current == 'inquiry' and self.state.next_state == 'inquiryReply':
            print('User Replied')
            self.send_message(sender, 'I hope it gets better!')
            self.reset_bot()
        # user replies on outreach
        elif self.identify_text_type(command) == 'Greeting' and self.state.current in ['initialOutreach', 'secondaryOutreach'] and self.state.next_state in ['secondaryOutreach', 'inquiry']:
            print('User Replied on Outreach')
            self.send_message(sender, random.choice(inquiries))
            self.state = State('inquiry', 'giveup')
        elif self.identify_text_type(command) == 'Reply' and self.state.current == 'inquiry' and self.state.next_state == 'giveup':
            print('User Replied for Outreach Inquiry')
            self.send_message(sender, 'I hope it gets better!')
            self.reset_bot()
        elif self.identify_text_type(command) == 'Other':
            self.send_message(
                sender, 'Sorry I do not understand that... Resetting state.')
            self.reset_bot()

    def get_users(self):
        self.ircc.send(f"NAMES {channel}\r\n")
        response = self.ircc.receive()
        users = response.split(":")[2].strip()
        users = users.split(' ')
        # users = users.remove(nickname)
        return users

    def handle_command(self, message):
        sender = message.split('!')[0][1:]
        content = message.split(f'PRIVMSG {channel} :')[1].strip()
        if content.startswith(nickname):
            command = content.split(': ')[1].lower()
            if command == 'die':
                self.send_message(sender, "Goodbye Amigo!")
                self.quit_bot('* gatito-bot has quit')
                time.sleep(2)
                sys.exit(0)
            elif command == "who":
                self.send_message(sender, "My name is "+nickname +
                                  ". I was created by M. Nigam & Kedar, CSC 482-02")
                self.send_message(
                    sender, 'I can tell you where a certain entity(human invention) was invented. Ask me a question like this: \"Where was <ITEM> invented?\"')
            elif command == "users":
                users = self.get_users()
                self.send_message(sender, ', '.join(users))
            elif command == "forget":
                self.send_message(sender, 'Forgetting you and this world..')
                self.reset_bot()
            elif 'invented' in command:
                self.handle_inventionQuery(sender, command)
            elif 'won' in command:
                cricketsearch.answer_question(command, self.scrape_winners(
                    "https://en.wikipedia.org/wiki/Cricket_World_Cup"), "https://en.wikipedia.org/wiki/ICC_T20_World_Cup")
            elif self.identify_text_type(command) != 'Other' and ((self.sender == None and self.state.current == 'waiting') or (self.state.current != 'waiting' and sender == self.sender)):
                print(
                    f"self.sender : {self.sender} and self.state.current : {self.state.current} and sender : {sender}")
                self.sender = sender if self.sender == None and self.state.current == 'waiting' else self.sender
                self.handle_greeting(sender, command)
            elif not ((self.sender == None and self.state.current == 'waiting') or (self.state.current != 'waiting' and sender == self.sender)):
                print("Interaction w previous user not complete")
            else:
                self.send_message(sender, "Sorry I am not trained for that :/")
        else:
            print("incorrect command")

    def run(self):
        randomuser = None
        while True:
            try:
                response = self.ircc.receive()
            except socket.timeout:
                print("Socket operation timed out. Stopping further attempts")
                print(f'current state : {self.state.current}')
                if self.state.current == 'waiting' and self.state.next_state == 'initialOutreach':
                    print("User didnt respond on 1'st outreach")
                    randomuser = random.choice(self.get_users())
                    self.sender = randomuser
                    self.send_message(randomuser,
                                      random.choice(greetings))
                    self.state = State('initialOutreach', 'secondaryOutreach')
                    self.ircc.reset_timer(30)
                elif self.state.current == 'initialOutreach' and self.state.next_state == 'secondaryOutreach':
                    print("User didnt respond on 2'nd outreach")
                    self.send_message(
                        randomuser, random.choice(second_outreach))
                    self.state = State('secondaryOutreach', 'inquiry')
                    self.ircc.reset_timer(15)
                elif self.state.current == 'secondaryOutreach' and self.state.next_state == 'inquiry':
                    print("Forget user")
                    self.send_message(
                        randomuser, random.choice(exit_phrases))
                    self.reset_bot()
                elif self.state.current == 'inquiry' and self.state.next_state == ['inquiryReply', 'giveup']:
                    print('user doesnt respond to inquiry')
                    self.send_message(
                        self.sender, 'You there.... ?')
                    self.ircc.reset_timer(30)
                elif self.state.next_state in ['giveup'] or self.state.current == 'outreachReply':
                    print('user doesnt respond to inquiry supplement ques')
                    self.send_message(
                        self.sender, random.choice(exit_phrases))
                    self.reset_bot()
            if response:
                if "PING" in response:
                    self.ircc.send(
                        f"PONG {response.split()[1]}\r\n")
                elif "PRIVMSG" in response and f'{nickname}' in response and self.stack.peek() != response:
                    self.stack.push(response)
                    self.handle_command(response)
                    self.ircc.reset_timer(30)

            time.sleep(1)
