import aiPart
import sys
from functools import partial
import threading
import time
import os
import subprocess
import json
import gc
import sys
import termios

tempHistory = []
isGeneratingResponse = False
chatMode = False

def listModels():
    for model in aiPart.modelList:
        print(f"{Colors.MAGENTA}{aiPart.modelList.index(model)}: {Colors.CYAN}{model}{Colors.ENDC}")

def selectModel():
    global outputLog
    if len(aiPart.modelList) > 0:
        listModels()
        print(f"select a model using the numbers 0 -> {len(aiPart.modelList) - 1}")
        try:
            userInputModelSelect = int(input("> "))
            aiPart.isLoadingModel = True
            aiPart.selectedModel = aiPart.modelList[userInputModelSelect]
            aiPart.reloadModel()
        except (ValueError, IndexError) as err:
            print(f"Raised Error: {err}")
    else:
        print(">> no models found <<")
        print("try refreshing the model list using >> rfmdls <<")

def getResponse():
    global tempHistory, isGeneratingResponse

    contextLimitedHistory = tempHistory.copy()
    max_history_chars = 2048 * 3
    while True:
        # Convert the whole list to a single string to check length
        current_content = "".join([str(msg) for msg in tempHistory])
        
        if len(current_content) > max_history_chars and len(tempHistory) > 1:
            # Remove the oldest message
            contextLimitedHistory.pop(0)
        else:
            break

    try:
        output = aiPart.llm.create_chat_completion(contextLimitedHistory, max_tokens=aiPart.maxTokens, frequency_penalty=aiPart.freqPenalty, temperature=aiPart.temperature, top_k=aiPart.topk)
        tempHistory.append(output["choices"][0]["message"])
        print(f"{aiPart.llm.metadata.get('general.name', 'Unknown Model')}: {output['choices'][0]['message']['content']}")
    except Exception as err:
        print(f"Raised Error: {err}")
    finally:
        time.sleep(2)
        isGeneratingResponse = False

def editConfigFile():
    if os.path.exists(aiPart.configFile):
        editor = os.environ.get('EDITOR', 'nano' if os.name != 'nt' else 'notepad')
        try:
            subprocess.run([editor, aiPart.configFile])
            aiPart.reloadModelParams()
            if aiPart.llm:
                aiPart.reloadModel()
        except Exception as err:
            print(f"Raised Error: {err}")

def saveChatHistory():
    if len(tempHistory) > 0:
        chatName = input("save chat name: ").strip()
        if not chatName:
            print(">> exitting, no name given <<")
            return
        while os.path.exists(os.path.join(aiPart.scriptPath, f"{chatName}.json")):
            tmpChs = input("do you wish to override it?\n(y/n/q):").lower()
            if tmpChs == "n":
                chatName = input("save chat name: ").strip()
            elif tmpChs == "y": break
            elif tmpChs == "q": return
        try:
            with open(os.path.join(aiPart.scriptPath, f"{chatName}.json"), "w") as chatSaveFile:
                json.dump(tempHistory, chatSaveFile, indent=2)
        except Exception as err:
            print(f"Raised Error: {err}")
    else:
        print(">> no history to save <<")

def loadChatHistory():
    global tempHistory
    chat = input("chat: ").strip()
    if os.path.exists(os.path.join(aiPart.scriptPath, chat)):
        try:
            with open(os.path.join(aiPart.scriptPath, chat), "r") as openTempChat:
                loadedTempChat = json.load(openTempChat)
                tempHistory = loadedTempChat
        except Exception as err:
            print(f"Raised Error: {err}")

def listDirectory():
    global outputLog
    elements = ""
    for element in os.listdir(aiPart.scriptPath):
        elements += f"  {Colors.MAGENTA}{element}{Colors.ENDC}  " if os.path.isdir(os.path.join(aiPart.scriptPath, element)) else f"  {Colors.CYAN}{element}{Colors.ENDC}  "
    print(elements)

def listCommands():
    commandsString = ""
    for cmd in commands:
        commandsString += f" {Colors.MAGENTA}'{Colors.RED}{cmd}{Colors.MAGENTA}'{Colors.ENDC} "
    print(commandsString)


def unloadModelCmd():
    if aiPart.llm:
        try:    
            tmpMdlN = aiPart.llm.metadata.get("general.name", "Unknown Model")
            aiPart.unloadModel()
            print(f">> '{Colors.CYAN}{tmpMdlN}{Colors.ENDC}' has been removed from memory <<")
        except Exception as err:
            print(f">> {Colors.RED}Failed{Colors.ENDC} to {Colors.CYAN}unload{Colors.ENDC} model <<")
            print(f"Raised Error: {err}")
            aiPart.llm = None
            gc.collect()
            print(f">> Forcing model out of {Colors.BLUE}memory{Colors.ENDC} <<")
            print(f">> Attempting to recover {Colors.BLUE}RAM{Colors.ENDC} <<")
    else:
        print(">> no model to unload <<")

def removeLastMessageFromChatHistory():
    global tempHistory
    if len(tempHistory) > 0:
        tempHistory.pop()
    else:
        print(">> no chat distory detected <<")

def setChatMode(): global chatMode; chatMode = not chatMode

class Colors:
    """ANSI color codes for the terminal."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'

commands = {
    "quit": partial(sys.exit, 0),
    "mdls": listModels,
    "rfmdls": aiPart.reloadModelList,
    "slmd": selectModel,
    "lscm": listCommands,
    "ulmd": unloadModelCmd,
    "dfconf": aiPart.reloadConfigFileToDefault,
    "edconf": editConfigFile,
    "svch": saveChatHistory,
    "clch": lambda: (tempHistory.clear(), print(">> chat history cleared <<")) if tempHistory else print(">> chat history is empty <<"),
    "ldch": loadChatHistory,
    "lsdr": listDirectory,
    "cls": partial(os.system, "clear"),
    "shch":  lambda: print(tempHistory),
    "popch": removeLastMessageFromChatHistory,
    "chat": setChatMode
}


loading_active = False
print("use 'lscm' to view commands or send a message to a loaded model by pressing ENTER")
while True:
    termios.tcflush(sys.stdin, termios.TCIFLUSH)
    if not isGeneratingResponse:
        if loading_active:
            # Clear the loading line before showing prompt
            sys.stdout.write("\r\033[K")  # Clear entire line
            loading_active = False
        
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    
        userInputText = input("> ") if not chatMode else input("- ")
        userInput = userInputText.strip().lower()

        if userInput in commands and not chatMode:
            commands[userInput]()
        elif userInput.startswith("sys(") and userInput.endswith(")") and not chatMode:
            command = userInput[4:-1]
            try:
                os.system(command)
            except Exception as err:
                print(f"Raised Error: {err}")
        
        else:
            if userInput and chatMode:
                if userInput == "./q":
                    chatMode = not chatMode
                    continue
                if aiPart.isLoadingModel:
                    print(">> model is still loading <<")
                    continue
                elif isGeneratingResponse:
                    print(">> model is busy <<")
                    continue
                elif not aiPart.llm:
                    print("No model loaded into memory.")
                    continue
                else:
                    isGeneratingResponse = True
                    tempHistory.append({"role": "user", "content": userInputText})
                    userInput = ""
                    userInputText = ""
                    threading.Thread(target=getResponse).start()
    else:
        if not loading_active:
            sys.stdout.write("loading...\n")
            sys.stdout.flush()
            loading_active = True
        time.sleep(0.1)
