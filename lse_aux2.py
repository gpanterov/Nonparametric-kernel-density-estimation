# Auxiliary file for the LSE order book program
# George Panterov

# Contains helpful routines for the building of the order book

# This is version 2
# This version has the possibility of getting the order book over several days
import csv
from datetime import datetime
import time
import copy
import os
import numpy as np
from copy import deepcopy
DAYS=[2,3,4,7,8,9,10,11,14,15,16,17,18,21,22,23,24,25,28,29,30,31]

ConvertCode={}
ConvertLong={}
f1=open("TickSizes.csv","r")

for line in f1:
    line=line.split(",")
    ConvertCode[line[5][1:-1].strip()]=line[0][1:-1].strip()
    ConvertLong[line[0][1:-1].strip()]=line[5][1:-1].strip()

def filepath(day, ind):
    
    """
Returns the pathname for the data file specified by ind (OrderDetail, OrderHistory or TradeReport)
on *day*. day must be an integer between 1 and 31
"""
    if ind!="TradeReport" and ind!="OrderDetail" and ind!="OrderHistory":
        raise NameError(' ind must be either TradeReport or OrderDetail')
    
    elif day<1 or day>31 or type(day)!=int:
        raise TypeError('day must be an integer between 1 and 31')
    
    if day<10:
        day="0"+str(day)
    else:
        day=str(day)
        
    path="/data/LSE_DATA/raw/T_" + ind + "_"+ day +"012008.csv/" + "t_" + ind +".csv"

    return path        

def GetInstrumentsSummary(dic,start,end):
    instruments=dic
    for day in DAYS[start:end]:
        t0=time.clock()
        print "Loading data from day ", day
        details_filepath=filepath(day, "OrderDetail")
        report_filepath=filepath(day, "TradeReport")
        
        report_file=open(report_filepath)
        details_file=open(details_filepath)
        # Load all orders
        for line in details_file:  # each line is a different order
            line=line.split(",")
            
            try:
                instr=instruments[line[3]]
                instr['numOrders']+=1
                instr['numSharesOffered']+=int(line[-6])
                
                
            except KeyError:  # Security encountered for the first time
                instruments[line[3]]={}
                instr=instruments[line[3]]
                instr['numOrders']=1
                instr['numSharesOffered']=int(line[-6])
                instr['Volume']=0
                instr['numTrades']=0
                instr['numSharesTraded']=0
                instr['CancelledTrades']=0
                
        print "         Loaded and classified the Order Details"

        # Load all trades
        for line in report_file:
            line=line.split(",")
            try:
                instr=instruments[line[1]]
                instr['numTrades']+=1
                instr['numSharesTraded']+=int(line[7])
                instr['Volume']+= (int(line[7])* float(line[6]))  # Volume traded
                if line[-7]=="D":
                    instr['CancelledTrades']+=1
                
            except KeyError:
                # Not in book
                instruments[line[1]]={}  # Create it
                instr=instruments[line[1]]
                instr['numOrders']=1
                instr['numSharesOffered']=0
                instr['Volume']=int(line[7])*float(line[6])
                instr['numTrades']=1
                instr['numSharesTraded']=int(line[7])
                instr['CancelledTrades']=0
                if line[-7]=="D":
                    instr['CancelledTrades']=1

                
        print "         Loaded and classified the Trade Details"
        print time.clock()-t0
        details_file.close(); report_file.close()
    return instruments        
                

            
class LimitOrder():
    def __init__ (self,raw_order):
        """
        returns an object from the LimitOrder class. Takes as input the *string* from the data files raw_order.
        raw_order must be a line in one of the OrderDetails files.
        """
        self.raw=raw_order
        
        raw_order=raw_order.split(",")  # Turn into a list of strings
        
        self.Code=raw_order[0]  # The order code
        self.TIcode=raw_order[3]  # The code of the instrument
        self.Type=raw_order[7]  # A buy or a sell order
        self.Price=float(raw_order[10]) 
        self.Size=int(raw_order[11])  # doesn't allow for half of stock
        self.BroadcastUpdateAction=raw_order[13]
        try:
            self.Time = datetime(int(raw_order[-3][4::]),int(raw_order[-3][2:4]),int(raw_order[-3][0:2]),
                             int(raw_order[-2][0:2]), int(raw_order[-2][3:5]), int(raw_order[-2][6:8]), int(raw_order[-2][9::]))
        except:
            
            self.Time = datetime(int(raw_order[-3][4::]),int(raw_order[-3][2:4]),int(raw_order[-3][0:2]),
                             int(raw_order[-2][0:2]), int(raw_order[-2][3:5]), int(raw_order[-2][6:8]))
             
            
        self.MessageSequenceNumber=int(raw_order[-1])  # A number that takes care of orders placed at the same time

        self.ind="LimitOrder"
        self.ParticipantCode=raw_order[6]
        self.BestBid=0; self.BestAsk=np.inf
        self.N_Prec=0;self.Vol_Prec=0
        self.OriginalSize=int(raw_order[11])
