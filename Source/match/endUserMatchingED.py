from __future__ import division
import os
import numpy as np
import cv2
from wand.image import Image
from skimage.measure import compare_ssim
import pdftotext
import glob
import json
import re
import fitz
from .utils import *
from difflib import SequenceMatcher
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red
from reportlab.lib.pagesizes import letter
from shutil import copyfile,rmtree
from bs4 import BeautifulSoup
import time

def triggerWarning(inputPath,resultPath,file,template,configString,s,CONFIG,lineList,ans,standardFolder,CURR_KW,aliasDict,newKwList):
	# Find missing keywords
	missingKws=[key for key in configString if key not in s]
	# Examine if the order of keywords is caused damaged
	keywordRank={}
	mishandledKws=[]
	checked={}
	l=len(s)
	for key in configString: 
		keywordRank[key]=configString.index(key)
		checked[key]=0
	for key in s:
		if (checked[key]): continue
		i=s.index(key)
		for j in range(i+1,l):
			checkedKey=s[j]
			if (keywordRank[key]>keywordRank[checkedKey]):
				if key not in mishandledKws: mishandledKws.append(key)
				if checkedKey not in mishandledKws: mishandledKws.append(checkedKey)
				checked[key]=checked[checkedKey]=1
				break
	lenLineList=len(lineList)
	if (not (len(missingKws) or len(mishandledKws) or len(newKwList))): return
	# if (not (len(missingKws) or len(mishandledKws))): return
	doc=fitz.open(file)
	page=doc[0]
	if (not len(page.searchFor(configString[0]))): missingKws.append(configString[0])
	startFilenamePos=len(inputPath)
	modifiedFile=resultPath+'/warning'+file[startFilenamePos:]
	copyfile(file,modifiedFile)
	sourceFolder=resultPath+'/mummy'
	sourceFile=sourceFolder+file[startFilenamePos:]
	copyfile(file,sourceFile)
	numKeyProcessing=0

	realMissingKws=[]
	for key in missingKws:
		if key.find('DATA')!=-1: continue
		realMissingKws.append(key)
	if (len(realMissingKws)):
		for key in realMissingKws:
			drawTextboxMissingKws(sourceFile,modifiedFile,key,configString,s,CONFIG,ans,standardFolder)
			numKeyProcessing+=1

	if (len(mishandledKws)):
		count={}
		for key in mishandledKws: count[key]=0
		for page in doc:
			for key in mishandledKws: count[key]+=len(page.searchFor(key))

		# Fixing tiny distance keywords
		realMishandledKws=[]
		l=len(mishandledKws)
		for i in range(l-1):
			if (CONFIG[mishandledKws[i]]['column'][0]): firstCol0=CONFIG[mishandledKws[i]]['column'][0]
			else: firstCol0=0
			if (CONFIG[mishandledKws[i+1]]['column'][0]): secondCol0=CONFIG[mishandledKws[i+1]]['column'][0]
			else: secondCol0=0
			distance=abs(firstCol0-secondCol0)
			if (distance<60): realMishandledKws.append(mishandledKws[i])
		for key in realMishandledKws: 
			drawTextboxMishandled(key,sourceFile,modifiedFile,count,CONFIG,aliasDict)
			numKeyProcessing+=1
		###############################

		# for key in mishandledKws: 
		# 	drawTextboxMishandled(key,sourceFile,modifiedFile,count,CONFIG,aliasDict)
	if (len(newKwList)):
		for key in newKwList: 
			drawTextboxNewKws(key,sourceFile,modifiedFile,CONFIG)
			numKeyProcessing+=1
	if (numKeyProcessing==0): os.remove(modifiedFile)


