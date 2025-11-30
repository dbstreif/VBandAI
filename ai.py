from openai import OpenAI, APIError, AuthenticationError, RateLimitError
import keyboard
from time import sleep

WPM = 17
CHARSPACE = 1200 / WPM
WORD_SPACE = CHARSPACE * 7

BASE_URL = "https://openrouter.ai/api/v1"
with open("apikey.txt", encoding="utf-8") as file:
    API_KEY = file.readline().strip()

# Dictionary representing the morse code chart
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                   '(':'-.--.', ')':'-.--.-'}


def lang_to_morse(resp_list):
    print("Translating from lang to morse...")
    out_list = []
    for word in resp_list:
        morsew = ""
        for char in word:
            morsew += " " + MORSE_CODE_DICT[char.upper()]
        out_list.append(morsew)
    print(f"Finished with input:\n{resp_list}\nand output:\n{out_list}")

    return out_list


def openai_call(text: str):
    print("Call OpenAI API")
    client = OpenAI(
      base_url= BASE_URL,
      api_key= API_KEY
    )

    messages = [
        {
            'role': "developer",
            'content': [
            {
                'type': "text",
                'text': f"You are a chatbot hooked up to a morse code channel \
                        room where users communicate with you in morse code. \
                        Please engage with them by prompting them with \
                        questions and have a conversation as if you were \
                        actually talking on an HF frequency. \
                        You're callsign is: K6BOT \
                        Make sure you follow standard FCC procedure as if you \
                        were live on air, and also present the user with useful \
                        tips and corrections to help them improve. \
                        Sometimes you will encounter text that is not legible. \
                        If so, please try your best to understand or request \
                        the user to try again. \
                        Also, you do not send any morse code, just respond in \
                        english, I'll translate in software. \
                        You're dictionary of chars is: {MORSE_CODE_DICT}"
            }
        ]
        },
        {
            'role': 'user', 
            'content': text
        }
    ]

    try:
        response = client.chat.completions.create(
            model="x-ai/grok-4.1-fast:free",
            messages=messages,
            max_tokens=1000
        )
        print("Got Response")

        reply = response.choices[0].message.content
        print(f"Got Reply: {reply}")

        return {
            "status_code": 200,
            "response": reply
        }

    except AuthenticationError as e:
        print(f"Auth Error: {str(e)}")
        return {
            "status_code": 401,
            "error": f"Auth Error: {str(e)}"
        }

    except RateLimitError as e:
        print(f"Rate Limit Error: {str(e)}")
        return {
            "status_code": 429,
            "error": f"Rate Limit Error: {str(e)}"
        }

    except APIError as e:
        print(f"API Error: {str(e)}")
        return {
            "status_code": 500,
            "error": f"API Error: {str(e)}"
        }

    except Exception as e:
        print(f"Unknown Exception Occurred: {str(e)}")
        return {
            "status_code": 500,
            "error": f"Internal Error: {str(e)}"
        }


def ai_keyer(user_text):
    response = openai_call(user_text)
    morse_list = lang_to_morse(response)

    print("Keying...")
    for word in morse_list:
        for key in word:
            if key == '.':
                keyboard.press_and_release("left ctrl")
            elif key == '-':
                keyboard.press_and_release("right ctrl")
            else:
                sleep(CHARSPACE / 1000)

            sleep(0.005) # a little lag time for VBand

        sleep(WORD_SPACE / 1000)
    print("Done!")



def main():
    print("Started")
    while True:
        user_text = input()
        print(f"user_text = {user_text}")
        ai_keyer(user_text)


if __name__ == "__main__":
    main()