class Deletion():
    def __init__ (self, raw_del):
        """
        returns a deletion object. raw_del must be a line from a OrderHistory file
        """
        self.raw=raw_del
        raw_del=raw_del.split(",")

        self.Code=raw_del[0]
        self.ActionType=raw_del[1]
        self.MatchingCode=raw_del[2]  # The code of the other order participating in the deletion      
        self.TradeSize=raw_del[3] # The quantity that is bought or sold
        self.TradeCode=raw_del[4] # This should be the code of the trade. It should match the trade report file
        self.TIcode=raw_del[5]
        self.RemainingSize=int(raw_del[-6])
        self.Buy_Sell=raw_del[-4]
        self.MessageSequenceNumber=int(raw_del[-3])
        try:
            self.Time = datetime(int(raw_del[-2][4::]),int(raw_del[-2][2:4]),int(raw_del[-2][0:2]),
                             int(raw_del[-1][0:2]), int(raw_del[-1][3:5]), int(raw_del[-1][6:8]), int(raw_del[-1][9::]))
        except:
            self.Time = datetime(int(raw_del[-2][4::]),int(raw_del[-2][2:4]),int(raw_del[-2][0:2]),
                             int(raw_del[-1][0:2]), int(raw_del[-1][3:5]), int(raw_del[-1][6:8]))
        self.Type=raw_del[10]  # This indicates whether it is a buy/sell change    
        self.ind="Deletion"

class Report():
    def __init__ (self, raw_report):
        """
        returns a report object. raw_report must be a line from an TradeReport file
        """
        self.raw=raw_report
        raw_report=raw_report.split(",")
        self.TIcode=raw_report[1]
        self.MessageSequenceNumber=int(raw_report[0])
        self.TradeCode=raw_report[5]
        self.TradePrice=float(raw_report[6])
        
        self.TradeSize=int(raw_report[7])
        self.TradeType=raw_report[11]
        # Note in the description file the trade date is listed as having the format
        # YYYYMMDD. This is incorrect. It has the normal format DDMMYYYY
        self.Time = datetime(int(raw_report[8][4::]),int(raw_report[8][2:4]),int(raw_report[8][0:2]),
                             int(raw_report[9][0:2]), int(raw_report[9][3:5]), int(raw_report[9][6:8]))
        self.ind="Report"

