from __future__ import division
import os
import numpy as np
import cv2
from wand.image import Image
from bs4 import BeautifulSoup
import pandas as pd
from skimage.measure import compare_ssim
import pdftotext
import glob
import json
import fitz
import re
from difflib import SequenceMatcher
from shutil import copyfile,rmtree
import xlrd

def findFontSize(file,key):
	os.system('pdf2txt.py -o output.html -t html \''+file+'\'')
	htmlData = open('output.html', 'r')
	soup = BeautifulSoup(htmlData)
	font_spans = [ data for data in soup.select('span') if 'font-size' in str(data) ]
	output = []
	for i in font_spans:
		tup = ()
		fonts_size = re.search(r'(?is)(font-size:)(.*?)(px)',str(i.get('style'))).group(2)
		tup = (str(i.text).strip(),fonts_size.strip())
		output.append(tup)

	targetSize=14
	for out in output:
		if (out[0].find(key)!=-1):
			targetSize=int(out[1])
			break
	return targetSize

def remove_at(s, i):
	return s[:i] + s[i+1:]

def preProcessPdf(filename):
	# for filename in file:
	# Covert PDF to string by page
	# print(filename)
	with open(filename, "rb") as f:
		pdf = pdftotext.PDF(f)
	# Remove header & footer
	# print(len(pdf))
	if (len(pdf) > 1):
		# fullPdf = removeHeaderAndFooter(pdf)
		fullPdf = []
		for i in range(len(pdf)):
			if (pdf[i].strip() != ''):
				fullPdf.append(pdf[i].split('\n'))
		# Join PDF
		fullPdf = [line for page in fullPdf for line in page]
	else:
		fullPdf = pdf[0].split('\n')
	for page in fullPdf:
		i=fullPdf.index(page)
		fullPdf[i]=re.sub(r'^( )*[0-9]$','',fullPdf[i])

	# for page in fullPdf: print(page)
	return fullPdf

def initCONFIG(jsonFile):
	with open(jsonFile,'r',encoding='utf8') as json_file: ORIGINAL_CONFIG=json.load(json_file)
	if "Multipages" in ORIGINAL_CONFIG[0]:
		CONFIG=ORIGINAL_CONFIG[0]["1"].copy()
	else: CONFIG=ORIGINAL_CONFIG[0].copy()
	HF_CONFIG=ORIGINAL_CONFIG[1].copy()
	return CONFIG,HF_CONFIG

def decorationPrint(file,c,times):
	for i in range(times): file.write(c)
	file.write('\n')

def fixSpaceColonString(line):
	ans=re.sub(r'( )+:',' :',line)
	return ans

def createStringList(CONFIG):
	s=[]
	checked={}
	for key in CONFIG: checked[key]=0

	for key in CONFIG: 
		if (not checked[key]): 
			s.append(key)
			checked[key]=1
	finalS=s.copy()
	for key in s:
		if key.find('DATA')!=-1: finalS.remove(key)
	return finalS

def investigateAnalogy(a,b,aliasDict):
	if (a==b): return 1
	# print(a,b)
	if (a.lower() in aliasDict[b]): return 1
	if (b.lower() in aliasDict[a]): return 1
	return 0

def getEditDistance(s0,s1,aliasDict):
	l0=len(s0)
	l1=len(s1)
	dp=[[0 for j in range(l1+1)] for i in range(l0+1)]

	for i in range(l0+1):
		for j in range(l1+1):
			if (i==0): dp[i][j]=j
			elif (j==0): dp[i][j]=i
			elif (investigateAnalogy(s0[i-1],s1[j-1],aliasDict)): dp[i][j]=dp[i-1][j-1]
			else: dp[i][j]=1+min({dp[i-1][j],dp[i][j-1],dp[i-1][j-1]}) 
	return dp[l0][l1]

def getDamerauDistance(s0,s1,aliasDict):
	l0=len(s0)
	l1=len(s1)
	dp=[[0 for j in range(l1+1)] for i in range(l0+1)]

	for i in range(l0+1):
		for j in range(l1+1):
			if (i==0): dp[i][j]=j
			elif (j==0): dp[i][j]=i
			elif (investigateAnalogy(s0[i-1],s1[j-1],aliasDict)): dp[i][j]=dp[i-1][j-1]
			else: dp[i][j]=1+min({dp[i-1][j],dp[i][j-1],dp[i-1][j-1]}) 
			if (i>1 and j>1 and investigateAnalogy(s0[i-1],s1[j-2],aliasDict) and investigateAnalogy(s0[i-2],s1[j-1],aliasDict)): dp[i][j]=min(dp[i][j],dp[i-2][j-2]+1)
	return dp[l0][l1]

