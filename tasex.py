# TASEX:
# Tainted symoblic execution -> taint driven concolic execution
#
# First iteration, just filter necessary dependencies that should be
# concrete as they have no impact on considered constraint across
# all its dependencies.

from z3 import *
import time

dword = 32
byte = 8
input_bvs = [SignExt(dword-byte, BitVec(f'off{i}', byte)) for i in range(8)]
concretes = 'B'*15 + '4BB!A' + 'B'*8
const_bvs = [BitVecVal(ord(concretes[idx]), dword) for i in range(8)]

def prove(*args):
    s = Solver()
    if len(args) == 1:
        s.add(Not(args[0]))
    else:
        s.add([*args[:-1], Not(args[-1])])
    print(s.sexpr())
    before = time.time()
    result = s.check()
    elapsed = time.time() - before
    if result == sat:
        print("it is sat!")
        print(s.model())
        print(s.statistics())
    else:
        print("It is unsant")
    print(f"Elapsed {elapsed}")

print('='*20)
print("All inputs are considered as symbolic")
print('='*20)
l1 = inputs_bvs[0] + input_bvs[1] < input_bvs[3] + input_bvs[4] + input_bvs[5]
l2 = inputs_bvs[1] + input_bvs[2] < input_bvs[4] + input_bvs[5] + input_bvs[6]
l3 = inputs_bvs[2] + input_bvs[3] < input_bvs[5] + input_bvs[6] + input_bvs[7]
prove(l1)               # iteration 0
prove(l1,l2)            # iteration 1
prove(l1,l2,l3)         # iteration 2

print('='*20)
print("Partial inputs are considered as symbolic, those that are only involved in considered constraint")
print('='*20)

# skip l1 as it anyway gonna be pure symbolic, though, on the second iteration it might be partially concrete
l1 = const_bvs[0] + input_bvs[1] < const_bvs[3] + input_bvs[4] + input_bvs[5]
l2 = inputs_bvs[1] + input_bvs[2] < input_bvs[4] + input_bvs[5] + input_bvs[6]

# on the third iteration we might consider that two previous iterations already resolved some variables as concrete
l1 = const_bvs[0] + const_bvs[1] < const_bvs[3] + const_bvs[4] + input_bvs[5]
l2 = const_bvs[1] + input_bvs[2] < const_bvs[4] + input_bvs[5] + input_bvs[6]
l3 = inputs_bvs[2] + input_bvs[3] < input_bvs[5] + input_bvs[6] + input_bvs[7]
prove(l1,l2)    # skip iteration 0 and jump on iteration 1 as 0 anyway pure symbolic
prove(l1,l2,l3) # iteration 3 where we turn some variables into concrete in two previous constraints

print('='*20)
print("Greedy turn inputs into concrete as we consider everything we have already met as concrete, those that are only involved in considered constraint")
print('='*20)
# once we solved iteration 0 constraint let's assume it is fully concrete
l2 = const_bvs[1] + const_bvs[2] < const_bvs[4] + const_bvs[5] + input_bvs[6]
# once we solved constraints for iterations 0 and 1 assume they are fully concrete
l3 = const_bvs[2] + const_bvs[3] < const_bvs[5] + const_bvs[6] + input_bvs[7]
prove(l2)
prove(l3)
