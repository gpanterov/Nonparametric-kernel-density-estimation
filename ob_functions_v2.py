# This module contains some order book functions
import csv
import numpy as np
from datetime import datetime, timedelta


# First we need to clearly identify the order flow

def GetMOFile(f_all,f_ch,start,end,Folder,interval=1000):
    if start>=end:
        return True
    counter=0
    #f_all and f_ch are csv objects (iterators)
    FileName=Folder+"MO_"+str(start)+".csv"
    f=csv.writer(open(FileName,"w"))
    VarNames=["type","size"]+["spread","order_imb","shares_imb","shares_tot","order_tot","num_bids","num_asks","time"]
    f.writerow(VarNames)
    while counter<interval:
        try:
            chng=f_ch.next();
            ob=f_all.next();
        except:
            return True
        Time=GetOrderTime(chng)
        if chng[1]=="MO" and Time.hour>=9 and Time.hour<16:
            counter+=1
            OB=GetBook(ob);
            OrderVars=GetOrderVars(chng,OB); OBVars=GetOBVars(OB)
            row=[OrderVars[1],OrderVars[3]]+OBVars+[str(Time)]
            f.writerow(row)
    print str(OrderVars[0])
    GetMOFile(f_all,f_ch,start+1,end,Folder,interval=interval)

def GetLOFile(f_all,f_ch,start,end,Folder,interval=1000):
    if start>=end:
        return True
    counter=0
    #f_all and f_ch are csv objects (iterators)
    FileName=Folder+"LO_"+str(start)+".csv"
    f=csv.writer(open(FileName,"w"))
    VarNames=["type","distance","size"]+["spread","order_imb","shares_imb","shares_tot","order_tot","num_bids","num_asks","time"]
    f.writerow(VarNames)
    while counter<interval:
        try:
            chng=f_ch.next();
            ob=f_all.next();
        except:
            return True
        Time=GetOrderTime(chng)
        if chng[1]=="LO"and Time.hour>=9 and Time.hour<16:
            counter+=1
            OB=GetBook(ob);
            OrderVars=GetOrderVars(chng,OB); OBVars=GetOBVars(OB)
            row=[OrderVars[1],OrderVars[2],OrderVars[3]]+OBVars+[str(Time)]
            f.writerow(row)
    print str(OrderVars[0])
    GetLOFile(f_all,f_ch,start+1,end,Folder,interval=interval)

def GetTypeFile(f_all,f_ch,start,end,Folder,interval=1000):
    if start>=end:
        return True
    counter=0
    #f_all and f_ch are csv objects (iterators)
    FileName=Folder+"Type_"+str(start)+".csv"
    f=csv.writer(open(FileName,"w"))
    VarNames=["type"]+["spread","order_imb","shares_imb","shares_tot","order_tot","num_bids","num_asks","time"]
    f.writerow(VarNames)
    while counter<interval:
        try:
            chng=f_ch.next();
            ob=f_all.next();
        except:
            return True
        Time=GetOrderTime(chng)
        if (chng[1]=="LO" or chng[1]=="MO")and Time.hour>=9 and Time.hour<16:
            counter+=1
            OB=GetBook(ob);
            OBVars=GetOBVars(OB)
            row=[chng[1]]+OBVars+[str(Time)]
            f.writerow(row)
    print chng[-2]
    GetTypeFile(f_all,f_ch,start+1,end,Folder,interval=interval)
    
def GetDelFile(f_all,f_ch,start,end,Folder,NumOrders=800):
    counter=0
    if start>=end:
        return True
    
    #f_all and f_ch are csv objects (iterators)
    FileName=Folder+"Del_"+str(start)+".csv"
    f=csv.writer(open(FileName,"w"))
    VarNames=["Deleted","RelPos","SizeChange","N_Prec_Change","Vol_Prec_Change","elapsed_seconds"]+\
              ["spread","order_imb","shares_imb","shares_tot","order_tot","num_bids","num_asks"]
    f.writerow(VarNames)
    while counter<=NumOrders:
        try:
            chng=f_ch.next();
            ob=f_all.next();
        except:
            return True
        OB=GetBook(ob);OBVars=GetOBVars(OB);
        Time=GetOrderTime(chng)
        if Time.hour>9 and Time.hour<16:
            n=RecordDelVars(chng,OB,OBVars,f)
            counter+=n
    print"Finished file number", start
    GetDelFile(f_all,f_ch,start+1,end,Folder,NumOrders)
    
        
    
