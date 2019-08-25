import os
import json
import numpy as np
import pdftotext
from extracting import extractingData
from match.endUserMatchingED import *
from match.separateMatching import *



if __name__ == '__main__':

	fileName = list(filter(lambda pdf: pdf[-3:].lower() == 'pdf' ,os.listdir('../PdfToExtract')))

	# Maching process + generate a warning file (missing kw)
	template = TemplateMatching()

	# Extractor
	for file in fileName:
		print(file,template[file])

		PDF_TYPE = template[file]
		# jsonDir='../Template/*json'
		# standardFolder='../Sample/'
		# inputPath='../Test'
		# resultPath='../Result'
		# # Matching process
		# PDF_TYPE = findTemplateBetaVersion(path,file,jsonDir,standardFolder)
		# print(PDF_TYPE)

		# Extractor
		extractingData(file, PDF_TYPE)