class OrderBook2():
       
    def __init__(self,start_day,asset):
        self.start_day=start_day
        self.asset=asset
        self.ob={}
        self.old_ob={}
        self.new_orders=[]
        self.deletions=[]
        self.LoadDay(start_day)
        self.TimeStamp=datetime(2008,1,start_day,6,0,0,0)
        self.Log=[]
    def LoadDay(self,day):
        print "------------Loads orders from day ",day,"--------"
        self.current_day=day
        details_filepath=filepath(day, "OrderDetail")
        deletions_filepath=filepath(day, "OrderHistory")
        

        
        details_file=open(details_filepath)
        deletions_file=open(deletions_filepath)
        

        for line in details_file:  # each line is a different order
            order=line.split(",")
            TIcode=order[3]   # The trading instrument for this order
            BroadcastUpdateAction=order[-4]  #
            if TIcode==self.asset and BroadcastUpdateAction=="F":  # This creates the starting order book at the beg. of the day
                try:
                    old_bookorder=self.ob[order[0]]   # Check if the order is not already on the book
                    # if the order exist don't do anything
                except:
                    # if the order doesn't exist add it .. This shouldn't happen generally
                    self.ob[order[0]]=LimitOrder(line)
                    #self.all_orders_dict[order[0]]=line
                
            elif TIcode==self.asset and BroadcastUpdateAction=="A":  # This indicates a new order
                self.new_orders.append(LimitOrder(line))
                

        for line in deletions_file:
            deletion=line.split(",")
            TIcode=deletion[5]
            if TIcode==self.asset:
                self.deletions.append(Deletion(line))
        self.new_orders.sort(key=lambda x: x.Time)  # sort the orders with the most recent ones coming first        
        self.deletions.sort(key=lambda x: x.Time)

        self.Actions=self.new_orders+self.deletions # Combine all the orders and changes to the orders together and sort them:
        self.Actions.sort(key=lambda x: (x.Time, x.MessageSequenceNumber))

        details_file.close()
        deletions_file.close()
        
    def NextAction(self):
        self.old_ob=deepcopy(self.ob)
        if len(self.Actions)==0:  # If there are no more orders or deletions then load the data from the next day
            # empty the orders and deletions from previous day
            if self.current_day==31:
                return True

            self.new_orders=[]
            self.deletions=[]
            day_ind=DAYS.index(self.current_day)  # The index of the current day in the DAYS list
            next_day=DAYS[day_ind+1]  # Take the next day
            self.LoadDay(next_day)  # And load the data into memory
            
        new=self.Actions.pop(0)  # this is either a new order or a change in an existing order or a market order
        
        if new.ind=="Deletion" : # if the next action is some type of a modification (deletion, expiry, trade etc..)
            
            if new.ActionType=="D":  # delete the order
                
                try:
                    _=self.ob.pop(new.Code)
                # _ is a member of the class LimitOrder(). Record the price and the size of the order
                    self.LastAction=[new.Type,"D",_.Price,_.Size,new.Time,new.Code]
                except:
                    print "Deleting order that is not in the order Book"
                    self.LastAction=[new.Type,"D",None,new.TradeSize,new.Time,new.Code]
                
                
            elif new.ActionType=="M":  # Order fully completed
                try:
                    _=self.ob.pop(new.Code)  # remove order from book
                    self.LastAction=[new.Type,"MO",_.Price, _.Size,new.Time,new.Code]
                except:
                    print "Order missing from Book"
                    self.LastAction=[new.Type,"MO",None, new.TradeSize,new.Time,new.Code]
                #print "Trade occured (full match). ", _.Size, " units traded at ", _.Price, " per share.              
			                    
                      
            elif new.ActionType=="E":  # order expired
                try:
                    _=self.ob.pop(new.Code) # remove from book
                    self.LastAction=[new.Type,"E",_.Price,_.Size,new.Time,new.Code]
                except KeyError:
                    self.LastAction=[new.Type,"E",None,new.TradeSize,new.Time,new.Code]
                    print "Order not in Book but it expires (Maybe from previous day!!!!!!!"			
		    print new.Code,new.MatchingCode, new.Time 
                
            elif new.ActionType=="P":  # Order partially matched
                order=self.ob[new.Code]
                if (order.Size != new.RemainingSize+int(new.TradeSize)):
                    print "!!! Order's sizes don't add up. Original Size is:",order.Size, ". Remaining size is: ",new.RemainingSize, ". Trade size is: ", new.TradeSize
                order.Size=copy.deepcopy(new.RemainingSize)  # change the size to the new value
               
                #print "Trade occured (partial match). ", new.TradeSize, " units traded at ", order.Price, " per share."
                self.LastAction=[new.Type,"MO",order.Price,new.TradeSize,new.Time,new.Code]
                
                # The corresponding order new.MatchingCode shouldn't be on the books unless it is UT order    
                
            elif new.ActionType=="Z": # Order's size decreased
                order=self.ob[new.Code]  # Take order from order book (remains on the book)
                decrease=copy.deepcopy(order.Size-new.RemainingSize)  #just to be safe use deepcopy because later we change order.Size
                self.LastAction=[new.Type,"Z",order.Price,decrease,new.Time,new.Code]
                
                order.Size=new.RemainingSize # change order size


            elif new.ActionType == "T":
                self.LastAction=[new.Type,"T",0,0,new.Time,new.Code]
            else:
                print new.ActionType, " Action Type not recognized."
                raise NameError(" Order Action Type must be one of D,E,P,M,Z or T")
                
        elif new.ind=="LimitOrder":
            #print "Added an order to the book"
            BestBid,BestAsk=self.GetBestBidAsk()
            self.ob[new.Code]=new  # add the order to the orderbook
            if new.Type=="B" and new.Price>BestAsk:
                new.Price=BestAsk-0.1
            elif new.Type=="S" and new.Price<BestBid:
                new.Price=BestBid+0.1
            self.ob[new.Code].BestBid=BestBid; self.ob[new.Code].BestAsk=BestAsk
            N_Prec,Vol_Prec=self.GetPrecededOrders(new.Type,new.Price)
            self.ob[new.Code].N_Prec=N_Prec;self.ob[new.Code].Vol_Prec=Vol_Prec
            self.LastAction=[new.Type,"LO",new.Price,new.Size,new.Time,new.Code]
            
        self.TimeStamp=new.Time
        dif=new.Time-datetime(2008,1,1,9,0,0)
        dif_seconds=dif.seconds
        if dif_seconds%1800==0:
            print "The Time is: ", new.Time.hour,":",new.Time.minute
    def Run (self,end_day,hr,mi,sec,msec,year=2008,month=1):
         
        
        stop=datetime(year,month,end_day,hr,mi,sec,msec)
        try:
            FolderName=ConvertLong[self.asset]
        except KeyError:
            FolderName=self.asset
        try:
            os.makedirs("/home/panterov/"+FolderName)
        except OSError:
            pass
        f3=csv.writer(open("/home/panterov/"+FolderName+"/_Changes.csv","w"))
        f4=csv.writer(open("/home/panterov/"+FolderName+"/_All.csv","w"))
        Dummy=False
        while (self.TimeStamp <= stop) and (not Dummy):
            Dummy=self.NextAction()
            B,A=self.GetBidAsk()
            Comp_Order=[(i.Price,i.Size,i.N_Prec,i.Vol_Prec,i.Time.day,i.Time.hour,i.Time.minute,i.Time.second,\
                         i.Time.microsecond,i.BestBid,i.BestAsk,i.OriginalSize,i.Code) for i in B] + \
                        [(i.Price,-i.Size,i.N_Prec,i.Vol_Prec,i.Time.day,i.Time.hour,i.Time.minute,i.Time.second,\
                          i.Time.microsecond,i.BestBid,i.BestAsk,i.OriginalSize,i.Code) for i in A]
            f3.writerow(self.LastAction)
            f4.writerow(Comp_Order)
        print "The Last Entry was:", self.LastAction
            
    def GetBestBidAsk(self):
        B,A=self.GetBidAsk()
        BestBid=0; BestAsk=np.Inf
        if len(B)<1 or len(A)<1:
            return BestBid,BestAsk
        if B[-1].Price<A[0].Price:
            BestBid=copy.deepcopy(B[-1].Price)
            BestAsk=copy.deepcopy(A[0].Price)
        else: # This happens at the auction early in the day
            BestBid=copy.deepcopy(B[-1].Price)
            for ask in A:
                if ask.Price>BestBid:
                    BestAsk=copy.deepcopy(ask.Price)
                    return BestBid, BestAsk
        return BestBid,BestAsk
    
            
    def GetBidAsk(self):
        BidOrders=[]; AskOrders=[]
        for i in self.old_ob:
            if self.old_ob[i].Type=="B":
                BidOrders.append(self.old_ob[i])
            else:
                AskOrders.append(self.old_ob[i])
                assert self.old_ob[i].Type=="S"
        BidOrders.sort(key=lambda x: (x.Price,x.Time,x.MessageSequenceNumber))#, reverse=True)
        AskOrders.sort(key=lambda x: (x.Price,x.Time,x.MessageSequenceNumber))
        return BidOrders,AskOrders
    def GetPrecededOrders(self,Type,price):
        # returns the number of orders and the total volume of shares of orders that need to be executed before some order
        n_prec=0; vol_prec=0
        B,A=self.GetBidAsk()
        if Type=="B": # a buy order
            passed=False;
            for book_order in B:
                if book_order.Price>=price:
                    passed=True
                if passed==True:
                    n_prec+=1; vol_prec+=book_order.Size
                    
        if Type=="S":
            passed=False
            for book_order in A:
                if book_order.Price>price:passed=True
                if passed==False:
                    n_prec+=1; vol_prec+=book_order.Size
        return n_prec, vol_prec
    

    def DisplayBook(self):
        BidOrders,AskOrders=self.GetBidAsk()
        print "Order Code, Price, Size, Type(Buy/Sell), ParticipantCode(Trader ID)"
        print "-----------------------------"

        for i in BidOrders:
            print i.Code, i.Price, i.Size, i.Type, i.ParticipantCode
        print "-----------------------------"
        print "-----------------------------"
        print "-----------------------------"
        
        print "Order Code, Price, Size, Type(Buy/Sell), ParticipantCode(Trader ID)"
        print "-----------------------------"
        
        for i in AskOrders:
            print i.Code, i.Price, i.Size, i. Type, i.ParticipantCode

        self.BidOrders=BidOrders; self. AskOrders=AskOrders