def RecordDelVars(Changes,OB,OBVars,Del_File):
    new_type=Changes[1]
    new_code=Changes[-1]
    new_time=GetOrderTime(Changes)
    cur_bid,cur_ask=GetBestBidAsk(OB)
    assert cur_bid<cur_ask
    assert cur_bid>0
    assert cur_ask>0
    counter=0
    for order_on_book in OB:
        Del=0 # Indicates 0 if the order is not deleted at this time and 1 if it is
        order_code=order_on_book[-1];
        order_ask=order_on_book[6]; order_bid=order_on_book[5];  # the best bid and asks at the time of the order
        order_price=order_on_book[0]; order_size=order_on_book[1]
        n_prec_old=order_on_book[2]; vol_prec_old=order_on_book[3]
        original_size=order_on_book[-2]

        if order_ask!=np.Inf and order_bid>0:  # take only orders that you have full info for
            counter+=1
        
            if order_size<0:
                order_type="S"
            else:
                order_type="B"
            elapsed_time=new_time-order_on_book[4]  #the elapsed time since placing the order
            elapsed_sec=elapsed_time.seconds + elapsed_time.days*86400
            
            Size_Change=float(order_size)/original_size

            n_prec_now,vol_prec_now=GetPrecededOrders(OB,order_type,order_price)
            N_Prec_Change=float(n_prec_old)-n_prec_now; Vol_Prec_Change=float(vol_prec_old)-vol_prec_now
            
            # produce the relative position change of the orders on the book. See Farmer page 16
            
            if order_size<0: # if a sell order is being cancelled
                delta_0=np.log(order_price)-np.log(order_bid)
                delta_t=np.log(order_price)-np.log(cur_bid)
            elif order_size>0: # a buy order
                delta_0=np.log(order_ask)-np.log(order_price)
                delta_t=np.log(cur_ask)-np.log(order_price)

            if delta_0<=0: 
                print "Error delta 0"
                print "order_size, order_price, order_bid, order_ask, cur_bid, cur_ask"
                print order_size, order_price, order_bid, order_ask, cur_bid, cur_ask
            if delta_t<=0:
                print "Error delta t"
            #assert delta_0>=0; assert delta_t>=0;
            rel_pos=float(delta_t)/delta_0 # the relative position of the order.
            if new_type=="D" and new_code==order_code:
                Del=1# This order is deleted:
                
            order_details=[Del,rel_pos,Size_Change,N_Prec_Change,Vol_Prec_Change,elapsed_sec]+OBVars
            
            Del_File.writerow(order_details)
    return counter
def GetDelVars(order,OB):
    order_on_book=order;
    cur_bid,cur_ask=GetBestBidAsk(OB)
    order_code=order_on_book[-1];
    
    order_ask=order_on_book[6]; order_bid=order_on_book[5];  # the best bid and asks at the time of the order
    order_price=order_on_book[0]; order_size=order_on_book[1]
    n_prec_old=order_on_book[2]; vol_prec_old=order_on_book[3]
    original_size=order_on_book[-2]
    if order_size<0:
        order_type="S"
    else:
        order_type="B"

    #elapsed_time=new_time-order_on_book[4]  #the elapsed time since placing the order
    Size_Change=float(order_size)/original_size

    n_prec_now,vol_prec_now=GetPrecededOrders(OB,order_type,order_price)
    N_Prec_Change=float(n_prec_old)-n_prec_now; Vol_Prec_Change=float(vol_prec_old)-vol_prec_now;

    if order_size<0: # if a sell order is being cancelled
        delta_0=np.log(order_price)-np.log(order_bid)
        delta_t=np.log(order_price)-np.log(cur_bid)
    elif order_size>0: # a buy order
        delta_0=np.log(order_ask)-np.log(order_price)
        delta_t=np.log(cur_ask)-np.log(order_price)
    rel_pos=float(delta_t)/delta_0
    return [rel_pos,Size_Change,N_Prec_Change,Vol_Prec_Change]