def fixScript(lineList):
	l=len(lineList)
	for i in range(l): lineList[i]=fixSpaceColonString(lineList[i])
	return lineList

def drawTextboxMissingKws(sourceFile,modifiedFile,key,configString,s,CONFIG,ans,standardFolder):
	doc=fitz.open(sourceFile)
	l=len(configString)
	# Search for first column in pdf
	tmpPage=doc[0]
	for tmpKey in s:
		if (len(tmpPage.searchFor(s[0]))): 
			startColumn=tmpPage.searchFor(s[0])[0][0]
			break
	index=0
	for page in doc:
		noApproximation=0
		# Warn based on other files
		homogeneousPdfFiles=glob.glob(standardFolder+ans+'/*pdf')
		for file in homogeneousPdfFiles:
			tmpDoc=fitz.open(file)
			tmpPage=tmpDoc[index]
			tmpLength=len(tmpPage.searchFor(key))
			if (tmpLength):
				targetFile=file
				for pos in tmpPage.searchFor(key):
					if (key=='Collect'):
						if (len(tmpPage.searchFor('Freight Collect'))): 
							FreightCollectPos=tmpPage.searchFor('Freight Collect')[0]
							if (FreightCollectPos[1]==pos[1]): continue
						if (len(tmpPage.searchFor('Total Collect'))): 
							TotalCollectPos=tmpPage.searchFor('Total Collect')[0]
							if (TotalCollectPos[1]==pos[1]): continue
					targetPos=pos
					noApproximation=1
					break
				if (noApproximation): break
		if (noApproximation):
			x0=targetPos[0]	
			y0=targetPos[1]	
			x1=targetPos[2]+len(key)*4	
			y1=targetPos[3]+10
			rect=fitz.Rect(x0,y0,x1,y1)
			highlight=page.addFreetextAnnot(rect,key,fontsize=12, fontname="helv", color=(1,0,0), rotate=0)	
			break
		index+=1

	if (not noApproximation):
		for page in doc:
			# Approximation
			targetSize=findFontSize(sourceFile,key)
			i=configString.index(key)
			latestKey=configString[0]
			nextKey=configString[i]
			for j in range(i-1,0,-1):
				if (configString[j] in s): 
					latestKey=configString[j]
					break
			for j in range(i+1,l):
				if (configString[j] in s):
					nextKey=configString[j]
					break
			if (nextKey.find('_')!=-1):
				barPos=nextKey.find('_')
				nextKey=nextKey[:barPos]
			if (nextKey==key): nextKey=CONFIG[key]['endObject']['bottom']
			if (not CONFIG[latestKey]['row'][1] or not CONFIG[latestKey]['row'][0]): numLines=1
			else: numLines=CONFIG[latestKey]['row'][1]-CONFIG[latestKey]['row'][0]
			if (not CONFIG[latestKey]['column'][1] or not CONFIG[latestKey]['column'][0]): width=1
			else: width=CONFIG[latestKey]['column'][1]-CONFIG[latestKey]['column'][0]
			latest_text_instances=page.searchFor(latestKey)
			if (page.searchFor(nextKey)):
				next_inst=page.searchFor(nextKey)[0]
				if (latest_text_instances):
					for inst in latest_text_instances:
						if (inst[3]<next_inst[1]):
							x0=inst[0]
							y0=(inst[3]+targetSize*numLines)
							if (CONFIG[latestKey]['row'][0]==CONFIG[key]['row'][0]): 
								y0=inst[1]
								x0+=width*(targetSize-5)
							else: x0=startColumn
							x1=x0+len(key)*targetSize*0.7
							y1=y0+targetSize*1.4
							rect=fitz.Rect(x0,y0,x1,y1)
							highlight=page.addFreetextAnnot(rect,key,fontsize=targetSize-2, fontname="helv", fill_color=(0, 1, 0), rotate=0)
				else:
					x0=next_inst[0]
					y0=(next_inst[1]-targetSize)
					if (nextKey in CONFIG):
						if (CONFIG[nextKey]['row'][0]==CONFIG[key]['row'][0]): 
							y0=next_inst[1]
							x0+=width*(targetSize-5)
						else: x0=startColumn
					x1=x0+len(key)*targetSize*0.7
					y1=y0+targetSize*1.4
					rect=fitz.Rect(x0,y0,x1,y1)
					highlight=page.addFreetextAnnot(rect,key,fontsize=targetSize-2, fontname="helv", fill_color=(1, 0, 0), rotate=0)
	doc.save(modifiedFile,garbage=4,deflate=True,clean=False)
	copyfile(modifiedFile,sourceFile)

