from datetime import datetime, timedelta
import copy
import numpy as np


class OrderBook():
    def __init__(self, Ask_Prices,Ask_Qty, Bid_Prices, Bid_Qty, Changes,tick_size):
        self.tick_size
        self.Ask=AggregateBook(self.Ask_Prices,self.Ask_Qty,self.tick_size)
        self.Bid=AggregateBook(self.Bid_Prices,self.Bid_Qty,self.tick_size)
        # self.Ask and self.Bid are dictionaries with prices as the keys and number of stocks as the values
        # self.Ask[25.5] gives you the number of stocks currently at the book at 25.5 price.
        self.Bid_Ticks=self.Bid.keys(); self.Bid_Ticks.sort()
        self.Ask_Ticks=self.Ask.keys(); self.Ask_Ticks.sort()

        self.Best_BidPr=max(self.Bid_Ticks)
        self.Best_AskPr=min(self.Ask_Ticks)
        # if there are Market Orders on the book they are recorded at zero price so disregard them -->
        if self.Best_AskPr==0:
            self.Best_AskPr=self.Ask_Ticks[1]  # take the second key in the list        
        # keep record of the current time -->
        self.Changes=Changes        
        Time=self.Changes[-1]
        Time=Time.split()
        Time1=Time[0]; Time2=Time[1]
        Time1=Time1.split("-"); Time2=Time2.split(":")
        self.Time=datetime(int(Time1[0]),int(Time1[1]),int(Time1[2]),int(Time2[0]),int(Time2[1]),int(Time2[2]))
        
    def GetPriceAtTick(self,n,side):
        # gets the price at the n-th tick from the best bid/ask
        if side=="Ask":
            return self.Best_AskPr + n*self.tick_size
        else:
            assert side=="Bid"
            return self.Best_BidPr - n*self.tick_size
        
class Position():
    # creates a virtual position if conditions are met and starts recording characteristics of the book
    def __init__(self,Book,Hold):
        self.Book=Book
        self.Hold=Hold
        self.TimeOpen=self.Book.Time
        self.TimeClose=self.TimeOpen+Hold
        self.Results={}
        self.Results['Ask']= []
        self.Results['Bid']=[]
        
    def Update (self, Book):
        if Book.Time >= self.TimeClose:
            return None
        else:
            self.Results['Ask'].append(self.Book.Best_AskPr)
            self.Results['Bid'].append(self.Book.Best_BidPr)
            
class BookCondition():  # creates a condition for number of stocks between two ticks.
    # Example  the stocks offered between ticks 3 and 5 is between 100 and 150
    def __init__(self,tick_bounds,value_bounds,side): 
        self.side=side  #  bid or ask condition
        self.tick_bounds= tick_bounds  # the tick-bounds of the condition
        self.value_bounds=value_bounds # the number of stocks offered between the ticks
            
    def Check (self, Book):
        if self.side=="Ask":
            Side=Book.Ask
            lb=Book.GetPriceAtTick(self.tick_bounds[0],"Ask")
            ub=Book.GetPriceAtTick(self.tick_bounds[1],"Ask")
        else:
            Side=Book.Bid
            lb=Book.GetPriceAtTick(self.tick_bounds[0],"Bid")
            ub=Book.GetPriceAtTick(self.tick_bounds[1],"Bid")          
            assert self.side=="Bid"
        Q=0     
        for Pr in Side:
            if lb<=Pr<ub:  # Aggregate the quantities between the two bounds in the condition
                Q+=Side[Pr]

        return (self.value_bounds[0]<= Q < self.value_bounds[1])
    
class StrategyCondition():
    def __init__ (self, Hold):
        self.Hold=Hold
    def Check(self,Book):
        return True
        
class Chromosome():
    def __init__(self):
        self.Positions=[]
        self.Genes=[]
        
    def CreateGenes(self,mu_value):  # the conditions
        step=2
        N=np.random.randint(2,20)
        for i in range(0,N,step):
            tick_bounds=(i,i+step)
            value_bounds=np.random.normal(mu_value,0.1*mu_value,2)
            value_bounds.sort()
            self.Genes.append(BookCondition(tick_bounds,value_bounds,side="Ask"))
        Hold=timedelta(hours=3)
        self.Genes.append(StrategyCondition(Hold))    

    def CheckConditions(self,Book):
        for gene in self.Genes:
            if not gene.Check(Book):
                return False  # if even one condition isn't satisfied exits and returns False
        return True

    def OpenPosition(self,Book):
        if self.CheckConditions(Book):
            self.Positions.append(Position(Book,self.Hold)) # append an instance of Position()
        
    def UpdatePositions (self, Book):  # update the positions
        for pos in self.Positions:
            pos.Update(Book)
            
    def Fitness(self): # calculates the fitness of the chromosome. calculate at the end of the run
        Asks=[pos.Results['Ask'] for pos in self.Positions]
        Bids=[pos.Results['Bid'] for pos in self.Positions]
        return fit

class Population():
    def __init__(self):
        self.Pop=[]
    def CreateChromosomes(self, Chrom,N):
        for i in range(N):
            self.Pop.append(Chrom())
    def Run(self,endTime):  # Simulates one generation of results and stops at endTime
        while Book.Time<=endTime:
            for chrom in self.Pop:
                chrom.OpenPosition(Book)  # see if conditions are met and open a position if so
                chrom.UpdatePositions(Book)  # update all positions
        self.Pop.sort(key=lambda x :x.Fitness(), reverse=True)  # sort chromosomes. high fitness first
    def ProduceNewGeneration(self):
        pass
def Simulate(MyPop,N):
    for i in range(N):
        MyPop.Run(endTime)
        MyPop.ProduceNewGeneration()
            
        
        

    