def GetPrecededOrders(OB,Type,Price):
    # returns the number of orders and the total volume of shares of orders that need to be executed before some order
    n_prec=0; vol_prec=0
    if Type=="B": # a buy order
        passed=False; bid_side=True
        for book_order in OB:
            if book_order[1]<0:bid_side=False
            if book_order[0]>=Price: passed=True
            if passed==True and bid_side==True:
                n_prec+=1; vol_prec+=book_order[1]
    if Type=="S":
        passed=False
        ask_side=False
        for book_order in OB:
            if book_order[0]<=Price:passed=False
            if book_order[1]<0: ask_side=True # indicates where we passed on the ask side
            if passed==False and ask_side==True:
                n_prec+=1; vol_prec+=abs(book_order[1])
    return n_prec, vol_prec
                
        
def GetOrderTime(Changes):
    # returns a datetime object with the order time. Changes is (raw) line from the Changes file
    line=Changes
    date_time=line[4]
    date=date_time.split()[0]; time=date_time.split()[1]
    year=int(date.split("-")[0]); month=int(date.split("-")[1]); day=int(date.split("-")[2])
    hour=int(time.split(":")[0]); minute=int(time.split(":")[1]); second=int(time.split(":")[2]) 
    order_time=datetime(year,month,day,hour,minute,second)        
    return order_time

def GetOrderVars(Changes,OB):
    line=Changes
    order_time=GetOrderTime(Changes)
    
    # returns the list of order specific variables
    BestBid,BestAsk=GetBestBidAsk(OB)
    if line[0]=="B" and line[1]=="MO":
        Type="MS"  # Market Sell
    # Note because the first element in change is the order type
    # of the order that is being modified we have to flip them.
    # i.e. sell indicates that the new order is a buy and vice versa

        Distance=None # Market orders don't have distance
        Size=float(line[3])
         
    elif line[0]=="B" and line[1]=="LO":
        Type="LB"  # Limit Buy
        Distance= np.log(BestAsk)-np.log(float(line[2]))
        Size=float(line[3])
    elif line[0]=="S" and line[1]=="MO":
        Type="MB"
        Distance=None
        Size=float(line[3])

    elif line[0]=="S" and line[1]=="LO":
        Type="LS"
        Distance=np.log(float(line[2]))-np.log(BestBid)
        Size=float(line[3])
    elif line[0]=="B" and (line[1]=="D" or line[1]=="E"):
        Type="DB" # deletion on the sell side
        Distance=None
        Size=float(line[3])
    elif line[0]=="S" and (line[1]=="D" or line[1]=="E"):
        Type="DS"
        Distance=None
        Size=float(line[3])
    else:
        Type=None; Distance=None; Size=None
    if Distance!=None and Distance<0:
        print "Negative Distance!!!", Distance
    return [order_time,Type,Distance,Size]

def GetOBVars(OB):
    # returns a list of variables associated with the Order Book and its shape
    BestBid,BestAsk=GetBestBidAsk(OB)
    n_bids=0; n_asks=0
    bid_shs=0; ask_shs=0;
    
    spread=np.log(BestAsk)-np.log(BestBid)
    for i in OB:
        Size=i[1]
        if Size>0:
            n_bids+=1
            bid_shs+=Size
        elif Size<0:
            n_asks+=1
            ask_shs+=Size
    
    n_imb=float(n_asks)/(n_bids+n_asks)    
    shs_imb=float(-ask_shs)/(bid_shs+(-ask_shs))
    
    shs_tot=(bid_shs+(-ask_shs))
    ord_tot=(n_bids+n_asks)    
    
    return [spread,n_imb,shs_imb,shs_tot,ord_tot,n_bids,n_asks]

       


def GetBook(Row,Year=2008,Month=1):
    # returns the order book from a Row of all_file
    OB=[]
    for i in Row:
        i=i[1:-1]  # get rid of the first and last parenthesis
        i=i.split(",")
        Price=float(i[0]);Size=float(i[1]);N_Prec=int(i[2]);Vol_Prec=int(i[3]);
        Day=int(i[4]);Hour=int(i[5]);Minute=int(i[6]);Second=int(i[7]);MicroSecond=int(i[8]);
        BestBid=float(i[9]); BestAsk=float(i[10]); OriginalSize=int(i[11]); Code=i[12].strip().strip("'")
        
        Time=datetime(Year,Month,Day,Hour,Minute,Second,MicroSecond)
        
        order=[Price,Size,N_Prec,Vol_Prec,Time,BestBid,BestAsk,OriginalSize,Code]
        OB.append(order)
        OB.sort(key=lambda x: (x[0],x[4]))
    return OB

