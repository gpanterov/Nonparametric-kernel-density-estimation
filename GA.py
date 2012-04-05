# Code for runnint a genetic algorithm on the order book data
# Each gene in the chromosome will be the percentage of orders/traders
# that are currently in the market at each tick

# The fitness function will be the standard deviation of the next order

# (later you may do with profit functions) but this is more scientific

import numpy as np
from datetime import datetime, timedelta
import csv
import copy

#Load the data. Three files
f1=open("_Bids.csv","r");
f2=open("_Asks.csv","r")
f3=open("_Changes.csv","r")
F1=csv.reader(f1)
F2=csv.reader(f2)
F3=csv.reader(f3)

BidPrices=[]
AskQty=[]
BidQty=[]
AskPrices=[]
Changes=[]
for line in F1:
    BidPrices.append([float(i) for i in line])
    
    line=F1.next()
    BidQty.append([int(i) for i in line])
print "Bids Loaded"
for line in F2:
    AskPrices.append([float(i) for i in line])
    
    line=F2.next()
    AskQty.append([int(i) for i in line])
print "Asks Loaded"
for line in F3:
    line[0]=float(line[0])  # price
    line[1]=int(line[1])  #size
    Changes.append(line)
print "Changes Loaded"

# Get the tick size. Estimate it by calculating the smallest difference between two consecutive prices
Ticks=[i[0] for i in Changes]
Ticks.sort()
new_Ticks=set(Ticks)
new_Ticks=list(new_Ticks)
new_Ticks.sort()
dif_Ticks=np.array(new_Ticks[1::])- np.array(new_Ticks[0:-1])
tick_size=min(dif_Ticks)
print "The minimum ticksize is:", tick_size

class OrderBook():
    def __init__(self, Ask_Prices,Ask_Qty, Bid_Prices, Bid_Qty, Changes,tick_size):
        self.Ask_Prices=Ask_Prices
        self.Ask_Qty=Ask_Qty
        self.Bid_Prices=Bid_Prices
        self.Bid_Qty=Bid_Qty
        self.Changes=Changes
        self.line=-1
        self.tick_size=tick_size
        
        self.Next()
        
        Time=self.Changes[-1][-1]
        Time=Time.split()
        Time1=Time[0]; Time2=Time[1]
        Time1=Time1.split("-"); Time2=Time2.split(":")
        self.Time_last_obs=datetime(int(Time1[0]),int(Time1[1]),int(Time1[2]),int(Time2[0]),int(Time2[1]),int(Time2[2]))

        
    def Next(self):
        self.line+=1
        i=self.line
        self.Ask=AggregateBook(self.Ask_Prices[i],self.Ask_Qty[i],self.tick_size)
        self.Bid=AggregateBook(self.Bid_Prices[i],self.Bid_Qty[i],self.tick_size)
        self.Bid_Ticks=self.Bid.keys(); self.Bid_Ticks.sort()
        self.Ask_Ticks=self.Ask.keys(); self.Ask_Ticks.sort()
        # keep record of the time
        Time=self.Changes[i][-1]
        Time=Time.split()
        Time1=Time[0]; Time2=Time[1]
        Time1=Time1.split("-"); Time2=Time2.split(":")
        self.Time=datetime(int(Time1[0]),int(Time1[1]),int(Time1[2]),int(Time2[0]),int(Time2[1]),int(Time2[2]))
        
        
        

class AskPosition():
    def __init__(self,nTicks,Book):
        
        self.Book=copy.deepcopy(Book)
        self.TimeOpen=self.Book.Time
        self.OpenPr=self.Book.Ask_Ticks[0]
        
        self.PosPr=self.Book.Ask[self.Book.Ask_Ticks[nTicks]]
        self.Stocks2Fill={}
        for i in range(nTicks+1):
            Pr=self.Book.Ask_Ticks[i]
            self.Stocks2Fill[Pr]=self.Book.Ask[Pr]
            
