import os
import json
import numpy as np
import pdftotext
from extracting import extractingData
from match.separateMatching import *
from TemplateMatching import * 



if __name__ == '__main__':

	fileName = list(filter(lambda pdf: pdf[-3:].lower() == 'pdf' ,os.listdir('../PdfToExtract')))
	jsonDir='../Template/*json'
	standardFolder='../Sample/'
	inputPath='../PdfToExtract'
	resultPath='../Result'


	# Maching process + generate a warning file (missing kw)
	with open(resultPath+'/performance.txt','w',encoding='utf8') as performanceFile:
		performanceFile.write('PERFORMANCE RECORDS\n\n')
		template,performanceResults = TemplateMatching(performanceFile)
		# import pdb
		# pdb.set_trace()
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
			if(int(PDF_TYPE) > 0):
				startTime=time.time()
				extractingData(file, PDF_TYPE)
				endTime=time.time()
				performanceResults[file].append(endTime-startTime)
			else: performanceResults[file].append(0)
			
			decorationPrint(performanceFile,'#',50)
			performanceFile.write(file+'\n')
			performanceFile.write('Matching time: '+str(performanceResults[file][0])+' seconds\n')
			performanceFile.write('Warning time: '+str(performanceResults[file][1])+' seconds\n')
			performanceFile.write('Extracting time: '+str(performanceResults[file][2])+' seconds\n')
			decorationPrint(performanceFile,'#',50)

