# The codes below is for auto adjust CONFIG when a case is determined
# Total of 4 functions

def swapKeywordRow(CONFIG, A,B,C,D):
	# from A B C D to A C B D
	# print(A,B,C,D)
	# A 'right' B -> C
	if (CONFIG[A]['endObject']['right'] == B): 
		CONFIG[A]['endObject']['right'] = C;
	# B 'left' A -> C
	if (CONFIG[B]['endObject']['left'] == A): 
		CONFIG[B]['endObject']['left'] = C;
	# B 'right' C -> D
	if (CONFIG[B]['endObject']['right'] == C): 
		CONFIG[B]['endObject']['right'] = D;
	# C 'left' B -> A
	if (CONFIG[C]['endObject']['left'] == B): 
		CONFIG[C]['endObject']['left'] = A;
	# C 'right' D -> B
	if (CONFIG[C]['endObject']['right'] == D): 
		CONFIG[C]['endObject']['right'] = B;
	# D 'left' C -> B
	if (CONFIG[D]['endObject']['left'] == C): 
		CONFIG[D]['endObject']['left'] = B;
	#change 'row' and 'column'
	# CONFIG[B]['row'], CONFIG[C]['row'] = CONFIG[C]['row'], CONFIG[B]['row']
	# CONFIG[B]['column'], CONFIG[C]['column'] = CONFIG[C]['column'], CONFIG[B]['column']
	return CONFIG
	
def swapKeywordColumn(CONFIG, A,B,C,D):
	# from A to A
	# 	   B    C
	# 	   C    B
	# 	   D    D
	# print(A,B,C,D)
	# A 'bottom' B -> C
	if (CONFIG[A]['endObject']['bottom'] == B): 
		CONFIG[A]['endObject']['bottom'] = C;
	# B 'top' A -> C
	if (CONFIG[B]['endObject']['top'] == A): 
		CONFIG[B]['endObject']['top'] = C;
	# B 'bottom' C -> D
	if (CONFIG[B]['endObject']['bottom'] == C): 
		CONFIG[B]['endObject']['bottom'] = D;
	# C 'top' B -> A
	if (CONFIG[C]['endObject']['top'] == B): 
		CONFIG[C]['endObject']['top'] = A;
	# C 'bottom' D -> B
	if (CONFIG[C]['endObject']['bottom'] == D): 
		CONFIG[C]['endObject']['bottom'] = B;
	# D 'top' C -> B
	if (CONFIG[D]['endObject']['top'] == C): 
		CONFIG[D]['endObject']['top'] = B;
	#change 'row' and 'column'
	# CONFIG[B]['row'], CONFIG[C]['row'] = CONFIG[C]['row'], CONFIG[B]['row']
	# CONFIG[B]['column'], CONFIG[C]['column'] = CONFIG[C]['column'], CONFIG[B]['column']
	return CONFIG

def missKeywordRow(CONFIG, A,X,B):
	# from A X B to A B
	if (CONFIG[A]['endObject']['right'] == X):
		CONFIG[A]['endObject']['right'] = B
	if (CONFIG[B]['endObject']['left'] == X):
		CONFIG[B]['endObject']['left'] = A
	return CONFIG

def missKeywordColumn(CONFIG, A,X,B):
	# from A to A
	# 	   X    B
	#      B
	if (CONFIG[A]['endObject']['bottom'] == X):
		CONFIG[A]['endObject']['bottom'] = B
	if (CONFIG[B]['endObject']['top'] == X):
		CONFIG[B]['endObject']['top'] = A
	return CONFIG

# The codes below is for determining which case can be auto adjust
# 

def missKeyword(CONFIG, configS, targetS):
	missed = 0
	keyX = -1
	for i in range(len(targetS)):
		# print(len(configS), len(targetS))
		if (configS[i] == targetS[i]):
			pass
		else:
			if (configS[i+1] != targetS[i]):
				print("Miss key error: cannot auto")
				break
			else:
				keyX = i # according to configS array
				break
	if (keyX == -1):
		return missed, CONFIG, -1
	print("Miss key: auto adjust CONFIG")
	missed = 1
	print(configS[keyX-1], configS[keyX], configS[keyX+1])
	# print(CONFIG)
	if (CONFIG[configS[keyX-1]]['row'][0] == CONFIG[configS[keyX+1]]['row'][0]):
		CONFIG = missKeywordRow(CONFIG, configS[keyX-1], configS[keyX], configS[keyX+1])
	elif (CONFIG[configS[keyX-1]]['column'][0] == CONFIG[configS[keyX+1]]['column'][0]):
		CONFIG = missKeywordColumn(CONFIG, configS[keyX-1], configS[keyX], configS[keyX+1])
	return missed, CONFIG, keyX

