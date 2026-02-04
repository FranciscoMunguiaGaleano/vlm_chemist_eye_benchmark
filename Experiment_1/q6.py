#!/usr/bin/env python

import ollama
import os
import glob
from PIL import Image as PilImage
import random
import time
import statistics
import sys

# Define dataset path
DATASET_STANDING_NOT_CLASSIFIED = '/home/francisco/vlm_accuaracy/Experiment_1/STANDING_NOT_CLASSIFIED/0'
DATASET_PRONE = '/home/francisco/vlm_accuaracy/Experiment_1/STANDING_NOT_CLASSIFIED/1'
responses_to_invalid = []

def query_llm(img_path, query, llm):
    try:
        if not os.path.exists(img_path):
            print(f"Image file not found: {img_path}")
            return None

        with open(img_path, 'rb') as img_file:
            image_data = img_file.read()
            print(f"Querying LLM with image data of size: {len(image_data)} bytes")
            #'llava-phi3:latest'
            #'llama:7b'
            # deepseek-r1:1.5b
            response = ollama.chat(
                model= llm,
                messages=[
                    {
                        'role': 'user',
                        'content': query,
                        'images': [image_data],
                    }
                ],
            )

        return response.get('message', {}).get('content', '').strip().upper()
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return None

def get_strict_yes_no_response(img_path, query, llm, max_retries=3):
    """
    Ask the LLM a question and retry if the answer is not strictly 'YES' or 'NO'.
    """
    for attempt in range(max_retries):
        answer = query_llm(img_path, query, llm)
        print(f"Attempt {attempt+1} response: {answer}")
        if answer in ("YES", "NO"):
            return answer
    print("Warning: LLM gave ambiguous answer after retries. Defaulting to NO.")
    responses_to_invalid.append(answer)
    return "NO"  # or None if you prefer 

def menu():
    while True:
        choice = input("\nType 1 for setting the llm to llava-phi3:latest "
            "\nType 2  for setting the llm to llava:7b"
            "\nType 3 to terminate the programme."
            "\n >> ")
        if choice == '1':
            llm = 'llava-phi3:latest'
            print(f"LLM model: {llm}")
            break
        elif choice == '2':
            llm = 'llava:7b'
            print(f"LLM model: {llm}")
            break
        elif choice == '3':
            print(f"Terminating programme")
            sys.exit(1)
        else:
            print("Not a valid option")
    return llm



if __name__ == '__main__':
    try:
        llm = sys.argv[1]
        if llm == 'llava:7b' or llm == 'llava-phi:latest':
            print(f"LLM model: {llm}")
        else:
            print(f"[Warning] LLM model: {llm} does not exists, did you mean llava:7b or llava-phi:latest?")
            llm = menu()
    except:
        llm = menu()
    
    prone = True
    nonprone = True
    accuracy = 0
    accuracy_total = 200
    response_time = []
    q1 = 'Is the person standing? ONLY reply with YES or NO'
    q2 = 'Is the person walking? ONLY reply with YES or NO'
    q3 = 'What is the person doing?'


    
    try:
        if nonprone:
            image_paths = glob.glob(os.path.join(DATASET_STANDING_NOT_CLASSIFIED, '*.jpg'))
            print(f"Found {len(image_paths)} images")
            i = 1
            for img_path in image_paths:
                start = time.time()
                answer = query_llm(img_path, q3, llm)
                if 'KNEELING' in answer or 'KNEELS' in answer or 'SITTING' in answer or 'CROUCHING' in answer or 'BENDING OVER' in answer or 'BENDING DOWN' in answer or 'SQUATTING DOWN' in answer or 'LYING' in answer:
                    print("The person is prone")
                elif 'WALKING' in answer or 'WALKS' in answer or 'STANDING' in answer or 'CHECKING' in answer or 'EXAMINING' in answer or 'LOOKING' in answer or 'WORKING' in answer:
                    print('The person is standing or walking')
                    accuracy += 1
                else:
                    print(f"Ambiguous answer: {answer}")
                    print("Warning: LLM gave ambiguous answer after retries. Defaulting to NO to avoid false positives.")
                    responses_to_invalid.append(answer)
                    #accuracy += 1
                end = time.time()
                response_time.append(end - start)
                print(f"Current image: {i}")
                i+=1

            print(f"\nVLM Accuracy for prone detection: {accuracy}/{accuracy_total} "
                  f"({(accuracy / accuracy_total) * 100:.2f}%)")
            print(f"\nHallucinations: {100*len(responses_to_invalid)/200} %")
            print(f"\nAvergae time: {statistics.mean(response_time)}")
        if prone:
            image_paths = glob.glob(os.path.join(DATASET_PRONE, '*.jpg'))
            print(f"Found {len(image_paths)} images")

            for img_path in image_paths:
                start = time.time()
                answer = query_llm(img_path, q3, llm)
                if 'KNEELING' in answer or 'SITTING' in answer or 'CROUCHING' in answer or 'BENDING OVER' in answer or 'SQUATTING DOWN' in answer or 'LYING' in answer:
                    print("The person is prone")
                    accuracy += 1
                elif 'WALKING' in answer or 'WALKS' in answer or 'STANDING' in answer or 'CHECKING' in answer or 'EXAMINING' in answer or 'LOOKING' in answer or 'WORKING' in answer:
                    print('The person is standing or walking')
                else:
                    print(f"Ambiguous answer: {answer}")
                    print("Warning: LLM gave ambiguous answer after retries. Defaulting to NO to avoid false positives.")
                    responses_to_invalid.append(answer)
                end = time.time()
                response_time.append(end - start)
                print(f"Current image: {i}")
                i+=1
            print(f"\nFinal VLM Accuracy for prone detection: {accuracy}/{accuracy_total} "
                  f"({(accuracy / accuracy_total) * 100:.2f}%)")
            print(f"\nHallucinations: {100*len(responses_to_invalid)/200} %")
            print(f"\nAvergae time: {statistics.mean(response_time)}")

    except Exception as e:
        print(f"Error: {e}")

