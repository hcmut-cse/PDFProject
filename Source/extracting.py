from __future__ import division
import argparse
import os
import json
import numpy as np
from PdfExtractor.Source.preProcess import preProcessPdf
from PdfExtractor.Source.processData import extractData
from PdfExtractor.Source.posProcess import leftProcess, subfieldProcess
from PdfExtractor.Source.connectContent import connectContent
import pdftotext
import copy
from SwapKw import *

PDF_FOLDER = '../PdfToExtract/'
TEMPLATE_FOLDER = '../Template/Merged/'
RESULT_FOLDER = '../Result/'

def constrain(x, min, max):
    if x < min:
        return min
    if x > max:
        return max
    return x

def extractProcess(fullPdf, CONFIG, removed, case, keynum, configS):
    # Sort CONFIG from top to bottom, from left to right
    configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
    CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
    # print(CONFIG)

    # Create config for current pdf
    # for key in CONFIG:
    #     CURR_CONFIG[key] = {}
    #     CURR_CONFIG[key]['row'] = CONFIG[key]['row'].copy()
    #     CURR_CONFIG[key]['column'] = CONFIG[key]['column'].copy()

    CURR_CONFIG = copy.deepcopy(CONFIG)

    print("- Extracting information from PDF...")
    # Extract data from PDF
    extractedData = extractData(fullPdf, CONFIG, CURR_CONFIG, removed)

    print("- Pos-processing extracted data...")
    # Run pos-processing
    extractedData = leftProcess(CONFIG, extractedData)
    extractedData = subfieldProcess(CONFIG, extractedData)
    if (case == 2):
        keyA = keynum[0]
        keyB = keynum[1]
        temp = extractedData[configS[keyA]]
        extractedData[configS[keyA]] = extractedData.pop(configS[keyB])
        extractedData[configS[keyB]] = temp

    return extractedData

def extractingData(file, PDF_TYPE, configS, targetS):

    with open(TEMPLATE_FOLDER + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
        ORIGINAL_CONFIG = json.load(json_file)

    print("========================================================")
    print(file)
    print("========================================================")

    print("- Pre-processing PDF for extracting...")
    CONFIG = {}
    HF_CONFIG = {}
    PDF_PAGES = 0

    # Preproces PDF
    fullPdf, removed, CONFIG, PDF_PAGES = preProcessPdf(PDF_FOLDER + file, ORIGINAL_CONFIG)
    # for line in fullPdf:
    #     print(line)

    if ("Multipages" in CONFIG):
        if (CONFIG['Multipages']):
            extractedData = dict()
            pageNumber = 0
            while pageNumber < len(fullPdf):
                pdfPage = fullPdf[pageNumber]

                CONFIG_TO_COPY = CONFIG["multi"][constrain(pageNumber, 0, len(CONFIG["multi"])-1)]
                config = dict()

                if pageNumber > 0:
                    for key in CONFIG_TO_COPY:
                        config[key+str(pageNumber)] = copy.deepcopy(CONFIG_TO_COPY[key])
                else:
                    config = copy.deepcopy(CONFIG_TO_COPY)

                case, config, keynum = checkForCase(config, configS, targetS)
                extractedData.update(extractProcess(pdfPage, config, removed, case, keynum, configS))
                pageNumber += 1
    else:
    	#Auto change CONFIG if missed/swapped
    	case, CONFIG, keynum = checkForCase(CONFIG, configS, targetS)
    	#then extract data
    	extractedData = extractProcess(fullPdf, CONFIG, removed, case, keynum, configS)

    print("- Connecting similar contents...")
    # If pdf have multi pages, we will check similar content and connect them
    if (PDF_PAGES > 1):
        extractedData = connectContent(PDF_PAGES, extractedData)

    print("- Writting result to file...")
    # Save extracted result to file
    with open(RESULT_FOLDER + file[:-3] + 'txt', 'w', encoding='utf8') as resultFile:
        for key in extractedData:
            resultFile.write("------------------------------------\n")
            resultFile.write("%s:\n%s\n" % (key, extractedData[key]))
            resultFile.write("------------------------------------\n")

    print("- Done!")
