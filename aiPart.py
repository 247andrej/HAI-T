from llama_cpp import Llama
import os
import json
import threading
import psutil

#--PATHS--
scriptPath = os.path.dirname(os.path.abspath(__file__))

modelsPath = os.path.join(scriptPath, "models")
if not os.path.exists(modelsPath):
    os.mkdir(modelsPath)

configFile = os.path.join(scriptPath, "config.json")
#------

#--VARIABLES--

llm = None
isLoadingModel = False
modelIsGenerating = False
modelList = []
modelList += [a for a in os.listdir(modelsPath) if a.endswith(".gguf")]
selectedModel = modelList[0] if len(modelList) > 0 else None
physical_cores = psutil.cpu_count(logical=False) or os.cpu_count()

contextLength = 1024
maxTokens = 200
temperature = 0.7
freqPenalty = 0.6

defaultConfigFileContent = {
    "context length": 1024,
    "max tokens": 200,
    "temperature": 0.7,
    "freq penalty": 0.6
}

#------

#--FUNCTIONS--

def reloadModel():
    global isLoadingModel, llm

    unloadModel()

    def loadModel():
        global llm, isLoadingModel
        try:
            llm = Llama(os.path.join(modelsPath, selectedModel), n_ctx=contextLength, flash_attn=False, verbose=False, n_gpu_layers=0, n_threads=physical_cores)
        except Exception as err:
            llm = None
            print(err)
        finally:
            isLoadingModel = False

    if selectedModel:
        isLoadingModel = True
        threading.Thread(target=loadModel).start()

def unloadModel():
    global llm
    if llm:
        llm.close()
        llm = None

def reloadModelList(): 
    global modelList
    modelList = []
    modelList += [a for a in os.listdir(modelsPath) if a.endswith(".gguf")]

def initConfigFile():
    if not os.path.exists(configFile):
        with open(configFile, "w") as tmpFlRd:
            json.dump(defaultConfigFileContent, tmpFlRd, indent=2)
initConfigFile()

def reloadModelParams():
    global contextLength, maxTokens, temperature, freqPenalty

    if os.path.exists(configFile):
        try:
            with open(configFile, "r") as readConfigFile:
                loadedConfigFile = json.load(readConfigFile)

                contextLength = loadedConfigFile.get("context length", 1024)
                maxTokens = loadedConfigFile.get("max tokens", 200)
                temperature = loadedConfigFile.get("temperature", 0.7)
                freqPenalty = loadedConfigFile.get("freq penalty", 0.6)

        except json.JSONDecodeError:
            initConfigFile()
reloadModelParams()

def reloadConfigFileToDefault():
    if os.path.exists(configFile):
        with open(configFile, "w") as tmpFlRd:
            json.dump(defaultConfigFileContent, tmpFlRd, indent=2)
#------