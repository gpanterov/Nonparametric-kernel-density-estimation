import numpy as np
import csv

vintage=csv.reader(open('Daily Currencies.csv'))

# Create a dictionary that stores the data. The keys of the dictionary are the variable names

varnames=vintage.next()  # This simply goes through the first entry (the variable names) so that they are not entered twice
nvars=len(varnames)
data=dict(zip(varnames,np.ones(nvars)))
for row in vintage:
    for V in range(1,nvars):
        
        try:
            data[varnames[V]].append(float(row[V]))
            
        except ValueError: data[varnames[V]].append(float(data[varnames[V]][-1]))
        except: data[varnames[V]].append('NA')
           
    

# Form the logs

##aud_us_log=np.log(data['exalus'])
##ret_dlog=aud_us_log[1::]-aud_us_log[0:-1]
##ret_d=(aud_us[1::]-aud_us[0:-1])/aud_us[0:-1]

# Form the moving averages

def MA(series,l):
    n=len(series)
    MA_series=np.ones(n)
    for i in range(l,n):
        k=i-l
        MA_series[i-1]=np.sum(series[k:i])/l
        assert len(series[k:i])==l
    return MA_series


def buy_sell(series,Long,Short,band=0):
    MA_Long=MA(series,Long); MA_Short=MA(series,Short)
    MA_Long=MA_Long[Long-1::]; MA_Short=MA_Short[Long-1::]; series=series[Long-1::]
    buy=MA_Short > MA_Long*(1+band)
    sell=MA_Short < MA_Long*(1-band)

    buy=series*buy
    sell=series*sell
    e=1e-15
    
    b_series=series[1::]*(buy[0:-1]!=0)
    profit_buy=(b_series-buy[0:-1])/(buy[0:-1]+e)
    assert np.max(profit_buy)<1e3 and np.min(profit_buy)>-1e3
    
    s_series=series[1::]*(sell[0:-1]!=0)
    profit_sell=(sell[0:-1]-s_series)/(sell[0:-1]+e)
    assert np.max(profit_sell)<1e3 and np.min(profit_sell)>-1e3
    
    N=len(series); Nb=np.sum(buy[0:-1]!=0); Ns=np.sum(sell[0:-1]!=0)
    ret_series=(series[1::]-series[0:-1])/series[0:-1]
    #return ret_series,profit_buy,profit_sell,N,Nb,Ns
    buy=profit_buy; sell=profit_sell;
    sig2=np.var(ret_series); mu=np.mean(ret_series) ; mu_b=np.mean(buy); mu_s=np.mean(sell)
    mu_comb=np.mean(buy+sell); N_comb=Nb+Ns; sig2_comb=np.var(buy+sell)

    t_b= (mu_b-mu)/(sig2/N +sig2/Nb)**0.5
    t_s=(mu_s-mu)/(sig2/N +sig2/Ns)**0.5

    t_bs=(mu_b-mu_s)/(sig2/Nb +sig2/Ns)**0.5

    t_comb=(mu_comb-mu)/(sig2/N +sig2_comb/N_comb)**0.5

    return mu_b, mu_s, mu_comb, t_b, t_s, t_comb

##series_label='exalus'
##series=np.array(data[series_label])
##l=200; s=5; band=0;
##mu_b, mu_s, mu_comb, t_b, t_s, t_comb=buy_sell(series,l,s,band)

##results_writer=csv.writer(open('trading_results.csv', 'wb'), delimiter=',')
##results_writer.writerow (['Series','Trading Rule', 'Mean for Buy Trades',' Mean for Sell Trades', 'Mean for both'])
##results_writer.writerow ([series_label,str(l)+'-'+str(s)+'-'+str(band),mu_b,mu_s,mu_comb])
##results_writer.writerow ([' ','t-stat ',t_b,t_s,t_comb])
##
##print 'mu_b = ', mu_b,'(',t_b,')'
##print 'mu_s = ', mu_s,'(',t_s,')'
##print 'mu_comb = ', mu_comb,'(',t_comb,')'
