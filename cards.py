#! python3
"""
Cards v0.4 by Daniel James
A spaced-repetition flashcard system in which users create flashcards from a
simple command-line interface that will be served back to them at an algorithmically
determined rate, helping to boost recall of information that the user is studying.
Flashcards will be sorted depending on keywords that determine how they are stored
and served. In the future, can choose which system's algorithm. Will start Pimsleur for simplicity.
"""
# TODO: Write unit tests to make sure each function is working properly
import sys, shelve, logging, time, random
from datetime import timedelta
logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
CARDFILE = 'cardfile'
REMOVE_THESE_KEYS = ['lastTopic']
args = sys.argv
# The LEVELS list is a lin seconds, of intervals after which a card must be reviewed.
# 5 seconds, 25 seconds, 2 minutes, 10 minutes, 1 hour, 5 hours, 1 day, 5 days, 25 days, 4 months, and 2 years.
"""
TODO: Shuffle function. shuffle card times randomly while staying within their time level.
TODO: have cardfile be passed to all functions as default cardfile CARDFILE.
"""
LEVELS = [5, 25, 120, 600, 3600, 18000, 86400, 432000, 2160000, 10368000, 63072000]
FORBIDDEN_MAGICKS = ["lastTopic"]
"""
Cards are stored in dict format for easy use in shelve. Each card entry will be a list of
four things: question, answer, timestamp of the last time it was accessed, and recall level.
The level represents which amount of time to wait until showing it again and is to be checked
against the timestamp so that relevant cards are shown when appropriate.
"""

class Card:
    def __init__(self, cardList, topic):
        cardFile = shelve.open(CARDFILE)
        self.question = cardList[0]
        self.answer = cardList[1]
        self.time = cardList[2]
        self.level = cardList[3]
        self.card = cardList
        try:
            topicList = cardFile[topic]
        except:
            topicList = []
        try:
            self.index = topicList.index(cardList)
        except:
            self.index = len(topicList)
        self.topic = topic
        cardFile.close()
    def save(self): # Updates cardfile entry by inserting the new information at the correct index, then deleting the old one (located one index further)
        cardFile = shelve.open(CARDFILE)
        saveCard = [self.question,self.answer,self.time,self.level]
        try:
            topicList = cardFile[self.topic]
        except:
            topicList = []
        topicList.insert(self.index, saveCard)
        if self.index != len(topicList)-1: # Since the new data has already been added to the list, this will be the case only if the card is new
            elementToDel = self.index + 1  # index of Element To Delete
            del topicList[elementToDel]
        cardFile[self.topic] = topicList
        cardFile['lastTopic'] = self.topic
        cardFile.close()
        return
    def edit(self):
        userInput = prompt_for_input("Would you like to edit the [q]uestion, [a]nswer, or [t]opic?")
        if userInput == 'q' or userInput == 'a':
            finished = 0
            cardIndex = 0
            if userInput == 'q':
                cardIndex = 0
                noun = "question"
            elif userInput == 'a':
                cardIndex = 1
                noun = "answer"
            finished = False
            while not finished:
                newEntry = prompt_for_input("Enter your new %s." %noun)
                print("The new %s is as follows:\n\n%s\n" % (noun, newEntry))
                if confirmation_input("Is this good?", defaultAns=1):
                    if cardIndex == 0:
                        self.question = newEntry
                    elif cardIndex == 1:
                        self.answer = newEntry
                    finished = 1
            self.save()
            print("Saved.")
            self.display()

        elif userInput == 't':
            print("You can't do that yet.")
            #TODO: Allow changing of topics
            pass
        else:
            pass

    def delete(self): # Loads cardFile and deletes its own entry in the list of topics
        cardFile = shelve.open(CARDFILE)
        ListContainingTheCardToDelete = cardFile[self.topic]
        del ListContainingTheCardToDelete[self.index]
        cardFile[self.topic] = ListContainingTheCardToDelete
        if len(cardFile[self.topic]) == 0:
            print("That was the last card in its topic. Removing topic from deck.")
            cardFile.pop(self.topic, None)
        cardFile.close()
        logging.info("Card removed from cardfile, and deleting itself.")
        del self
    def display(self):
        print("----------")
        print("Topic: %s" % self.topic)
        print("----------")
        print("Question: \n%s" % self.question)
        print("----------")
        print("Answer: \n%s" % self.answer)
        print("----------")


