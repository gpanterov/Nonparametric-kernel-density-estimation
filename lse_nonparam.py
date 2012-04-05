import csv
import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import random
import rpy2.rlike.container as rlc


NP=importr('np')
r=robjects.r

def GetBW_MO(FolderOut,FolderData,start,end): # Returns an R vector of the bandwidht and two data frames with the dep and indep variables (entire training sample)
    counter=0
    var1=[];var2=[];var3=[];var4=[];var5=[]
    ty={}; tx={}  # the two data frames for dependent (ty) and indep (tx)
    ty['size']=[];ty['type']=[];
    tx['spread']=[];tx['order_imb']=[];tx['shares_imb']=[]
    for i in range (start,end):
        try:
            f=csv.reader(open(FolderOut+"MO_"+str(i)+".out","r"))
            data_file=csv.DictReader(open(FolderData +"MO_" +str(i)+".csv","r"))
            counter+=1  # if new file opened add to the counter
            line=f.next()
            print line
            line=line[0].split(" ")
            line=[float(i) for i in line]
            var1.append(line[0]);var2.append(line[1]);var3.append(line[2]);var4.append(line[3]);var5.append(line[4])
            
            for obs in data_file:
                ty['size'].append(float(obs['size'])); ty['type'].append(obs['type'])
                tx['spread'].append(float(obs['spread']));tx['order_imb'].append(float(obs['order_imb'])); tx['shares_imb'].append(float(obs['shares_imb']))
        except:
            pass
    
    # you need to remove abnormally large bandiwdth estimation. Perhaps take the log of the size in order to eliminate outliers.
    
    bw1=sum(var1)/counter; bw2=sum(var2)/counter; bw3=sum(var3)/counter; bw4=sum(var4)/counter; bw5=sum(var5)/counter;
    bw=[bw1,bw2,bw3,bw4,bw5]
    bw=robjects.FloatVector(bw)
    print bw
    
    ty['type']=robjects.FactorVector(ty['type']); ty['size']=robjects.IntVector(ty['size'])
    tx['spread']=robjects.FloatVector(tx['spread']); tx['order_imb']=robjects.FloatVector(tx['order_imb']); tx['shares_imb']=robjects.FloatVector(tx['shares_imb']);
    TY=rlc.OrdDict([('size',ty['size']),('type',ty['type'])])
    TX=rlc.OrdDict([('spread',tx['spread']),('order_imb',tx['order_imb']),('shares_imb',tx['shares_imb'])])
    ty=robjects.DataFrame(TY); tx=robjects.DataFrame(TX);
    return bw,ty,tx

def GetBW_LO(FolderOut,FolderData,start,end): # Returns an R vector of the bandwidht and two data frames with the dep and indep variables (entire training sample)
    counter=0
    var1=[];var2=[];var3=[];var4=[];var5=[]; var6=[]
    ty={}; tx={}  # the two data frames for dependent (ty) and indep (tx)
    ty['distance']=[];ty['size']=[];ty['type']=[];
    tx['spread']=[];tx['order_imb']=[];tx['shares_imb']=[]
    for i in range (start,end):
        try:
            f=csv.reader(open(FolderOut+"LO_"+str(i)+".out","r"))
            data_file=csv.DictReader(open(FolderData +"LO_" +str(i)+".csv","r"))
            counter+=1  # if new file opened add to the counter
            line=f.next()
            print line
            line=line[0].split(" ")
            line=[float(i) for i in line]
            var1.append(line[0]);var2.append(line[1]);var3.append(line[2]);var4.append(line[3]);var5.append(line[4]); var6.append(line[5])
            
            for obs in data_file:
                ty['distance'].append(float(obs['distance']));ty['size'].append(float(obs['size'])); ty['type'].append(obs['type'])
                tx['spread'].append(float(obs['spread']));tx['order_imb'].append(float(obs['order_imb'])); tx['shares_imb'].append(float(obs['shares_imb']))

        except:
            pass
    bw1=sum(var1)/counter; bw2=sum(var2)/counter; bw3=sum(var3)/counter; bw4=sum(var4)/counter; bw5=sum(var5)/counter;bw6=sum(var6);
    bw=[bw1,bw2,bw3,bw4,bw5,bw6]
    bw=robjects.FloatVector(bw)
    print bw
    ty['type']=robjects.FactorVector(ty['type']); ty['size']=robjects.IntVector(ty['size']); ty['distance']=robjects.FloatVector(ty['distance'])
    tx['spread']=robjects.FloatVector(tx['spread']); tx['order_imb']=robjects.FloatVector(tx['order_imb']); tx['shares_imb']=robjects.FloatVector(tx['shares_imb']);
    # Need to use rlc.OrdDict because when you convert to dataframe a dictionary the order of the columns gets lost
    TY=rlc.OrdDict([('distance',ty['distance']),('size',ty['size']),('type',ty['type'])])
    TX=rlc.OrdDict([('spread',tx['spread']),('order_imb',tx['order_imb']),('shares_imb',tx['shares_imb'])])
    ty=robjects.DataFrame(TY); tx=robjects.DataFrame(TX);

    return bw,ty,tx

