money = '30k-50k'

money = money.split('-')
if 'k' in money[1]:
    maxmoney = int(money[1].strip('k')) * 1000
    minmoney = int(money[0].strip('k')) * 1000
    print(minmoney,maxmoney)


