from openai import OpenAI
import time

# Added key here
with open("api_key.txt", "r") as file:
    api_key = file.read()
client = OpenAI(
    api_key=api_key,
)

# Added the assistant here
my_assistant = client.beta.assistants.retrieve("asst_9DQgg0cSnpmvioyIayNCMKNs")

def main():

    correct_count = 0
    incorrect_count = 0
    concepts_to_learn = []
    
    # Create a thread
    thread = client.beta.threads.create()


    def generate_question(user_level):
        
        if user_level <= 3:
            prompt = f"Create a level {user_level} difficulty multiple-choice question related to LIGN 101."
        else:
            prompt = f"Create a level {user_level} difficulty one-sentence-answer question related to LIGN 101."

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=my_assistant.id
        )
        
        # Check status
        while True:
            time.sleep(3)
            run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
            )
            if run.status == 'completed':
                break
            elif run.status == 'failed':
                return run.last_error

        messages = client.beta.threads.messages.list(
        thread_id=thread.id
        )
        
        return messages.data[0].content[0].text.value


    def answer_question(answer):

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"My answer: {answer}\n"
        )

        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=my_assistant.id
        )
        
        # Check status
        while True:
            time.sleep(3)
            run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
            )
            if run.status == 'completed':
                break
            elif run.status == 'failed':
                return run.last_error

        messages = client.beta.threads.messages.list(
        thread_id=thread.id
        )
        return messages.data[0].content[0].text.value
    
    
    def add_concepts():

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"What are the main concepts thatI need to know to answer this question? Give me one or two concepts in the format: [CONCEPT1, CONCEPT2]."
        )

        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=my_assistant.id
        )
        
        # Check status
        while True:
            time.sleep(3)
            run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
            )
            if run.status == 'completed':
                break
            elif run.status == 'failed':
                return run.last_error

        messages = client.beta.threads.messages.list(
        thread_id=thread.id
        )

        #['To answer this question, you should be familiar with the following concepts: ["Linguistic Hierarchy", "Morphemes"].']

        response = messages.data[0].content[0].text.value
        for c in response.strip('[]').split(', '):
            concepts_to_learn.append(c)



    def check_if_wrong(text):
        incorrect_keywords = ['incorrect', 'not correct', 'not accurate', 'inaccurate', 'wrong', 'sorry', 'okay', 'fine']
        return any(keyword in text.lower() for keyword in incorrect_keywords)
    
    def check_if_correct(text):
        correct_keywords = ['correct', 'right', 'great', 'good']
        return any(keyword in text.lower() for keyword in correct_keywords)
        

    # Initial user's level
    user_level = 3

    incorrect_answers = []

    while True:
        num_of_questions = input('\nHow many questions would you like to do? Please input a number: ')
        try:
            num_of_questions = int(num_of_questions)
        except ValueError:
            num_of_questions = 1

        for _ in range(num_of_questions):
            question = generate_question(user_level)
            user_input = input(question)
            if len(user_input) < 1:
                user_input = "Skip."
            
            print("\n Your response is: " + user_input + "\n")
            evaluation = answer_question(user_input)
            print(evaluation)

            if check_if_wrong(evaluation):
                # if wrong
                incorrect_answers.append((question, evaluation))
                incorrect_count += 1
                user_level = max(1, user_level - 1)
                add_concepts()
            elif check_if_correct(evaluation):
                # if correct
                correct_count += 1
                user_level = min(5, user_level + 1)
            else:
                # if hard to identify correctness
                incorrect_count += 1
                # Let's just keep the same level
                #user_level = max(5, user_level - 1)

        # Ask if the user wants to continue after each set of questions
        decision = input("\nWould you like to try other questions (Yes/No): ")
        if 'yes' not in decision.lower():
            break
    
    def print_summary(correct_count, incorrect_count):
        print("\n" + "="*110)
        print(f"You answered {correct_count} questions correctly and {incorrect_count} questions incorrectly.".center(110))
        

    def print_incorrect_answers_summary(incorrect_answers, concepts_to_learn):
        if not incorrect_answers:
            print("Great job! All your answers were correct.".center(110))
            print("="*110)
        else:
            # NEW BELOW
            print("\nHere are the concepts you may want to revisit:\n")
            print(f"{concepts_to_learn}\n")
            print("="*110)


            print("Review these questions and explanations to improve:")
            for idx, (question, explanation) in enumerate(incorrect_answers, 1):
                print(f"\n{idx}. Question: {question}".center(110))
                print(f"\n   Explanation: {explanation}".center(110))


    print_summary(correct_count, incorrect_count)
    print_incorrect_answers_summary(incorrect_answers, concepts_to_learn)
    
    def print_congratulatory_message(correct_count, incorrect_count):
        total_questions = correct_count + incorrect_count
        print("\n" + "="*110)
        print("🌟🌟🌟 CONGRATULATIONS! 🌟🌟🌟".center(110))
        print(f"You have completed a total of {total_questions} questions today.".center(110))
        print("Good luck on your finals!".center(110))
        print("="*110 + "\n")

    # Then call this function at the end of your main function
    print_congratulatory_message(correct_count, incorrect_count)


main()
