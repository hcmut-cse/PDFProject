import os

def compareTextFiles(resultFile,answerKeyFile):
	with open(resultFile,'r') as result:
		with open(answerKeyFile,'r') as answer:
			res=result.readlines()
			ans=answer.readlines()
			diff=[]
			lenRes=len(res)
			lenAns=len(ans)
			if (lenRes>lenAns): 
				l=lenRes
				for i in range(abs(lenRes-lenAns)): ans.append('\n')
			else: 
				l=lenAns
				for i in range(abs(lenRes-lenAns)): res.append('\n')
			for i in range(l):
				if (res[i]!=ans[i]): diff.append(i)

			return diff


def compareFolders(resultDir,answerKeyDir):
	print('Extracting comparison among files:')
	files=os.listdir(resultDir)
	files.sort()

	for file in files:
		if (file[-3:]=='txt' and 'performance' not in file and 'result' not in file):
			for i in range(50): print('#',end='')
			print()

			# import pdb
			# pdb.set_trace()
			# count=0
			# i=0
			# for c in file:
			# 	if (c=='_'): count+=1
			# 	if (count==2): 
			# 		answerKeyFile=file[(i+1):]
			# 		typeName=file[5:i]
			# 		break
			# 	i+=1
				# print(c,count)
			# answerKeyFiles=os.listdir(answerKeyDir+'/'+typeName)
			# if (answerKeyFile not in answerKeyFiles): continue
			resultFile=resultDir+'/'+file
			answerKeyFile=answerKeyDir+'/'+file
			print(resultFile)
			print(answerKeyFile)
			diff=compareTextFiles(resultFile,answerKeyFile)
			if (len(diff)):
				print('Wrong answers at lines: ',end='')
				for i in diff: print(i,end=' ')
				print()
			for i in range(50): print('#',end='')
			print()

def main():
	resultDir='../Result'
	answerKeyDir='../AnswerKey/2_6_12'
	compareFolders(resultDir,answerKeyDir)


if __name__=='__main__': main()