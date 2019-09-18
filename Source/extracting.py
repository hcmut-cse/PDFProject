from __future__ import division
import argparse
import os
import json
import numpy as np
from PdfExtractor.Source.preProcess import preProcessPdf
from PdfExtractor.Source.processData import extractData
from PdfExtractor.Source.posProcess import posProcessData
from PdfExtractor.Source.connectContent import connectContent
import pdftotext

PDF_FOLDER = '../PdfToExtract/'
TEMPLATE_FOLDER = '../Template/Temp/'
RESULT_FOLDER = '../Result/'

def extractingData(file, PDF_TYPE):

    with open(TEMPLATE_FOLDER + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
        ORIGINAL_CONFIG = json.load(json_file)

    print("========================================================")
    print(file)
    print("========================================================")

    print("- Pre-processing PDF for extracting...")
    CURR_CONFIG = {}
    CONFIG = {}
    HF_CONFIG = {}
    PDF_PAGES = 0

    # Preproces PDF
    fullPdf, removed, CONFIG, HF_CONFIG, PDF_PAGES = preProcessPdf(PDF_FOLDER + file, ORIGINAL_CONFIG)
    # for line in fullPdf:
    #     print(line)

    # Sort CONFIG from top to bottom, from left to right
    configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
    CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
    # print(CONFIG)

    # Create config for current pdf
    for key in CONFIG:
        CURR_CONFIG[key] = {}
        CURR_CONFIG[key]['row'] = CONFIG[key]['row'].copy()
        CURR_CONFIG[key]['column'] = CONFIG[key]['column'].copy()

    print("- Extracting information from PDF...")
    # Extract data from PDF
    extractedData = extractData(fullPdf, CONFIG, CURR_CONFIG, removed)

    print("- Pos-processing extracted data...")
    # Run pos-processing
    extractedData = leftProcess(CONFIG, extractedData)
    extractedData = subfieldProcess(CONFIG, extractedData)

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