def recursively_print_time(seconds, i=0, gradations=(86400, 3600, 60, 1), nouns=(' days ', ' hours ', ' minutes ', ' seconds'), returnString=''): # wherein I take a stab at recursion
    seconds = int(seconds)
    numThing = 0
    while seconds % gradations[i] != seconds and seconds >= gradations[i]:
        numThing = numThing + 1
        seconds = seconds - gradations[i]
    if numThing != 0:
        returnString = returnString + str(numThing) + nouns[i]
        if numThing == 1 and i!= 3: # remove the plural from the noun if 1
            returnString.replace('s', '')
    if i == 3:
        if numThing == 1:
            returnString = returnString[0:-1]
        print(returnString)
        return
    recursively_print_time(seconds,i=i+1,returnString=returnString)
def press_any_key(text='Press any key to continue.'):
    print(text)
    input()
def prompt_for_input(text): return input(text + " > ") # General test prompt that just adds an arrow
def confirmation_input(text, defaultAns=0, finished=False): # Provides a y/n prompt for passed text, with optional default answer
    while finished == False:
        if defaultAns == 0: # No default
            print(text + ' (Y/N) > ', end='')
        elif defaultAns == 1: # if 1, default answer is yes
            print(text + ' ([Y]/N) > ', end='')
        elif defaultAns == 2: # if 2, default answer is 2
            print(text + ' (Y/[N]) > ', end='')
        confirmation = input().lower()
        if confirmation == '': # apply default answer
            if defaultAns == 1:
                return True
            elif defaultAns == 2:
                return False
        elif confirmation == 'y' or confirmation == 'yes':
            return True
        elif confirmation == 'n' or confirmation == 'no':
            return False
def list_input(text, listIndices): # Prompts for and validates input according to provided list of acceptable indices
    print(text, end='')
    userInput = input()
    found = listIndices.count(userInput)
    if found:
        return userInput
    else:
        return False
def topic_confirmation_loop(question_text): # asks for user input until user agrees to it.
    finished = 0
    while finished == 0:
        userInput = prompt_for_input(question_text)
        if userInput == '':
            print("You must enter a topic.")
        else:
            try: # Try and type it as an integer. If so, fail. Can't have them inputting topics that might interfere with our list indexxes
                inputInt = int(userInput)
                print("Topics may not be integers.")
            except: # Topic is not an integer, proceed.
                print('You entered: %s.' % userInput)
                if confirmation_input('Is this good?', defaultAns=1):
                    return userInput

def print_next_review_time(cardFile): # pass it an open card file
    timeList = []
    topics = get_list_of_topics(cardFile)
    for topic in topics:
        theseCards = cardFile[topic]
        for thisCard in theseCards:
            thisCardTime = thisCard[2]
            interval = LEVELS[thisCard[3]]
            timeDifference = time.time() - thisCardTime
            timeUntilNextReview = interval - timeDifference
            timeList.append(timeUntilNextReview)
    least = min(timeList)
    if least <= 0:
        print("Next card review is already due.")
        return least
    else:
        print("Next card review due in ", end='')
        recursively_print_time(least)
        return least
def get_list_of_topics(cardFile): # returns a list of topics - cardFile, scrubbed of data keys that are not topics
    logging.debug("Initiated get_list_of_topics.")
    list_of_topics = list(cardFile.keys())
    logging.debug("Keys in the cardfile: %s" %list_of_topics)
    for forbiddenFruit in REMOVE_THESE_KEYS:
        list_of_topics.remove(forbiddenFruit)
        logging.debug("Cleaned %s from list. New list: %s" % (forbiddenFruit, list_of_topics))
    logging.debug("Returning list: %s" %list_of_topics)
    return list_of_topics
