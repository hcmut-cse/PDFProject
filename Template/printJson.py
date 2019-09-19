import json
if __name__=='__main__':
	with open('1.json', 'r', encoding='utf8') as json_file:
		ORIGINAL_CONFIG = json.load(json_file)
		CONFIG = ORIGINAL_CONFIG[0].copy()
		for kw in CONFIG: print(kw,end=', ')
		print()
		print()

	with open('2_6_12.json', 'r', encoding='utf8') as json_file:
		ORIGINAL_CONFIG = json.load(json_file)
		CONFIG = ORIGINAL_CONFIG[0].copy()
		for kw in CONFIG: print(kw,end=', ')
		print()