from match.endUserMatchingED import *

def TemplateMatching(performanceFile):
	jsonDir='../Template/Merged/*json'
	standardFolder='../Sample/'
	inputPath='../PdfToExtract'
	resultPath='../Result'
	aliasFile='alias.xlsx'

	with open(resultPath+'/result.txt','w',encoding='utf8') as resultFile:
		if os.path.isdir(resultPath+'/'+'warning'):
			files=glob.glob(resultPath+'/'+'warning/*pdf') 
			for file in files: os.remove(file)
			os.rmdir(resultPath+'/'+'warning')
		if os.path.isdir(resultPath+'/'+'mummy'): 
			files=glob.glob(resultPath+'/'+'mummy/*pdf') 
			for file in files: os.remove(file)
			os.rmdir(resultPath+'/'+'mummy')
		os.makedirs(resultPath+'/'+'warning')
		os.makedirs(resultPath+'/'+'mummy')
		matchingPath=inputPath+'/*pdf'
		decorationPrint(resultFile,'#',50)
		resultFile.write('MATCHING\n')
		return_dict,performanceResults,configS,targetS,aliasD = endUserSolve(resultFile,inputPath,resultPath,matchingPath,jsonDir,standardFolder,aliasFile)
		decorationPrint(resultFile,'#',50)
		rmtree(resultPath+'/mummy')

			# if os.path.isdir(inputPath+'/'+'warning'):
			# 	files=glob.glob(inputPath+'/'+'warning/*pdf')
			# 	for file in files: os.remove(file)
			# 	os.rmdir(inputPath+'/'+'warning')

	return return_dict,performanceResults,configS,targetS,aliasD