def list_topic_choices(list_of_topics): # simply prints the topics in list_of_topics along with their index, returns a list of the indices iterated
    listLength = len(list_of_topics)
    listOfIndices = []
    for i in range(0, listLength):
        print('(%s) %s' % (str(i), list_of_topics[i]))
        listOfIndices.append(str(i))
    return listOfIndices
def check_if_topic_exists(list_of_topics, topic): # checks the list of topics for existence of a given topic
    topicExists = list_of_topics.count(topic)
    if topicExists > 0:
        return True
    else:
        return False
def add_topic_to_cardfile(topic): # add a new topic key to the cardfile.
    cardFile = shelve.open(CARDFILE)
    cardFile[topic] = []
    cardFile.close()
def input_or_choose_topic(list_of_topics): # apply topic input loop (selection) until user signals they're happy with it
    complete = 0
    topic = ""
    cardFile = shelve.open(CARDFILE)
    while complete == 0: # Loop the loop until the good times roll
        if list_of_topics == []: # if there is not LoT, we know we need to input and store one
            topic = topic_confirmation_loop('Enter a new topic')
            add_topic_to_cardfile(topic)
            complete = 1
        else: # There is a LoT, so we must list the topics and choose one
            topicIndices = list_topic_choices(list_of_topics)
            print('Choose a topic from the list, add a new one, or ENTER for last(%s): > ' % (cardFile['lastTopic']), end='')
            userInput = input()
            if userInput == "": # user would like to use last topic used
                topic = cardFile['lastTopic']
                complete = 1
            else: # user input is not blank
                indexFound = topicIndices.count(userInput)
                if indexFound > 0: # user entered a valid index
                    topicIndex = int(userInput)
                    topic = list_of_topics[topicIndex]
                    complete = 1
                else: # Input was not found on index list. Treat it as a new topic
                    topic = userInput
                    try: # Try and type it as an integer. If so, fail.
                        topicInt = int(topic)
                        print("Topics may not be integers.")
                    except: # Topic is not an integer, proceed.
                        if check_if_topic_exists(list_of_topics, topic): # topic exists already, just use it.
                            complete = 1
                            return topic
                        else: # topic does not yet exist in the list, add it.
                            print("Topic '%s' will be added." % userInput)
                            if confirmation_input('Is this good?', defaultAns=1): # User is happy with their topic choice
                                add_topic_to_cardfile(topic)
                                complete = 1
    cardFile.close()
    return topic
def update_topics(cardFile): #
    list_of_topics = get_list_of_topics(cardFile)
    for topic in list_of_topics:
        if cardFile[topic] == []:
            del cardFile[topic]
    logging.info("Topics updated.")
def insert_card_in_cardfile(topic, card, cardFile):
    logging.debug("Adding card to card file.")
    try: # Tesrt to see if topic exists in cardfile
        testingVar = cardFile[topic][0]
        logging.debug("Topic %s appears to exist as a key in card file already." %topic)
    except:
        cardFile[topic] = []
        logging.debug("Adding topic %s to cardFile as blank list." %topic)
    currentTopicEntries = cardFile[topic]
    logging.debug("Current topic entries in cardfile for %s: %s" %(topic, currentTopicEntries))
    currentTopicEntries.append(card)
    logging.debug("Appended card %s to entry. New entry: %s" %(card, currentTopicEntries))
    cardFile[topic] = currentTopicEntries
    cardFile['lastTopic'] = topic
    logging.debug("Added new entry to card file. %s" %cardFile[topic][-1])
    logging.debug("Before cardfile is closed, keys are: %s" %list(cardFile.keys()))
