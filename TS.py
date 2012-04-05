from numpy import *
import matplotlib.pyplot as plt
from scipy.optimize import *
a=array(range(1,20))


# Calibrate the model
T=150 # number of periods (number of obs. in the sample)
sigma=1.5 # This is the variance of the innovations
rho=array(0.7)  # Should be less than one
psi=0.2
c=0 # Constant term (drift)

y=ones(T)
eps=random.normal(0,sqrt(sigma),T)  # White noise innovations
eps[0]=0
y[0]=0  # Set a deterministic initial values


# Create an ARCH(1) process
z=eps; a0=0.5; a1=0.4;a2=0.2; sig2=ones(T); e=ones(T)-1; y_arch=ones(T)-1

for t in range(1,T):
    
    sig2[t]=a0+a1*e[t-1]**2
    e[t]=z[t]*sqrt(sig2[t])
    y_arch[t]=c+e[t]
# Create the AR(1) process
for k in range(1,T):
    
    y[k]=c+rho*y[k-1] + eps[k]


# Create the equivalent MA representation of the AR(1) process

y_ma=ones(T); y_ma[0]=y[0]
for k in range(1,T):
    h=range(k+1)
    rho_m=rho*ones(k+1)
    y_ma[k]=sum(eps[k::-1]*(rho_m**h))

MA=ones(T)-1
for k in range(1,T):
    
    MA[k]=c+psi*eps[k-1]+eps[k]
    
m=c/(1-rho)


def Cov_hat(y,h):
    return cov(y[h::],y[:-h:])

def ACF(y,h):
    return array([Cov_hat(y,i)[0,1] for i in range(1,h+1)])/Cov_hat(y,i)[0,0]

def AR_OLS(y):
    h=1; n=len(y)
    X=array([ones(n-h),y[:-h:]]).T
    X=mat(X)
    y=mat(y[h::]).T
    return ((X.T*X).I)*(X.T*y)

def MA_eps(y,t,psi):
    n=len(y)
    psi_m=psi*ones(t)
    
    #eps=psi_m**(range(t))*y[t-1::-1]*(-ones(t))**range(t)
    eps_t=y-psi*MA_eps(y,t-1,psi)
    return eps_t




def ARCH_Sig2(y,t,a0,a1,c):
    if t<=0: return 0
    z=(y-c)**2/sig2
    sig2_t=a0+a1*(z[t-1]**2)*ARCH_Sig(z,t-1,a0,a1)
    return sig2_t

def ARCH_Sig(z,t,a0,a1):
    if t<=0: return array([1])
    sig2_t=a0+a1*(z[t-1]**2)*ARCH_Sig(z,t-1,a0,a1)
    return sig2_t



def ARCH_Errors(Tu,y,t):
    c=Tu[0];a0=Tu[1];a1=Tu[2]
    if t<=0 : return array([1])
    
    z=(y[0:t]-c)/ARCH_Sig(ARCH_Errors((c,a0,a1),y,t-1),t-1,a0,a1)**0.5
    return z

#ARCH_Errors((0,a0,a1),y,20)

def ARCH_Likelihood(Tu,y,sigma):
    c=Tu[0];a0=Tu[1];a1=Tu[2]
    T=len(y)
    return -sum(-(T-1)*log(2*pi)/2 - (T-1)*log(sigma)/2-(ARCH_Errors((c,a0,a1),y,T)**2)/(0.5*sigma))
    

    
def ARCH2(z,t,(a0,a1,a2)):
    args=(a1,a2,a3)
    a=args
    if t<=0: return 0
    
    sig2_t=a[0]+a[1]*(z[t-1]**2)*ARCH2(z,t-1,args)+a[2]*(z[t-2]**2)*ARCH2(z,t-2,args)
    return sig2_t



# This function recursively returns the estimate of eps_t based on the initial value
# 
def MA_eps2(y,t,psi):
    if t<=0:
        return 0
    eps_t=y[t]-psi*MA_eps2(y,t-1,psi)
    return eps_t

def MA_likelihood (psi,y, sigma , q=1):
    T=len(y)
    err=array([MA_eps2(y,k,psi) for k in range(1,T)])
    return -sum(-(T-1)*log(2*pi)/2 - (T-1)*log(sigma)/2-(err**2)/(0.5*sigma))


x0=(0.5,0.9,0.3)

xopt=fmin(ARCH_Likelihood,x0,args=(y_arch,sigma))
    
'''
plt.plot(y_arch)
plt.show()
'''
