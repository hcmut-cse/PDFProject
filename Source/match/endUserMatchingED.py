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
from match.utils import *
from difflib import SequenceMatcher
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red
from reportlab.lib.pagesizes import letter
from shutil import copyfile,rmtree
from bs4 import BeautifulSoup

def triggerWarning(path,file,template,configString,s,CONFIG,lineList,ans,standardFolder):
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
		for j in range(i+1,l-1):
			checkedKey=s[j]
			if (keywordRank[key]>keywordRank[checkedKey]):
				mishandledKws.append(key)
				mishandledKws.append(checkedKey)
				checked[key]=checked[checkedKey]=1
				break
	lenLineList=len(lineList)
	if (not (len(missingKws) or len(mishandledKws))): return
	startFilenamePos=len(path)
	modifiedFile=path+'/warning'+file[startFilenamePos:]
	copyfile(file,modifiedFile)
	sourceFolder=path+'/mummy'
	sourceFile=sourceFolder+file[startFilenamePos:]
	copyfile(file,sourceFile)
	# import pdb
	# pdb.set_trace()
	if (len(missingKws)):
		for key in missingKws:
			drawTextboxMissingKws(sourceFile,modifiedFile,key,configString,s,CONFIG,ans,standardFolder)
	if (len(mishandledKws)):
		count={}
		for key in mishandledKws: count[key]=0

		for i in range(lenLineList):
			for key in mishandledKws:
				if (lineList[i].find(key)!=-1): count[key]+=1

		for key in mishandledKws: 
			drawTextboxMishandled(key,sourceFile,modifiedFile,count,CONFIG)

def findTemplateBetaVersion(path,file,jsonDir,standardFolder):
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
		for s in sList:
			dis=getDamerauDistance(configString,s,aliasDict)

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
				# print(ans)
				targetConfigString=configString
				targetS=s
				targetCONFIG=CONFIG
		
	# print(file)
	if (minDistance>5): return -1,-1
	if (minDistance!=0): 	
		triggerWarning(path,file,ans,targetConfigString,targetS,targetCONFIG,lineList,ans,standardFolder)
	return ans,minDistance

def endUserSolve(resultFile,path,matchingFolder,jsonDir,standardFolder):
	return_dict = {}
	matchingFiles=glob.glob(matchingFolder)
	for file in matchingFiles:

		decorationPrint(resultFile,'-',36)
		ans,minDistance=findTemplateBetaVersion(path,file,jsonDir,standardFolder)

		# print(file,ans)
		
		if (ans==-1): resultFile.write(file[9:]+' unknown template\n')
		else:
			pos=re.search(path+'/',file).span()
			resultFile.write(file[pos[1]:]+' '+ans+'\n')
			if (minDistance!=0): resultFile.write('Warning: '+file[pos[1]:]+' doesn\'t fully match the template\n')
		decorationPrint(resultFile,'-',36)

		startFilenamePos=len(path+'/')
		# print(file[startFilenamePos:])

		return_dict[file[startFilenamePos:]] = ans

	return return_dict


def templateMatch(inputPath,resultPath,jsonDir,standardFolder):
	with open(resultPath+'/result.txt','w',encoding='utf8') as resultFile:
		if os.path.isdir(inputPath+'/'+'warning'):
			files=glob.glob(inputPath+'/'+'warning/*pdf') 
			for file in files: os.remove(file)
			os.rmdir(inputPath+'/'+'warning')
		if os.path.isdir(inputPath+'/'+'mummy'): 
			files=glob.glob(inputPath+'/'+'mummy/*pdf') 
			for file in files: os.remove(file)
			os.rmdir(inputPath+'/'+'mummy')
		os.makedirs(inputPath+'/'+'warning')
		os.makedirs(inputPath+'/'+'mummy')
		exactPath=inputPath+'/*pdf'
		decorationPrint(resultFile,'#',50)
		resultFile.write('MATCHING\n')
		return_dict = endUserSolve(resultFile,inputPath,exactPath,jsonDir,standardFolder)
		decorationPrint(resultFile,'#',50)
		rmtree(inputPath+'/mummy')

		if os.path.isdir(resultPath+'/'+'warning'):
			files=glob.glob(resultPath+'/'+'warning/*pdf') 
			for file in files: os.remove(file)
			os.rmdir(resultPath+'/'+'warning')
		os.makedirs(resultPath+'/'+'warning')

		warning = inputPath+'/warning/*pdf'
		warningFiles=glob.glob(warning)
		for file in warningFiles:
			startFilenamePos=len(inputPath+'/warning/')
			modifiedFile=resultPath+'/warning/'+file[startFilenamePos:]
			copyfile(file,modifiedFile)

		if os.path.isdir(inputPath+'/'+'warning'):
			files=glob.glob(inputPath+'/'+'warning/*pdf') 
			for file in files: os.remove(file)
			os.rmdir(inputPath+'/'+'warning')

	return return_dict
			



def TemplateMatching():
	jsonDir='../Template/*json'
	standardFolder='../Sample/'
	inputPath='../Test'
	resultPath='../Result'
	return_dict = templateMatch(inputPath,resultPath,jsonDir,standardFolder)
	return return_dict