def GetBW_Type(FolderOut,FolderData,start,end): # Returns an R vector of the bandwidht and two data frames with the dep and indep variables (entire training sample)
    counter=0
    var1=[];var2=[];var3=[];var4=[];var5=[]; 
    ty={}; tx={}  # the two data frames for dependent (ty) and indep (tx)
    ty['type']=[];
    tx['spread']=[];tx['order_imb']=[];tx['shares_imb']=[]; tx['shares_tot']=[]
    for i in range (start,end):
        try:
            f=csv.reader(open(FolderOut+"Type_"+str(i)+".out","r"))
            data_file=csv.DictReader(open(FolderData +"Type_" +str(i)+".csv","r"))
            counter+=1  # if new file opened add to the counter
            line=f.next()
            print line
            line=line[0].split(" ")
            line=[float(i) for i in line]
            var1.append(line[0]);var2.append(line[1]);var3.append(line[2]);var4.append(line[3]);var5.append(line[4]);
            
            for obs in data_file:
                ty['type'].append(obs['type'])
                tx['spread'].append(float(obs['spread']));tx['order_imb'].append(float(obs['order_imb'])); tx['shares_imb'].append(float(obs['shares_imb']))
                tx['shares_tot'].append(float(obs['shares_tot']))

        except:
            pass
    bw1=sum(var1)/counter; bw2=sum(var2)/counter; bw3=sum(var3)/counter; bw4=sum(var4)/counter; bw5=sum(var5)/counter;
    bw=[bw1,bw2,bw3,bw4,bw5]
    bw=robjects.FloatVector(bw)
    print bw
    ty['type']=robjects.FactorVector(ty['type']);
    tx['spread']=robjects.FloatVector(tx['spread']); tx['order_imb']=robjects.FloatVector(tx['order_imb']); tx['shares_imb']=robjects.FloatVector(tx['shares_imb']);
    tx['shares_tot']=robjects.IntVector(tx['shares_tot'])
    # Need to use rlc.OrdDict because when you convert to dataframe a dictionary the order of the columns gets lost
    TY=rlc.OrdDict([('type',ty['type'])])
    TX=rlc.OrdDict([('spread',tx['spread']),('order_imb',tx['order_imb']),('shares_imb',tx['shares_imb']),('shares_tot',tx['shares_tot'])])
    ty=robjects.DataFrame(TY); tx=robjects.DataFrame(TX);

    
    return bw,ty,tx

