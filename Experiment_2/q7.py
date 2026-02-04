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
DATASET_PPE = '/home/francisco/vlm_accuaracy/Experiment_2/PPE_NOT_CLASSIFIED/1'
DATASET_NOT_PPE = '/home/francisco/vlm_accuaracy/Experiment_2/PPE_NOT_CLASSIFIED/0'
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
            response = ollama.chat(
                #model='llava-phi3:latest',
                model= llm,
                #model='llama3.2-vision:latest',
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
    return "YES"  # or YES for reducing false positives

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
    
    ppe = True
    nonppe = True
    accuracy = 0
    accuracy_total = 200
    response_time = []
    query = 'Is the person wearing a lab coat? ONLY reply with YES or NO.'
    
    try:
        if nonppe:
            image_paths = glob.glob(os.path.join(DATASET_NOT_PPE, '*.jpg'))
            print(f"Found {len(image_paths)} images")
            i = 1
            for img_path in image_paths:
                start = time.time()
                answer = get_strict_yes_no_response(img_path, query, llm)
                if answer == "YES":
                    # Second query: is the person standing?
                    print("The person is wearing PPE")
                else:
                    print("The person is not wearing PPE")
                    accuracy += 1
                #print(f"Image {accuracy_total}")
                end = time.time()
                response_time.append(end - start)
                print(f"Current image: {i}")
                i+=1

            print(f"\nVLM Accuracy for PPE detection: {accuracy}/{accuracy_total} "
                  f"({(accuracy / accuracy_total) * 100:.2f}%)")
            print(f"\nHallucinations: {100*len(responses_to_invalid)/200} %")
            print(f"\nAverage time: {statistics.mean(response_time)}")
        if ppe:
            image_paths = glob.glob(os.path.join(DATASET_PPE, '*.jpg'))
            print(f"Found {len(image_paths)} images")

            for img_path in image_paths:
                start = time.time()
                answer = get_strict_yes_no_response(img_path, query, llm)
                if answer == "YES":
                    # Second query: is the person standing?
                    print("The person is wearing PPE")
                    accuracy += 1
                else:
                    print("The person not wearing PPE")
                #print(f"Image {accuracy_total}")
                end = time.time()
                response_time.append(end - start)
                print(f"Current image: {i}")
                i+=1
            print(f"\nFinal VLM Accuracy for PPE detection: {accuracy}/{accuracy_total} "
                  f"({(accuracy / accuracy_total) * 100:.2f}%)")
            print(f"\nHallucinations: {100*len(responses_to_invalid)/200} %")
            print(f"\nAverage time: {statistics.mean(response_time)}")

    except Exception as e:
        print(f"Error: {e}")