class Chromosomes():
    def __init__(self,n_bids,n_asks,pos_depth,stopLoss,takeProfit,time_exp):
        self.OpenPos=False
        self.Profits=[]
        self.Bids, self.Asks=self.BookConditions(n_bids,n_asks)
        self.pos_depth,self.stopLoss,self.takeProfit,self.time_exp=self.TradingStrategy(pos_depth,stopLoss,takeProfit,time_exp)
        
    def BookConditions(self,n_bids,n_asks,r=0.2):
        Asks={}
        Bids={}
        
        
        self.n=n_bids+n_asks
        for i in range(n_asks):
            l=np.random.uniform(0,r);
            u=np.random.uniform(l,2*r)
            
            Asks[i]=(l,u)
        for i in range(n_bids):
            l=np.random.uniform(0,r);
            u=np.random.uniform(l,2*r)
            Bids[i]=(l,u)
            
        return Bids, Asks
    
    def TradingStrategy(self,pos_depth,stopLoss,takeProfit,time_exp):
        return pos_depth,stopLoss,takeProfit,time_exp
    
    def Shrink(self,p):
        for i in self.Asks:
            if np.random.uniform()<p:
                l,u=self.Asks[i]
                s1=np.random.uniform(l,(u-l)/2.0)
                s2=np.random.uniform((u-l)/2.0,u)
                l+=s1; u-=s2;
                self.Asks[i]=(l,u)
        for i in self.Bids:
            if np.random.uniform()<p:
                l,u=self.Bids[i]
                s1=np.random.uniform(l,(u-l)/2.0)
                s2=np.random.uniform((u-l)/2.0,u)
                l+=s1; u-=s2;
                self.Bids[i]=(l,u)
                
    def Expand(self,p):
        for i in self.Asks:
            if np.random.uniform()<p:
                l,u=self.Asks[i]
                s1=np.random.uniform(0,l)
                s2=np.random.uniform(u,1)
                
                self.Asks[i]=(s1,s2)
        for i in self.Bids:
            if np.random.uniform()<p:
                l,u=self.Bids[i]
                s1=np.random.uniform(0,l)
                s2=np.random.uniform(u,1)
                
                self.Bids[i]=(s1,s2)
                
    def Shift(self,p):
        for i in self.Asks:
            if np.random.uniform()<p:
                l,u=self.Asks[i]
                s1=np.random.uniform(0,l)
                s2=np.random.uniform(u,1)
                
                if np.random.uniform()<0.5:  # There is a 50% chance of shift up or shift down.
                    self.Asks[i]=(l-s1,u-s1)
                else:
                    self.Asks[i]=(l+s2,u+s2)
                    
        for i in self.Asks:
            if np.random.uniform()<p:
                l,u=self.Bids[i]
                s1=np.random.uniform(0,l)
                s2=np.random.uniform(u,1)
                
                if np.random.uniform()<0.5:
                    self.Bids[i]=(l-s1,u-s1)
                else:
                    self.Bids[i]=(l+s2,u+s2)
                    
    def Remove(self,p):
        for i in self.Asks:
            if np.random.uniform()<p:
                del self.Asks[i]
        for i in self.Bids:
            if np.random.uniform()<p:
                del self.Bids[i]
                
    def Add(self,p,r=0.1):
        if np.random.uniform()<p:
            i=np.random.poisson(max(self.Asks.keys()))
            try:
                self.Asks[i]
            except KeyError:   
                l=np.random.uniform(0,r)
                u=np.random.uniform(r,2*r)
                self.Asks[i]=(l,u)
                          
        if np.random.uniform() < p :
            i=np.random.poisson(max(self.Bids.keys()))
            try:
                self.Bids[i]
            except KeyError:
                
                l=np.random.uniform(0,r)
                u=np.random.uniform(l,2*r)
                self.Bids[i]=(l,u)
                
    def Evaluate(self, Book):
        if self.OpenPos==True:
            self.OpenPos= not (Book.Time>=self.TimeClos)  # if it is already passed the time you closed your position. indicates if pos is T/F
        if CheckConditions(self,Book) and self.OpenPos==False:
            # open position
            self.OpenPos=True
            pos=AskPosition(self.pos_depth,Book)
            profit,self.TimeClose=Fitness(self,pos,Book)
            self.Profits.append(profit)

             
                
def AggregateBook(Prices,Qty,TickSize):
    P={}      
    for i in range(len(Prices)):
        
        try:
            P[Prices[i]]+=Qty[i]
        except KeyError:
            P[Prices[i]]=float(Qty[i])            
    try:
        Ticks=np.arange(Prices[0],Prices[-1],TickSize)
    except IndexError:
        Ticks=[TickSize]
    
    for k in Ticks:
        try:
            check=P[k]            
        except KeyError:
            P[k]=0
    return P
        