def add_card_loop(cardFile): # Adds a new card to the file. Accepts open card file as argument.
    finished = False
    def print_input_to_verify(response_list):
        print("Topic: " + response_list[2])
        print("Question: " + response_list[0])
        print("Answer: " + response_list[1])
    i = 0
    list_of_user_responses = []
    print("Type 'quit' in any field to quit.")
    while not finished:

        prompts = ["What is the question?","What is the answer? Be specific."]
        if i < 2:
            list_of_user_responses.append(prompt_for_input(prompts[i]))
        elif i == 2:
            list_of_topics = get_list_of_topics(cardFile)
            list_of_user_responses.append(input_or_choose_topic(list_of_topics))
        else:
            print_input_to_verify(list_of_user_responses)
            if confirmation_input('Does that look good?', defaultAns=1): # confirm that the flash cardFile are as intended
                topic, question, answer = list_of_user_responses[2], list_of_user_responses[0], list_of_user_responses[1]
                return topic, question, answer
        if list_of_user_responses[i].lower() == 'quit':
            print("Quitting.")
            return False, False, False
        i += 1

def review_cards(cards, cardsToServe): # pass it an open data file and a list of keys
    numLeft = len(cardsToServe) # numLeft will keep track of how many cards are left to go.
    if numLeft != 1: # can't shuffle one card.
        if confirmation_input('Would you like to shuffle the order of the cards?', defaultAns=1): random.shuffle(cardsToServe)
    for cardTuple in cardsToServe:
        topic = cardTuple[0]
        i = cardTuple[1]
        thisCard = cards[topic][i]
        print("\n" + thisCard[0] + "\n")
        press_any_key(text='Think well of the answer, then press any key to continue.')
        print('Answer: %s\n' % (thisCard[1]))
        if confirmation_input('Did you get it completely right?'):
            thisCard[3] = thisCard[3] + 1 # Graduate card to next level.
            print('Card graduated to level %s. It\'s up for review in ' % (str(thisCard[3])), end='')
            recursively_print_time(LEVELS[thisCard[3]])
        else:
            thisCard[3] = 0 # Put the card back into the review level.
        thisCard[2] = time.time() # Update card's time of access
        cardList = cards[topic]
        cardList[i] = thisCard
        cards[topic] = cardList # Update entry in card file.
        numLeft -= 1
        if numLeft > 0:
            if confirmation_input('You have %s cards left. Continue?' % str(numLeft), defaultAns = 1):
                pass
            else:
                print("Card review paused. Don't wait too long.")
                cards.close()
                return
        else:
            least = print_next_review_time(cards)
            time.sleep(0.1)
            if least <= 0: # Run again!
                cardsToServe = poll_for_review(cards)
                if confirmation_input("Would you like to review more cards?", defaultAns=1):
                    review_cards(cards, cardsToServe)

    cards.close()
    return
def validate_list_input(promptText, list_of_indices): # asks user to choose an input from a list, and returns it after validation
    logging.info("Beginning validate_list_input. List of indices: %s" % (list_of_indices))
    finished = False
    while finished == False:
        userInput = prompt_for_input(promptText)
        found = list_of_indices.count(userInput)
        logging.info("user input: %s, found: %s" % (userInput, found))
        if found:
            return userInput
        elif userInput == 'x':
            exit()
        elif userInput == '':
            return userInput
        else:
            print("Invalid input. Try again.")
def choose_item_from_list(passedList, resultsPerPrompt=10): # prints a given list and asks user to choose one. returns index of chosen item.
    list_of_indices = [0] # We give it an initial value of 0 to bump the list of indices up by one when the for loop runs. This ensures the modulo function will run without issue.
    listLength = len(passedList)
    logging.info("Choosing item from list. List length: %s" %listLength)
    firstInList = 1
    print('')
    choice = ''
    for i in range(firstInList,listLength+1):
        logging.debug("Current index is %s." % i)
        print("(%s) %s\n" % (str(i), passedList[i-1][0])) # Prints question of currently iterated card
        list_of_indices.append(str(i))
        if i % resultsPerPrompt == 0 or i == listLength+1: # Check if i is divisible by number of results per prompt, if so, prompt to choose or continue
            indicesLength = len(list_of_indices)
            print("Showing results %s through %s of %s." % (firstInList, indicesLength-1,listLength))
            choice = validate_list_input("Choose a card number from the list, ENTER to continue, or 'x' to exit.", list_of_indices)
            firstInList = i+1
            if choice != '':
                return int(choice)-1 # -1 to adjust for having the index be ahead

    while choice == '':
        choice = validate_list_input("Choose a card number from the list, or 'x' to exit.", list_of_indices)

    return int(choice)-1 # Subtract 1 so it jives with actual list indices
