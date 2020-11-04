## Cards by Dan James
# Spaced-repetition command-line flashcard software to help with memorization.

Cards was conceived of a need for a simple flashcard utility available for free to all. It allows creation of flash cards,
each composed of a question, an answer, and an optional topic (to help keep them sorted when editing/changing them).
These cards will help the user memorize information according to the principles of spaced-repetition recall.

The user can create cards that contain a question that they wish to memorize the answer to, as well as an answer they
will be shown to evaluate the quality of the memorization. Due to the potential complexity of the user's answers,
evaluation is open-ended and left for the user to judge; as in, a user may recall the correct answer, but in a different
wording / configuration than stored on the card. As such, the user's intellectual integrity in the judgement of their
recall is paramount to the success of their learning with this system.

Once one or more cards have been created, the program will begin serving them for review. The review time is extended
based on whether or not the content has been properly memorized: Correct answers will increase the interval between
reviews, meaning it must be reviewed less often with time, while an incorrect recall will reset the interval to the
lowest tier and be served more frequently. The interval in this version is hard-coded according to the original Pimsleur
algorithm.

Cards can be edited or deleted as well.

Readme change