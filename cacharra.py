
ipList = "[('10.42.0.92', 60406),('10.42.0.1', 33086)]"

resultList = []
ipList = ipList[1:-1]
ipList = ipList.split(',')
temp = None
for i in range(len(ipList)):
    if i % 2 == 0:
        temp = ipList[i][2:-1]
    else:
        resultList.append((temp,int(ipList[i][:-1])))
print(resultList)
# ipList = ipList.split(')')
# ipList = list(ipList.split(','))
# print(ipList)