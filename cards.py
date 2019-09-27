#! python3
"""
Cards v0.2 by Daniel James
A spaced-repetition flashcard system in which users create flashcards from a
simple command-line interface that will be served back to them at an algorithmically
determined rate, helping to boost recall of information that the user is studying.
Flashcards will be sorted depending on keywords that determine how they are stored
and served. In the future, can choose which system's algorithm. Will start with Leitner and Pimsleur for simplicity.
"""
import sys, shelve, logging, time
from datetime import timedelta
logging.basicConfig(level=logging.WARNING, format=' %(asctime)s - %(levelname)s - %(message)s')
CARDFILE = 'cardfile.cdf'
DATAFILE = 'datafile.cdf'
args = sys.argv
# The LEVELS list is a list, in seconds, of intervals after which a card must be reviewed.
# 5 seconds, 25 seconds, 2 minutes, 10 minutes, 1 hour, 5 hours, 1 day, 5 days, 25 days, 4 months, and 2 years.
LEVELS = [5, 25, 120, 600, 3600, 18000, 86400, 432000, 2160000, 10368000, 63072000]
"""
Cards are stored in dict format for easy use in shelve. Each card entry will be a list of
four things: question, answer, timestamp of the last time it was accessed, and recall level.
The level represents which amount of time to wait until showing it again and is to be checked
against the timestamp so that relevant cards are shown when appropriate.
"""
def confirmation_input(text):
    print(text + ' (Y/N) >', end='')
    confirmation = input().lower()
    if confirmation == 'y' or confirmation == 'yes':
        return True
    else:
        return False
def topic_confirmation_loop(question_text): # asks for user input until user agrees to it.
    completed = 0
    userInput = ""
    while completed == 0:
        print(question_text + " > ", end='')
        userInput = input()
        if userInput == '':
            print("You must enter a topic.")
        else:
            try: # Try and type it as an integer. If so, fail.
                inputInt = int(userInput)
                print("Topics may not be integers.")
            except: # Topic is not an integer, proceed.
                print('You entered: %s.' % userInput)
                if confirmation_input('Is this good?'):
                    completed = 1
    return userInput
def pressAnyKey(text='Press any key to continue.'):
    print(text)
    input()
def print_next_review_time(cardFile): # pass it an open card file
    timeList = []
    for key in cardFile.keys():
        thisCard = cardFile[key]
        thisCardTime = thisCard[2]
        interval = LEVELS[thisCard[3]]
        timeDifference = time.time() - thisCardTime
        timeUntilNextReview = interval - timeDifference
        timeList.append(timeUntilNextReview)
    least = min(timeList)
    nextTime = "{:0>8}".format(str(timedelta(seconds=least)))
    print("Next review coming up in: %s" %nextTime)
    return least
def get_list_of_topics(dataFile): # returns list of topics in the data file
    keyList = []
    keyList = list(dataFile.keys())
    topicsKeyCount = keyList.count("topics") # Just checking if the data file is empty of topics or not
    if topicsKeyCount > 0:
        list_of_topics = dataFile["topics"]
        return list_of_topics
    else:
        return []
def add_topic_to_datafile(dataFile, topic): # adds topic to dataFile["topics"]
    list_of_topics = get_list_of_topics(dataFile)
    list_of_topics.append(topic)
    dataFile["topics"] = list_of_topics
    return True
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
def input_or_choose_topic(list_of_topics, dataFile): # apply topic input loop (selection) until user signals they're happy with it
    complete = 0
    topic = ""
    while complete == 0: # Loop the loop until the good times roll
        if list_of_topics == []: # if there is not LoT, we know we need to input and store one
            topic = topic_confirmation_loop('Enter a new topic')
            add_topic_to_datafile(dataFile, topic)
            complete = 1
        else: # There is a LoT, so we must list the topics and choose one
            topicIndices = list_topic_choices(list_of_topics)
            print('Choose a topic from the list, add a new one, or ENTER for last(%s): > ' % (dataFile['lastTopic']), end='')
            userInput = input()
            if userInput == "":
                topic = dataFile['lastTopic']
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
                            if confirmation_input('Is this good?'): # User is happy with their topic choice
                                add_topic_to_datafile(dataFile, topic)
                                complete = 1
    return topic