def GetBW_Del(FolderOut,FolderData,start,end): # Returns an R vector of the bandwidht and two data frames with the dep and indep variables (entire training sample)
    
    var1=[];var2=[];var3=[];var4=[];var5=[];nobs=[]
    ty={}; tx={}  # the two data frames for dependent (ty) and indep (tx)
    ty['Deleted']=[];
    tx['RelPos']=[];tx['N_Prec_Change']=[];tx['Vol_Prec_Change']=[]; tx['elapsed_seconds']=[]
    for i in range (start,end):
        try:
            f=csv.reader(open(FolderOut+"Del_"+str(i)+".out","r"))
            data_file=csv.DictReader(open(FolderData +"Del_" +str(i)+".csv","r"))
            
            line=f.next()
            print line
            line=line[0].split(" ")
            line=[float(i) for i in line]
            var1.append(line[0]);var2.append(line[1]);var3.append(line[2]);var4.append(line[3]);var5.append(line[4]); nobs.append(line[5])
            
            for obs in data_file:
                ty['Deleted'].append(obs['Deleted'])
                tx['RelPos'].append(float(obs['RelPos']));tx['N_Prec_Change'].append(float(obs['N_Prec_Change']));
                tx['Vol_Prec_Change'].append(float(obs['Vol_Prec_Change']))
                tx['elapsed_seconds'].append(float(obs['elapsed_seconds']))

        except:
            pass
    tot_obs=sum(nobs)
    bw1=sum(np.array(var1)*np.array(nobs))/tot_obs;
    bw2=sum(np.array(var2)*np.array(nobs))/tot_obs;
    bw3=sum(np.array(var3)*np.array(nobs))/tot_obs;
    bw4=sum(np.array(var4)*np.array(nobs))/tot_obs;
    bw5=sum(np.array(var5)*np.array(nobs))/tot_obs;
    bw=[bw1,bw2,bw3,bw4,bw5]
    bw=robjects.FloatVector(bw)
    print bw
    ty['Deleted']=robjects.FactorVector(ty['Deleted']);
    tx['RelPos']=robjects.FloatVector(tx['RelPos']); tx['N_Prec_Change']=robjects.FloatVector(tx['N_Prec_Change']);
    tx['Vol_Prec_Change']=robjects.FloatVector(tx['Vol_Prec_Change']); tx['elapsed_seconds']=robjects.FloatVector(tx['elapsed_seconds'])

    TY=rlc.OrdDict([('Deleted',ty['Deleted'])])
    TX=rlc.OrdDict([('RelPos',tx['RelPos']),('N_Prec_Change',tx['N_Prec_Change']),('Vol_Prec_Change',tx['Vol_Prec_Change']),('elapsed_seconds',tx['elapsed_seconds'])])
    ty=robjects.DataFrame(TY); tx=robjects.DataFrame(TX);

    return bw,ty,tx


def DrawMO(bw,ty,tx,indep_vars):  # Draws from the MO distro. indep_vars should be a list
    indep=rlc.OrdDict([('spread',robjects.FloatVector([indep_vars[0]])),('order_imb',robjects.FloatVector([indep_vars[1]])),\
                      ('shares_imb',robjects.FloatVector([indep_vars[2]]))])
    indep=robjects.DataFrame(indep)
    z=random.random()
    for TYPE in ["MB","MS"]:
        for SIZE in range(100,30000,250):
            new_dep=rlc.OrdDict([('size',robjects.IntVector([SIZE])), ('type',robjects.FactorVector([TYPE]))]); new_dep=robjects.DataFrame(new_dep)
            cum_prob=r.fitted(NP.npcdist(tydat=ty,txdat=tx,bws=bw,bwscaling=True,eydat=new_dep,exdat=indep))
            print TYPE,SIZE,cum_prob[0]
            if z<cum_prob[0]:
                print "z is: ", z
                print "the cumulative prob is: ",cum_prob[0]
                return TYPE,SIZE

            
FolderOut="/home/gpanterov/Documents/LSE_OrderBook/temp/newdata/MO/OUT/"
FolderData="/home/gpanterov/Documents/LSE_OrderBook/temp/newdata/MO/"

bw,ty,tx=GetBW_MO(FolderOut,FolderData,0,24)
indep_vars=[0.003,0.336,0.899]
s,t=DrawMO(bw,ty,tx,indep_vars)