def drawTextboxMishandled(key,sourceFile,modifiedFile,count,CONFIG,aliasDict):
	doc=fitz.open(sourceFile)
	for page in doc:
		text_instances=page.searchFor(key)
		if (not len(text_instances)):
			for tmpKey in aliasDict[key]:
				text_instances=page.searchFor(tmpKey)
				if (len(text_instances)): break
		for inst in text_instances: 
			trueInst=1
			if (count[key]>1):
				for margin in CONFIG[key]['endObject']:
					tmpKeys=CONFIG[key]['endObject'][margin]
					if (tmpKeys==-1): continue
					listTmpKey=[]
					lastPos=0
					l=len(tmpKeys)
					for i in range(l):
						if (tmpKeys[i]=='|'):
							listTmpKey.push(tmpKeys[lastPos:i])
							lastPos=i+1
					for tmpKey in listTmpKey:
						tmpKey=CONFIG[key]['endObject'][margin]
						if (tmpKey=='same_left'): tmpKey=CONFIG[key]['endObject']['left']
						if (tmpKey!=-1):
							if (margin=='top'):
								if (page.searchFor(tmpKey)):
									tmpPos=page.searchFor(tmpKey)[0]
									if (tmpPos[1]>inst[3]): 
										trueInst=0
										break
							elif (margin=='bottom'):
								if (page.searchFor(tmpKey)):
									tmpPos=page.searchFor(tmpKey)[0]
									if (tmpPos[3]<inst[1]):
										trueInst=0
										break
								else: trueInst=0
							elif (margin=='left'):
								if (page.searchFor(tmpKey)):
									tmpPos=page.searchFor(tmpKey)[0]
									if (tmpPos[0]>inst[2]):
										trueInst=0
										break
							else:
								if (page.searchFor(tmpKey)):
									tmpPos=page.searchFor(tmpKey)[0]
									if (tmpPos[2]<inst[0]):
										trueInst=0
										break
			if (trueInst):
				highlight=page.addHighlightAnnot(inst)
				highlight.setColors({"stroke": (0,1,0)})
				break

	doc.save(modifiedFile,garbage=4, deflate=True, clean=False)
	copyfile(modifiedFile,sourceFile)

def createListOfStringLineList(CONFIG,lineList,configString):
	l=len(lineList)
	checked={}
	ansList=[[configString[0]]]
	for key in CONFIG: checked[key]=0
	checked[configString[0]]=1
	aliasDict={}
	for key in CONFIG:
		aliasDict[key]=[]
		if ('alias' in CONFIG[key]):
			for alias in CONFIG[key]['alias']:
				aliasName=CONFIG[key]['alias'][alias]['name']
				aliasDict[key].append(aliasName)
	for i in range(l):
		posDict={}
		posList=[]
		for key in CONFIG:
			pos=lineList[i].find(key)
			if (pos!=-1):
				trueKey=1
				if (pos+len(key)<len(lineList[i])):
					if (lineList[i][pos+len(key)]<='Z' and lineList[i][pos+len(key)]>='A' and lineList[i][pos+len(key)-1]<='Z' and lineList[i][pos+len(key)-1]>='A'): trueKey=0
					if (lineList[i][pos+len(key)]<='z' and lineList[i][pos+len(key)]>='a' and lineList[i][pos+len(key)-1]<='z' and lineList[i][pos+len(key)-1]>='a'): trueKey=0
				if (trueKey):
					posDict[key]=pos
					posList.append(key)
			for alias in aliasDict[key]:
				pos=lineList[i].find(alias)
				if (pos!=-1):
					posDict[key]=pos
					posList.append(key)
					break
		posDict=dict(sorted(posDict.items(),key=lambda k:k[1]))
		for key in posDict: 
			if not (checked[key]):
				for s in ansList: s.append(key)
				checked[key]=1
			else:
				minDis=10000000000
				for ans in ansList:
					numWords=len(ansList[0])
					tmpConfig=configString[:numWords]
					tmpDis=getEditDistance(ans,tmpConfig,aliasDict)
					if (tmpDis<minDis):
						minDis=tmpDis
						chosenAns=ans
				tmp=chosenAns.copy()
				tmp.remove(key)
				tmp.append(key)
				ansList.append(tmp)
	return ansList,aliasDict

