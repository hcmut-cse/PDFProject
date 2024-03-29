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
		template,performanceResults,configS,targetS,aliasD = TemplateMatching(performanceFile)
		# Extractor
		for file in fileName:

			

			pending_list = [8, 10, 11]
			PDF_TYPE,configS,targetS  = template[file]
			print(file,PDF_TYPE)
			# Extractor
			try:
				if(int(PDF_TYPE) > 0):
					startTime=time.time()
					extractingData(file, PDF_TYPE, configS, targetS, aliasD)
					endTime=time.time()
					performanceResults[file].append(endTime-startTime)
				else: performanceResults[file].append(0)
			
				decorationPrint(performanceFile,'#',50)
				performanceFile.write(file+'\n')
				performanceFile.write('Matching time: '+str(performanceResults[file][0])+' seconds\n')
				performanceFile.write('Warning time: '+str(performanceResults[file][1])+' seconds\n')
				performanceFile.write('Extracting time: '+str(performanceResults[file][2])+' seconds\n')
				decorationPrint(performanceFile,'#',50)

				if (int(PDF_TYPE) in pending_list):
					print("File " + file + " is in pending folder (" + str(PDF_TYPE) + ") which still has error in extracting!!!")
			except:
				print("File " + file + " has error while extracting!")


			
