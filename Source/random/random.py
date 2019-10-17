import json

def main():
	name0='4_merged.json'
	name1='4_temp.json'

	with open(name0, 'r', encoding='utf8') as json_file_0:
		config0=json.load(json_file_0)[0]
		with open(name1,'r',encoding='utf8') as json_file_1:
			config1=json.load(json_file_1)[0]

			# list0=[]
			# list1=[]
			# for key in config0: list0.append(key)
			# for key in config1: list1.append(key)
			# print(list0)
			# print(list1)
			# exit()

			forgottenList=[]
			for key in config1:
				if key not in config0: forgottenList.append(key)
			print(forgottenList)

			mistakenList=[]
			for key in config1: 
				if config0[key]!=config1[key]: mistakenList.append(key)

			print(mistakenList)

if __name__=='__main__': main()