def view_cards(topic): # View or edit cards
    cardFile = shelve.open(CARDFILE)
    cardsToView = cardFile[topic]
    cardFile.close()
    logging.debug("Viewing cards: %s" %cardsToView)
    viewed_cards = []
    cardsToViewLength = len(cardsToView)
    logging.info("Finished list of cards to view. Entries: %s " %cardsToViewLength)
    choiceIndex = choose_item_from_list(cardsToView) # user chooses a card to view
    cardChoice = cardsToView[choiceIndex]
    chosenCard = Card(cardChoice, topic)
    chosenCard.display()
    choice = prompt_for_input("[E]dit  [D]elete  [Q]uit ")
    if choice.lower() == 'e':
        chosenCard.edit()
        del chosenCard
    elif choice.lower() == 'd':
        print("This will completely delete this card from your file.")
        confirmation = input("If you're certain, type 'yes': >")
        if confirmation.lower() == 'yes':
            chosenCard.delete()
def poll_for_review(cards): # Checks card file to see if any cards need review and returns them as a list. Pass it an open cardfile
    cardsToServe = [] #This will be a list of tuples representing each card's topic and index in the list of its card file entry.
    logging.info("Polling for review.")

    list_of_topics = get_list_of_topics(cards)
    if len(list_of_topics) > 0: # Make sure there are cards present in the data file at all.
        logging.debug("topics found in cardfile.")
        for topic in list_of_topics:
            logging.debug("processing topic %s" %topic)
            cardsInTopic = cards[topic]
            logging.debug("for %s, found: %s" %(topic, cardsInTopic))
            for thisCard in cardsInTopic:# search keys for times and check against their level
                cardIndex = cardsInTopic.index(thisCard)
                cardTime = thisCard[2]
                cardLevel = thisCard[3]
                timeDifference = time.time() - cardTime
                if timeDifference > LEVELS[cardLevel]:
                    newTuple = (topic, cardIndex)
                    cardsToServe.append(newTuple)
                    logging.debug("Have added tuple %s,%s to cardsToServe" %newTuple)
        if cardsToServe: # cards were found that need review
            numberOfCards = len(cardsToServe)
            print('You have %s cards to review.' % numberOfCards)
        else:
            print('You have no cards that need review.')
            print_next_review_time(cards)
        return cardsToServe
    else:
        cardsToServe.append("nocards")
        return cardsToServe
def quit_by_magick():
    raise ValueError("You may not speak the hallowed words of the ancient magicks. This topic is disallowed")
def print_usage(): # prints list of available usage commands
    print("Cards v0.4 by Dan\n")
    print("cards          - Check for and begin a card review.")
    print("cards add      - Add a new card for review.")
    print("cards view     - View, edit, or delete cards in catalogue.")
    print("cards topics   - View all topics in the catalogue.")
    print("cards clear    - Clear all cards from catalogue and start fresh.")
    print("cards poll     - Checks if you have cards to review.")
    print("cards help     - View this list.")
    print("\nReview often for maximum learning power.")
def card_input_verified_as_valid(topic, question, answer):
    # TODO
    return True


