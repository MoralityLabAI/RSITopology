"""Exact rational reversible Markov compression witness, uniform stationary example."""
from fractions import Fraction as Q

def mm(A, B):
    return tuple(tuple(sum((A[i][k]*B[k][j] for k in range(len(B))), Q(0))
                       for j in range(len(B[0]))) for i in range(len(A)))

def mv(A, x):
    return tuple(sum((v*y for v,y in zip(row,x)), Q(0)) for row in A)

def add(x,y,sign=1):
    return tuple(a+sign*b for a,b in zip(x,y))

def sq(x):
    return sum((v*v for v in x), Q(0))

def power(M, n):
    size = len(M)
    out = tuple(tuple(Q(int(i==j)) for j in range(size)) for i in range(size))
    for _ in range(n):
        out = mm(M,out)
    return out

def example():
    K = ((Q(3,4),Q(0),Q(1,4)),
         (Q(0),Q(1,2),Q(1,2)),
         (Q(1,4),Q(1,2),Q(1,4)))
    P = ((Q(1,2),Q(1,2),Q(0)),
         (Q(1,2),Q(1,2),Q(0)),
         (Q(0),Q(0),Q(1)))
    I = ((Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0)),(Q(0),Q(0),Q(1)))
    N = tuple(tuple(I[i][j]-P[i][j] for j in range(3)) for i in range(3))
    A = mm(mm(P,K),P)
    return K,P,N,A

def diagnostic(t, f):
    K,P,N,A = example()
    assert mv(P,f) == f
    micro = mv(power(K,t),f)
    latent = mv(N,micro)
    macro_error = add(mv(P,micro), mv(power(A,t),f), sign=-1)
    return sq(latent),sq(macro_error)