def CheckConditions (chrom, Book):
    Ask=Book.Ask
    Bid=Book.Bid
    total_qty=sum([Ask[i] for i in Ask])+sum([Bid[i] for i in Bid])        
    
    cond=True  # Start by assuming that conditions are satisfied
    Ticks=Book.Ask_Ticks
    if total_qty==0:
        return False
    if len(chrom.Asks.keys())>Ticks:
        # there are more conditions than orders on ticks in the order book. Therefore the conditions is not satisfied
        return False
    for i in chrom.Asks:
        try:
            cond=cond* (chrom.Asks[i][0] < Ask[Ticks[i]]/float(total_qty) < chrom.Asks[i][1])
        except IndexError:
            pass
        if not cond:
            return False
    Ticks=Book.Bid_Ticks
    if len(chrom.Bids.keys())>Ticks:
        return False
    for i in chrom.Bids:
        try:
            cond=cond* (chrom.Bids[i][0] < Bid[Ticks[i]]/float(total_qty) < chrom.Bids[i][1])
        except IndexError:
            pass
 
        if not cond:
            return False
        
    return cond  #if it gets to here cond should be True

def Fitness(Chrom,New_Pos,Book):
    Book=copy.deepcopy(Book)
    assert Book.line==New_Pos.Book.line
    newTime=New_Pos.TimeOpen
    
    time_exp=Chrom.time_exp
    takeProfit=Chrom.takeProfit
    stopLoss=Chrom.stopLoss
    pos_depth=Chrom.pos_depth

    endTime=newTime+time_exp
    
    OpenPr=New_Pos.OpenPr; PosPr=New_Pos.PosPr
    posValue=(Book.Bid_Ticks[-1]-OpenPr)/OpenPr
    
    K=New_Pos.Stocks2Fill.keys(); K.sort()
    stocks2fill=sum([New_Pos.Stocks2Fill[k] for k in K])
    alone_at_tick=New_Pos.Stocks2Fill[max(K)]==0
    filled=(stocks2fill==0)
    
    while (newTime < endTime) and (not filled) and (takeProfit > posValue > stopLoss):
        Book.Next()
        l=Book.line
        
        chng=Book.Changes[l]
        newTime=Book.Time
        if newTime>endTime:
            TimeClose=endTime
            break
        try:
            New_Pos.Stocks2Fill[chng[0]]+=chng[1]
            if New_Pos.Stocks2Fill[max(K)]==0:
                alone_at_tick=True
        except KeyError:
            
            if chng[0]<min(K):
                New_Pos.Stocks2Fill[chng[0]]=chng[1]
            elif chng[0]>max(K):
                pass
            else:
                # shouldn't get to here
                raise NameError
        all_keys=New_Pos.Stocks2Fill.keys(); all_keys.sort()    
        stocks2fill=sum([New_Pos.Stocks2Fill[k] for k in all_keys[:-1]])
        filled=(stocks2fill==0)*alone_at_tick
        posValue=(Book.Bid_Ticks[-1]-OpenPr)/OpenPr
        TimeClose=newTime
    print newTime,endTime,"||", (not filled),"||",(takeProfit,posValue,stopLoss)
    
    return posValue, TimeClose
    
class Population():
    def __init__ (self,N):
        self.all_chroms=[]
        self.CreateChroms(N)
    def CreateChroms(self,N):
        for i in range(N):
            n_bids=np.random.poisson(10); n_asks=np.random.poisson(10)
            pos_depth=5  #number of ticks where to place the ask order
            takeProfit=0.5  # Sell if takeProfit or stopLoss are crossed
            stopLoss=-0.5
            time_exp=timedelta(hours=3)
            self.all_chroms.append(Chromosomes(n_bids,n_asks,pos_depth,stopLoss,takeProfit,time_exp))

    def Run(self,Book,EndTime):
        EndTime=min(EndTime,Book.Time_last_obs)
        while Book.Time<EndTime:
            Book.Next()
            for c in self.all_chroms:
                c.Evaluate(Book)
        print sum([sum(i.Profits) for i in self.all_chroms])
        print Book.Time

Pop=Population(100)
Bk=OrderBook(AskPrices,AskQty,BidPrices,BidQty,Changes,tick_size)
EndTime=datetime(2011,1,1)
Pop.Run(Bk,EndTime)