def findTemplateBetaVersion(inputPath,resultPath,file,jsonDir,standardFolder,CURR_KW,startTime):
	jsonFiles=glob.glob(jsonDir)
	minDistance=100000
	starPos=jsonDir.find('*')
	for jsonFile in jsonFiles:
		CONFIG,HF_CONFIG=initCONFIG(jsonFile) # HF_CONFIG for fun
		lineList=preProcessPdf(file)
		lineList=fixScript(lineList)
		for key in CONFIG: key=fixSpaceColonString(key)
		configString=createStringList(CONFIG)
		sList,aliasDict=createListOfStringLineList(CONFIG,lineList,configString)
		# New keys
		newKwList=generateListNewKws(file,jsonFile[starPos:-5],CURR_KW,jsonDir)
		for key in newKwList:
			for tmpKey in aliasDict:
				found=0
				for element in aliasDict[tmpKey]:
					if element.find(key)!=-1: 
						newKwList.remove(key)
						found=1
						break
				if (found): break
		for s in sList:
			dis=getDamerauDistance(configString,s,aliasDict)
			dis+=len(newKwList)*0.5
			# Testing===========================================================================
			# print('=========================================================================')
			# print('Standard string:',configString)
			# print('Target S:',s)
			# print('Distance:',dis)
			# print('Template:',jsonFile[starPos:-5])
			# print('=========================================================================')
			# Testing==========================================================================
			if (minDistance>dis): 
				minDistance=dis
				ans=jsonFile[starPos:-5]
				targetConfigString=configString
				targetS=s
				targetCONFIG=CONFIG
				targetAliasDict=aliasDict
				targetNewKwList=newKwList
				# Testing===========================================================================
				# print('=========================================================================')
				# print('Standard string:',configString)
				# print('Target S:',s)
				# print('Distance:',minDistance)
				# print('Template:',jsonFile[starPos:-5])
				# print('New keywords:',newKwList)
				# print('=========================================================================')
				if (minDistance==0 or minDistance>15): break
				# Testing==========================================================================
		if (minDistance==0): break

	# Calculate matching time
	for i in range(50): print('#',end='')
	print()
	pathPos=re.search(inputPath,file).span()
	print(file[pathPos[1]+1:])
	endMatchingTime=time.time()
	matchingTime=endMatchingTime-startTime
	# print('Matching time:',endTime-startTime,'seconds')
	#############################################################

	# print(file)
	if (minDistance>8): return -1,-1
	if (minDistance!=0): 	
		triggerWarning(inputPath,resultPath,file,ans,targetConfigString,targetS,targetCONFIG,lineList,ans,standardFolder,CURR_KW,targetAliasDict,targetNewKwList)
		
		# Calculate matching time
		endWarningTime=time.time()
		warningTime=endWarningTime-endMatchingTime		
	else: warningTime=0
		# print('Warning time:',endTime-startTime,'seconds')
		#############################################################


	# Terminate outputing overall time of a file
	for i in range(50): print('#',end='')
	print()
	#############################


	#############################
	# configString: standard list of keywords
	# targetS: list of keywords in PDF 

	print(configString)
	print(targetS)	
	#############################

	# return ans,minDistance
	return ans,minDistance,matchingTime,warningTime,configString,targetS

def endUserSolve(resultFile,inputPath,resultPath,matchingFolder,jsonDir,standardFolder,performanceFile):
	return_dict = {}

	matchingFiles=glob.glob(matchingFolder)
	matchingFiles.sort()
	CURR_KW={}
	for file in matchingFiles:
		startTime=time.time()
		ans,minDistance,matchingTime,warningTime,configString,targetS=findTemplateBetaVersion(inputPath,resultPath,file,jsonDir,standardFolder,CURR_KW,startTime)

		pos=re.search(inputPath+'/',file).span()
		performanceFile.write(file[pos[1]:]+'\n')
		performanceFile.write('Matching Time: '+str(matchingTime)+' seconds\n')
		performanceFile.write('Warning Time: '+str(warningTime)+' seconds\n')

		if (ans==-1):
			resultFile.write(file[pos[1]:]+' unknown template\n')
		else:
			resultFile.write(file[pos[1]:]+' '+ans+'\n')
			if (minDistance!=0): resultFile.write('Warning: '+file[pos[1]:]+' doesn\'t fully match the template\n')
			# New key===============================================
			# resultFile.write('New keywords: ')
			# for key in generateListNewKws(file,ans,CURR_KW): resultFile.write(key+'\n')
			# resultFile.write('\n')
			# ======================================================
		startFilenamePos=len(inputPath+'/')
		return_dict[file[startFilenamePos:]] = ans
		decorationPrint(resultFile,'#',50)
		decorationPrint(performanceFile,'#',50)


	return return_dict


def templateMatch(inputPath,resultPath,jsonDir,standardFolder):
	with open(resultPath+'/result.txt','w',encoding='utf8') as resultFile:
		with open(resultPath+'/performance.txt','w',encoding='utf8') as performanceFile:
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
			decorationPrint(performanceFile,'#',50)
			resultFile.write('MATCHING\n')
			endUserSolve(resultFile,inputPath,resultPath,matchingPath,jsonDir,standardFolder,performanceFile)
			decorationPrint(resultFile,'#',50)
			decorationPrint(performanceFile,'#',50)
			rmtree(resultPath+'/mummy')



# def main():
# 	jsonDir='../template/*json'
# 	standardFolder='../sample/'
# 	inputPath='../matching/random'
# 	resultPath='../result'
# 	templateMatch(inputPath,resultPath,jsonDir,standardFolder)
	
# if __name__=='__main__': main()