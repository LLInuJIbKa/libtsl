#!/usr/bin/env python
#Does the finite difference stuff

from numpy import *
from libtsl import geometry, htparams

rod=geometry("rod",1.0/12.0) #rod with 1" diameter

Tinf=72.0

params=htparams(g=32.2, #gravity
        l=rod.d,
        xsect=rod.xsect,
        Tinf=72.0, #deg. F
        kvisc=0.00021, #courtesy Cengel
        k_f=0.01464,  #courtesy Cengel
        k_s=102.3, #courtesy Cengel
        alpha=0.00029)

x=array([0.0, 0.5, 1.5, 3.5, 6.0, 9.0, 12.0, 18.0, 24.0, 30.0, 36.0])
T=array([250.0, Tinf,  Tinf, Tinf, Tinf, Tinf, Tinf, Tinf, Tinf, Tinf, Tinf])
x=x/12.0 #convert to feet
T=T+459.67 #convert to rankines
Tinf=Tinf+459.67 #convert to rankines

#redo this thing a few times
for n in xrange(20):
    A=hstack((1, zeros(len(x)-1)))
    b=T[0]
    for j in xrange(1,len(x)-1):
        params.thermexp=1.0/T[j]
        Apart=zeros(x.size)
        Apart[j-1]=1.0/(x[j]-x[j-1])
        Apart[j+1]=1.0/(x[j+1]-x[j])
        hpoverka=params.hc(T[j],"rod") *rod.p *(x[j+1]-x[j-1]) /params.k_s/rod.xsect/2.0
        Apart[j]=-Apart[j-1]-Apart[j+1]-hpoverka
        b=vstack((b, -hpoverka*Tinf)) #check k_s vs. k_f
        A=vstack((A,Apart))
    A=vstack((A,hstack((zeros(len(x)-1),1)) ))
    b=vstack((b,Tinf))
    #Matrix solution is supposedly not finite difference according to Bargar >_<
    T=linalg.solve(A,b)

    '''
    After wrestling with this thing for a long time, I finally figured out
    how Doc Bargar wanted us to solve it. He's not very good at explaining things!
    basically, he wants us to, for i in [2..8], solve for T_i using T_{i-1} and T_{i+1}.
    In other words, while T_0 and T_11 get left alone (this is good! They're BCs!), the other
    T_i are weighted-averaged on down the line.

    Of course, the solution after cycling through i in [2..8] will be far from exact, but
    that's okay because it wasn't gonna be exact anyway with h and all. You just have
    to iterate!  ...a lot.

    Upshot: Bargar wasn't talking out of his ass after all.
    Downshot: This method may have some pretty crummy convergence properties.
    '''

x=x*12.0 #back to inches
T=T-459.67 #back to F
print "__X__ __T__"
for xypair in zip(x,T):
    print xypair[0], xypair[1][0]
    
