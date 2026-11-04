import unittest
from fractions import Fraction as Q
from itertools import product
from reversible_lumpability import example, mv, mm, sq, diagnostic, power

class ReversibleTests(unittest.TestCase):
    def test_symmetric_markov_and_projector(self):
        K,P,N,A = example()
        for i in range(3):
            self.assertEqual(sum(K[i]),1)
            for j in range(3):
                self.assertEqual(K[i][j],K[j][i])
        self.assertEqual(mm(P,P),P)
        self.assertEqual(mm(P,N),tuple(tuple(Q(0) for _ in range(3)) for _ in range(3)))
        self.assertNotEqual(mm(mm(N,K),P),tuple(tuple(Q(0) for _ in range(3)) for _ in range(3)))

    def test_two_step_operator_identity_and_eigenvector(self):
        K,P,N,A = example()
        left = mm(mm(P,power(K,2)),P)
        aa = mm(A,A)
        D = tuple(tuple(left[i][j]-aa[i][j] for j in range(3)) for i in range(3))
        B = mm(mm(N,K),P)
        BtB = tuple(tuple(sum((B[k][i]*B[k][j] for k in range(3)),Q(0))
                            for j in range(3)) for i in range(3))
        self.assertEqual(D,BtB)
        self.assertEqual(D,((Q(1,128),Q(1,128),Q(-1,64)),
                            (Q(1,128),Q(1,128),Q(-1,64)),
                            (Q(-1,64),Q(-1,64),Q(1,32))))
        v = (Q(1),Q(1),Q(-2))
        self.assertEqual(mv(D,v),tuple(Q(3,64)*z for z in v))

    def test_leakage_and_macro_memory_bounds(self):
        eta_sq = Q(3,64)
        for fa,fb in product((-1,0,1),repeat=2):
            f = tuple(Q(x) for x in (fa,fa,fb))
            mass = sq(f)
            for t in range(7):
                leak_sq,macro_sq = diagnostic(t,f)
                self.assertLessEqual(leak_sq,Q(t*t)*eta_sq*mass)
                b = Q(t*(t-1),2)
                self.assertLessEqual(macro_sq,b*b*eta_sq*eta_sq*mass)

    def test_two_step_macro_error_positive(self):
        leak,macro = diagnostic(2,(Q(0),Q(0),Q(1)))
        self.assertGreater(leak,0)
        self.assertGreater(macro,0)

if __name__ == "__main__":
    unittest.main()