def GetBestBidAsk(OB):
    OB.sort(key=lambda x: (x[0],x[4]))
    BestBid=0;BestAsk=np.Inf
    for i in OB:
        if i[1]>0 and i[0]>0:
            BestBid=i[0]
        if i[1]<0 and i[0]>0:
            BestAsk=i[0]
            return BestBid,BestAsk
    return BestBid,BestAsk

def CreateIntervalFiles(all_file,changes_file,start_time,end_time,Folder,SubFolder):
    # creates interval files between start time and end time from all_file and changes_file
    # located in Folder. The output files are in SubFolder
    f1=csv.reader(open(Folder+all_file,"r"))
    f2=csv.reader(open(Folder+changes_file,"r"))
    OB_VarNames=["spread","order_imb","shares_imb","shares_tot","order_tot","num_bids","num_asks"];
    Time_VarNames=["day","hour","minute","second"]
    
    Types_VarNames=["Type"]; Types_VarNames.extend(OB_VarNames);Types_VarNames.extend(Time_VarNames)
    MO_VarNames=["Type","Size"]; MO_VarNames.extend(OB_VarNames);MO_VarNames.extend(Time_VarNames)
    LO_VarNames=["Type","Distance","Size"];LO_VarNames.extend(OB_VarNames);LO_VarNames.extend(Time_VarNames)
    Del_VarNames=["Deleted","RelPos","SizeChange","N_Prec_Change","Vol_Prec_Change"]; Del_VarNames.extend(OB_VarNames);
    MO_file=csv.writer(open(SubFolder+"MO_"+str(start_time.day)+"-"+str(start_time.hour)+"-"+str(start_time.minute)+"_"+\
                            str(end_time.day)+"-"+str(end_time.hour)+"-"+str(end_time.minute)+".csv","w"))
    LO_file=csv.writer(open(SubFolder+"LO_"+str(start_time.day)+"-"+str(start_time.hour)+"-"+str(start_time.minute)+"_"+\
                        str(end_time.day)+"-"+str(end_time.hour)+"-"+str(end_time.minute)+".csv","w"))
    Types_file=csv.writer(open(SubFolder+"Types_"+str(start_time.day)+"-"+str(start_time.hour)+"-"+str(start_time.minute)+"_"+\
                        str(end_time.day)+"-"+str(end_time.hour)+"-"+str(end_time.minute)+".csv","w"))
    Del_file=csv.writer(open(SubFolder+"Del_"+str(start_time.day)+"-"+str(start_time.hour)+"-"+str(start_time.minute)+"_"+\
                        str(end_time.day)+"-"+str(end_time.hour)+"-"+str(end_time.minute)+".csv","w"))
    
    Types_file.writerow(Types_VarNames);MO_file.writerow(MO_VarNames);LO_file.writerow(LO_VarNames)
    Del_file.writerow(Del_VarNames)
    for orders in f2:
        book=f1.next()  #orders currently on book
        order_time=GetOrderTime(orders)
        if (order_time>=start_time) and (order_time<end_time):
            
            OB=GetBook(book)  # get the order book
            OrderVars=GetOrderVars(orders,OB) # get the order variables (Time, Type, Distance, Size)
            OBVars=GetOBVars(OB)  # get the order book variables (spread, imbalance total shares etc.)
            time_details=[order_time.day,order_time.hour,order_time.minute,order_time.second]
            if (OrderVars[1]=="MB") or (OrderVars[1]=="MS"): # a market order
                row_mo=[OrderVars[1],OrderVars[3]]; row_mo.extend(OBVars);row_mo.extend(time_details)
                MO_file.writerow(row_mo)
                # add to the Types file
                row_types=[OrderVars[1]]; row_types.extend(OBVars); row_types.extend(time_details)
                Types_file.writerow(row_types)
            elif (OrderVars[1]=="LB") or (OrderVars[1]=="LS"): # a limit order
                row_lo=[OrderVars[1],OrderVars[2],OrderVars[3]]; row_lo.extend(OBVars); row_lo.extend(time_details)
                LO_file.writerow(row_lo)
                # add to Types file
                row_types=[OrderVars[1]]; row_types.extend(OBVars);row_types.extend(time_details)
                Types_file.writerow(row_types)
            
            RecordDelVars(orders,OB,OBVars,Del_file)
	