# Create list keyword from other template to make data
def createData(PDF, keyword,CURR_KW):
	workbook = xlrd.open_workbook('alias.xlsx')
	sheet = workbook.sheet_by_index(0)
	for i in range (sheet.nrows):
		for j in range (sheet.ncols):
			if (sheet.cell(i, j).value == ''):
				continue
			CURR_KW[sheet.cell(i, j).value] = 1
# Make data keyword for test template
def currDataTemp(str_templateCheck, listCheck):
	with open('../' + 'Template' + '/' + 'Merged' + '/' + str_templateCheck + '.json', 'r', encoding='utf8') as json_file:
		ORIGINAL_CONFIG_CHECK = json.load(json_file)
	CONFIG_CHECK = ORIGINAL_CONFIG_CHECK[0].copy()
	# listCheck = []
	for key in CONFIG_CHECK:
		# key = key.lower()
		key = re.sub(r'[0-9]+', '', key)
		key = key.replace("_","")
		listCheck.append(key)
	return listCheck
# preProcess Text to seperate word with 2 or more space
def preProcessText(listPdf, fullPdf):
	for line in fullPdf:
		# line = line.lower()
		listLine = []
		listLine = re.split("\\s \\s+", line)
		listPdf.append(listLine)
	return listPdf
# Check if keyword in data
def detectInData(fullPdf, listCheck, CURR_KW, newKw,listPdf):
	# for listLine in listPdf:
	# 	for ele in listLine:
	# 		ele = ele.replace(":","")
	# 		ele = ele.strip()
	# 		for key in CURR_KW:
	# 			if (ele == key):
	# 				if ele not in listCheck:
	# 					listCheck.append(ele)
	# 					newKw.append(ele)
	# return newKw

	for listLine in listPdf:
		for ele in listLine:
			if (":" in ele):
				ele = ele.replace(":","")
				ele = ele.replace(r'[0-9]+',"")
				ele = ele.strip()
				for key in CURR_KW:
					if (key in ele):
						if ele not in listCheck:
							#listCheck.append(ele)
							newKw.append(ele)
	return newKw
def proNewKey(newKw, CURR_KW, listCheck):
	# for key in CURR_KW:
	# 	print(key)
	# for key in newKw:
	# 	print(key)
	newList = []
	for new in newKw:
		for key in CURR_KW:
			if key in new:
				#print(key)
				if key not in listCheck:
					newList.append(key)
	newKw = newList
	return newKw
def generateListNewKws(file,template,CURR_KW,jsonDir):
	newKw = []
	listPdf = []
	listCheck = []

	templateFiles=glob.glob(jsonDir)
	starPos=jsonDir.find('*')
	PDF=[]
	for templateFile in templateFiles:
		jsonPos=templateFile.find('.json')
		PDF.append(templateFile[starPos:jsonPos])

	fullPdf=preProcessPdf(file)
	# Data of test template
	listCheck = currDataTemp(template, listCheck)
	# Take keyword from others template to make data
	keyword = []
	createData(PDF,keyword,CURR_KW)
	listPdf = preProcessText(listPdf, fullPdf)
	# for line in listPdf:
	#     print(line)
	newKw = detectInData(fullPdf, listCheck, CURR_KW, newKw,listPdf)
	newKw = proNewKey(newKw, CURR_KW, listCheck)
	#newKw = detectNotInData(fullPdf, listCheck, CURR_KW, newKw,listPdf)
	# print(newKw)
	return newKw

def drawTextboxNewKws(key,sourceFile,modifiedFile,CONFIG):
	doc=fitz.open(sourceFile)
	for page in doc:
		text_instances=page.searchFor(key)
		for inst in text_instances: 
			highlight=page.addHighlightAnnot(inst)
			highlight.setColors({"stroke": (1,0,1)})
					
	doc.save(modifiedFile,garbage=4, deflate=True, clean=False)
	copyfile(modifiedFile,sourceFile)