def swapKeyword(CONFIG, configS, targetS):
    swapped = 0
    keyA = -1
    keyB = -1
    for i in range(len(configS)):
        # print(configS[i] == targetS[i])
        if (configS[i] != targetS[i]): 
            if (keyA == -1): 
                keyA = i
            elif (keyB == -1): 
                keyB = i
            else:
                print("Swap key error: cannot auto, more than 2 kw are swapped")
                return swapped, CONFIG, -1
    if (configS[keyA] != targetS[keyB] or configS[keyB] != targetS[keyA]):
        print("Swap key error: cannot auto")
        return swapped, CONFIG, -1
    elif ((keyA != -1) and (keyB != -1)):
        print("Swap key: auto adjust CONFIG")
        swapped = 2
        print(configS[keyA], configS[keyB])
        # print("Before:")
        # print(configS[keyA],": ",CONFIG[configS[keyA]])
        # print(configS[keyB],": ",CONFIG[configS[keyB]])
        if (CONFIG[configS[keyA]]['row'][0] == CONFIG[configS[keyB]]['row'][0]):
            # print(configS[keyA], configS[keyB])
            CONFIG = swapKeywordRow(CONFIG, configS[keyA-1], configS[keyA], configS[keyB], configS[keyB+1])
            
        elif (CONFIG[configS[keyA]]['column'][0] == CONFIG[configS[keyB]]['column'][0]):
            CONFIG = swapKeywordColumn(CONFIG, configS[keyA-1], configS[keyA], configS[keyB], configS[keyB+1])
        # print("After:")
        # print(configS[keyA],": ",CONFIG[configS[keyA]])
        # print(configS[keyB],": ",CONFIG[configS[keyB]])
        return swapped, CONFIG, [keyA, keyB]
    return swapped, CONFIG, -1

def checkForCase(CONFIG, configS, targetS):
	# for i in range(len(configS)):
	# 	if ("DATA" in configS[i]):
	# 		configS.pop(i)
	# for i in range(len(targetS)):
	# 	if ("DATA" in targetS[i]):
	# 		targetS.pop(i)
	case = 0
	# print(len(configS), len(targetS))
	# print(len(configS) > len(targetS))
	if (len(configS) > len(targetS)):
		# print("Miss key")
		print(len(configS), len(targetS))
		print(configS)
		print(targetS)
		# print(CONFIG)
		case, CONFIG, key = missKeyword(CONFIG, configS, targetS)
	elif (len(configS) == len(targetS)):
		# print("Swap key")
		# print(configS)
		# print(targetS)
		case, CONFIG, key = swapKeyword(CONFIG, configS, targetS)
	elif (len(configS) < len(targetS)):
		print("New key")
		case = 3
		key = -1
	return case, CONFIG, key

def replaceAliases(fullPdf, aliasD):
	# for key in aliasD: print(key)
	for key in aliasD:
		keyFound = 0
		for line in fullPdf:
			if (line.find(key) != -1):
				keyFound = 1
				# print(key)
				break
		if not keyFound:
			print(key)
			print(aliasD[key])
			aliList = []
			for ali in aliasD[key]:
				row = -1
				for line in fullPdf:
					row = row + 1
					if (line.find(ali) != -1):
						aliList.append((ali,row))
						break
			if (len(aliList) == 1):
				# print(aliList)
				print(fullPdf[aliList[0][1]])
				fullPdf[aliList[0][1]] = fullPdf[aliList[0][1]].replace(aliList[0][0],key)
				print(fullPdf[aliList[0][1]])
			if (len(aliList) == 2):
				# print(aliList)
				strA = aliList[0][0]
				strB = aliList[1][0]
				choose = aliList[0] if (strB in strA) else aliList[1]
				print(choose)
				fullPdf[choose[1]] = fullPdf[choose[1]].replace(choose[0],key)
	# for line in fullPdf:
	# 	print(line)
	return fullPdf