def addCard(cards): # Adds a new card to the file. Accepts open shelve file as argument.
    finished = False
    dataFile = shelve.open(DATAFILE)
    while not finished:
        print('What is the question? >', end='') # First inquire for question and answer
        question = input()
        print('What is the answer? Be specific. >', end='')
        answer = input()
        print('What is the topic of the card?')
        list_of_topics = get_list_of_topics(dataFile)
        topic = input_or_choose_topic(list_of_topics, dataFile)
        print('The topic is this: \'%s\'' % topic)
        print('Your question is this: \'%s\'' % question)
        print('The answer is this: \'%s\'' % answer)
        if confirmation_input('Does that look good?'): # confirm that the flash cards are as intended
            cardLength = len(cards.keys()) # get number of card entries. this will be the index of the new card
            curTime = time.time() # get current time
            thisCard = [question, answer, curTime, 0, topic] # This makes up the card's data
            cardFile = shelve.open(CARDFILE) # add card to the data file.
            cardFile[str(cardLength)] = thisCard # card is stored by numerical index - the number it is added as, in order.
            cardFile.close()
            dataFile['lastTopic'] = topic
            print('Card saved.')
            finished = True
    dataFile.close()
def reviewCards(cards, cardsToServe): # pass it an open data file and a list of keys
    numLeft = len(cardsToServe) # numLeft will keep track of how many cards are left to go.
    for key in cardsToServe:
        thisCard = cards[key]
        print("\n" + thisCard[0] + "\n")
        pressAnyKey(text='Think well of the answer, then press any key to continue.')
        print('Answer: %s\n' % (thisCard[1]))
        if confirmation_input('Did you get it completely right?'):
            thisCard[3] = thisCard[3] + 1 # Graduate card to next level.
            logging.info('Card graduated to level %s. It\'s up for review in %s seconds.' % (str(thisCard[3]), str(LEVELS[thisCard[3]])))
        else:
            thisCard[3] = 0 # Put the card back into the review level.
        thisCard[2] = time.time() # Update card's time of access
        cards[key] = thisCard # Update entry in card file.
        numLeft -= 1
        if numLeft > 0:
            if confirmation_input('You have %s cards left. Continue?' % str(numLeft)):
                pass
            else:
                print("Card review paused. Don't wait too long.")
                cards.close()
                return
        else:
            print('Card review completed.')
            least = print_next_review_time(cards)
    cards.close()
    return

if len(args) == 1: # No arguments provided
    logging.info("Checking for cards that need review.")
    cardsToServe = [] # This will be a list of keys representing the cardsto serve up as populated below
    cards = shelve.open(CARDFILE) # Open the data file
    logging.info("Data file opened.")
    if len(cards) > 0: # Make sure there are cards present in the data file at all.
        cardKeys = cards.keys()
        cardLength = len(cardKeys)
        logging.info('Number of cards stored: %s' % str(cardLength))
        for key in cardKeys: # search keys for times and check against their level
            thisCard = cards[key]
            cardTime = thisCard[2]
            cardLevel = thisCard[3]
            timeDifference = time.time() - cardTime
            if timeDifference > LEVELS[cardLevel]:
                cardsToServe.append(key)
        if cardsToServe: # cards were found that need review
            numberOfCards = len(cardsToServe)
            if confirmation_input('You have %s cards to review. Do it now?' % (str(numberOfCards))): # does user want to do it now?
                # Begin the card review loop
                reviewCards(cards, cardsToServe)
            else:
                print('Don\'t wait too long.')
                cards.close()
        else: # no cards were found that need review
            print("No cards currently require review.")
            least = print_next_review_time(cards)
            cards.close()
    else: # no cards are present in data file
        print('You have no cards. Add one to get started:\n \"cards add\"')
        cards.close()
elif len(args) > 1:
    if args[1] == 'add':
        cards = shelve.open(CARDFILE)
        addCard(cards) # Add a card to the catalogue
    elif args[1] == 'list':
        pass #  # Nothing yet
    elif args[1] == 'clear':
        print("This will clear ALL cards from your file. Are you absolutely sure?")
        print("If you're certain, type 'yes': >")
        confirmation = input()
        if confirmation.lower() == 'yes':
            cards = shelve.open(CARDFILE)
            keylist = cards.keys()
            for key in keylist:
                del cards[key]
            cards.close()
            dataFile = shelve.open(DATAFILE)
            keylist = dataFile.keys()
            for key in keylist:
                del dataFile[key]
            dataFile.close()
        print("Card file is cleared.") # Clear all cards from the catalogue.
    elif args[1] == 'topics':
        dataFile = shelve.open(DATAFILE)
        theKeys = dataFile.keys()
        listOfKeys = list(theKeys)
        for item in listOfKeys:
            if item == "topics":
                for topic in dataFile["topics"]:
                    print(topic)
        if listOfKeys == []:
            print("No topics or cards found.")
        dataFile.close() # Show topics of cards. Not that great.
    elif args[1] == 'view': # View cards, sorted by topic. Coming soon.
        pass

"""
class Card:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
"""