if len(args) == 1: # No arguments provided
    print("Cards v0.4 by Dan\nUse 'cards help' to view usage.\n")
    logging.info("Checking for cards that need review.")
    cards = shelve.open(CARDFILE) # Open the data file
    cardFileKeys = list(cards.keys())
    if cardFileKeys == []:
        logging.debug("No keys found in cardfile at all. Entering lasttopic.")
        cards['lastTopic'] = ''
    logging.debug("Cardfile Open. Keys: %s" %list(cards.keys()))
    cardsToServe = poll_for_review(cards)
    if cardsToServe:
        if cardsToServe[0] == "nocards":
            print('You have no cards. Add one to get started:\n \"cards add\"')
            cards.close()
        elif confirmation_input('Review them now?', defaultAns=1): # does user want to do it now?
            review_cards(cards, cardsToServe)
            print('Card review completed.')
        else:
            print('Don\'t wait too long.')
            cards.close()
    else: # no cards were found that need review
        cards.close()

elif len(args) > 1: # Parse those arguments!
    if args[1] == 'add':
        # syntax is 'cards add topic question answer' or optionally 'cards add question answer'
        # The latter will use the last-used 'topic' if one exists, or else 'No topic'

        lastTopic = ""
        topic, question, answer = "", "", ""

        cards = shelve.open(CARDFILE)
        try:
            lastTopic = cards['lastTopic']
            logging.debug("Detected that a last topic exists.")
        except:
            lastTopic = 'No topic'
            cards['lastTopic'] = lastTopic
        if len(args) == 2:  # If there are no other arguments than 'add', begin the assisted card loop
            topic, question, answer = add_card_loop(cards)

        elif len(args) == 3:
            print("Not enough arguments.")  #TODO: usage info here
        elif len(args) == 4:
            topic = lastTopic
            question = args[2]
            answer = args[3]
        elif len(args) == 5:
            topic = args[2]
            question = args[3]
            answer = args[4]
            logging.debug("Topic: %s| Question: %s| Answer: |%s" % (topic, question, answer))
        else:
            print("Too many arguments!") #TODO: usage here too

        if answer:  # indicating add_card_loop hasn't been quit and there are minimum arguments to proceed
            curTime = time.time() # get current time

            if card_input_verified_as_valid(topic, question, answer):
                cardData = [question, answer, curTime, 0] # This makes up the card's data
                thisCard = Card(cardData, topic)

                if topic in FORBIDDEN_MAGICKS:  # Just in case there are tricksters afoot. Put this in validation function
                    quit_by_magick()

                thisCard.save()
                cards.close()
                print("Card added successfully.")

    elif args[1] == 'list':
        pass #  # Nothing yet
    elif args[1] == 'clear':
        print("This will clear ALL cards from your file. Are you absolutely sure?")
        confirmation = input("If you're certain, type 'yes': >")
        if confirmation.lower() == 'yes':
            cards = shelve.open(CARDFILE)
            keylist = list(cards.keys())
            for key in keylist:
                del cards[key]
            cards.close()
        print("Card file is cleared.") # Clear all cards from the catalogue.
    elif args[1] == 'topics':
        cardFile = shelve.open(CARDFILE)
        list_of_topics = get_list_of_topics(cardFile)
        cardFile.close()
        print("\nThe following topics were found:\n")
        for topic in list_of_topics:
            print(topic)
    elif args[1] == 'view': # View cards, sorted by topic.
        finished = 0
        while finished == 0:
            cardFile = shelve.open(CARDFILE)
            topics = get_list_of_topics(cardFile)
            logging.debug("List of topics: %s" %topics)
            topicIndices = list_topic_choices(topics)
            logging.debug("Accompanying indices: %s" %topicIndices)
            chosenIndex = list_input("\nEnter the number of the topic to view, or any other key to quit. > ", topicIndices)
            if chosenIndex == False:
                finished = 1
            else:
                topic = topics[int(chosenIndex)]
                logging.info("Topic chosen: %s" %topic)
                view_cards(topic)
            cardFile.close()
            if finished == 0:
                if not confirmation_input('Would you like to view another card?', defaultAns=1):
                    print("Card view complete.")
                    finished = 1


    elif args[1] == 'poll': # Poll for review without asking if the user would like to
        cards = shelve.open(CARDFILE)
        poll_for_review(cards)
        cards.close()
    elif args[1] == 'help': # Prints usage of cards program
        print_usage()
    else:
        print("Try 'cards help'")
