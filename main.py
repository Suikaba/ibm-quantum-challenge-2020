def qor(qc, a, b, c):
    qc.x(a)
    qc.x(b)
    qc.ccx(a, b, c)
    qc.x(c)
    qc.x(a)
    qc.x(b)

def inner_phase_oracle(qc, perm, oracle, aux):
    def check_one(i, j, out):
        qc.cx(perm[i*2], perm[j*2])
        qc.cx(perm[i*2+1], perm[j*2+1])
        qor(qc, perm[j*2], perm[j*2+1], out)
        qc.cx(perm[i*2], perm[j*2])
        qc.cx(perm[i*2+1], perm[j*2+1])

    def check_all():
        workspace = aux[0:6]
        itr = 0
        for i in range(4):
            for j in range(i + 1, 4):
                check_one(i, j, workspace[itr])
                itr += 1

    check_all()
    qc.mct(aux[0:6], oracle, aux[6:], mode='basic')
    check_all()

def inner_diffusion(qc, perm, aux):
    qc.h(perm)
    qc.x(perm)
    qc.h(perm[7])
    qc.mct(perm[0:7], perm[7], aux, mode='basic')
    qc.h(perm[7])
    qc.x(perm)
    qc.h(perm)

# create permutations by grover search
iter_cnt1 = 2 # 2 is best
def create_perm(qc, perm, oracle, aux):
    for i in range(iter_cnt1):
        inner_phase_oracle(qc, perm, oracle, aux)
        inner_diffusion(qc, perm, aux)

def inv_create_perm(qc, perm, oracle, aux):
    for i in range(iter_cnt1):
        inner_diffusion(qc, perm, aux)
        inner_phase_oracle(qc, perm, oracle, aux)


def adder3(qc, s, x, c):
    qc.rccx(x, s[0], c[0])
    qc.rccx(c[0], s[1], c[1])
    qc.cx(c[1], s[2])
    qc.rccx(c[0], s[1], c[1])
    qc.cx(c[0], s[1])
    qc.rccx(x, s[0], c[0])
    qc.cx(x, s[0])

# after call, c become dirty bit
def adder3_dirty(qc, s, x, c):
    qc.rccx(x, s[0], c[0])
    qc.rccx(c[0], s[1], c[1])
    qc.cx(c[1], s[2])
    #qc.rccx(c[0], s[1], c[1])
    qc.cx(c[0], s[1])
    #qc.rccx(x, s[0], c[0])
    qc.cx(x, s[0])

def inv_adder3(qc, s, x, c):
    qc.cx(x, s[0])
    qc.rccx(x, s[0], c[0])
    qc.cx(c[0], s[1])
    qc.rccx(c[0], s[1], c[1])
    qc.cx(c[1], s[2])
    qc.rccx(c[0], s[1], c[1])
    qc.rccx(x, s[0], c[0])

def inv_adder3_dirty(qc, s, x, c):
    qc.cx(x, s[0])
    #qc.rccx(x, s[0], c[0])
    qc.cx(c[0], s[1])
    #qc.rccx(c[0], s[1], c[1])
    qc.cx(c[1], s[2])
    qc.rccx(c[0], s[1], c[1])
    qc.rccx(x, s[0], c[0])

def is_count4(qc, xs, out, dirty, aux):
    assert len(dirty) >= 4
    assert len(aux) >= 1
    s = [xs[0], dirty[0], dirty[1]]
    adder3(qc, s, xs[1], dirty[2:])
    adder3(qc, s, xs[2], dirty[2:])
    adder3(qc, s, xs[3], dirty[2:])
    adder3(qc, s, xs[4], dirty[2:])
    adder3_dirty(qc, s, xs[5], dirty[2:])
    qc.x(s[0])
    qc.x(s[1])
    qc.mct(s, out, aux[0:], mode='basic')
    qc.x(s[1])
    qc.x(s[0])

def inv_is_count4(qc, xs, out, dirty, aux):
    assert len(dirty) >= 4
    assert len(aux) >= 1
    s = [xs[0], dirty[0], dirty[1]]
    qc.x(s[0])
    qc.x(s[1])
    qc.mct(s, out, aux[0:], mode='basic')
    qc.x(s[1])
    qc.x(s[0])
    inv_adder3_dirty(qc, s, xs[5], dirty[2:])
    inv_adder3(qc, s, xs[4], dirty[2:])
    inv_adder3(qc, s, xs[3], dirty[2:])
    inv_adder3(qc, s, xs[2], dirty[2:])
    inv_adder3(qc, s, xs[1], dirty[2:])

# addr == 1
def check_one_board(qc, addr, perm, oracle, aux, stars):
    assert len(aux) >= 15
    workspace = aux[0:6]
    aux2 = aux[6:] # can use 9 aux
    def proc():
        for i in range(6):
            r, c = int(stars[i][0]), int(stars[i][1])
            q1, q2 = perm[r*2], perm[r*2+1]
            if c == 0:
                qc.x(q1)
                qc.x(q2)
            elif c == 1:
                qc.x(q1)
            elif c == 2:
                qc.x(q2)

            qc.rccx(q1, q2, workspace[i])

            if c == 0:
                qc.x(q1)
                qc.x(q2)
            elif c == 1:
                qc.x(q1)
            elif c == 2:
                qc.x(q2)

    proc()
    is_count4(qc, workspace, aux2[0], aux2[1:5], aux2[5:])
    qc.mct([addr[0], addr[1], addr[2], addr[3], aux2[0]], oracle, aux2[5:], mode='basic')
    inv_is_count4(qc, workspace, aux2[0],aux2[1:5], aux2[5:])
    proc()

# memo: gray_code
# 15, 14, 10, 11, 9, 8, 0, 1, 3, 2, 6, 7, 5, 4, 12, 13
def phase_oracle(qc, addr, perm, oracle, aux, problem_set):
    create_perm(qc, perm, oracle, aux)

    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1111])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1110])
    qc.x(addr[1])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1010])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1011])
    qc.x(addr[2])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1001])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1000])
    qc.x(addr[0])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0000])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0001])
    qc.x(addr[2])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0011])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0010])
    qc.x(addr[1])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0110])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0111])
    qc.x(addr[2])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0101])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b0100])
    qc.x(addr[0])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1100])
    qc.x(addr[3])
    check_one_board(qc, addr, perm, oracle, aux, problem_set[0b1101])
    qc.x(addr[2])

    # inversion
    inv_create_perm(qc, perm, oracle, aux)


def diffusion(qc, addr, perm, aux):
    tmp = [None] * 12
    for i in range(4):
        tmp[i] = addr[i]
    for i in range(8):
        tmp[i + 4] = perm[i]
    qc.h(tmp)
    qc.x(tmp)
    qc.h(tmp[11])
    qc.mct(tmp[0:11], tmp[11], aux, mode='basic')
    qc.h(tmp[11])
    qc.x(tmp)
    qc.h(tmp)


def week3_ans_func(problem_set):
    address = QuantumRegister(4)
    perm = QuantumRegister(8) # row and col
    oracle = QuantumRegister(1)
    aux = QuantumRegister(15)
    solution = ClassicalRegister(4)
    #solution = ClassicalRegister(8) # perm
    #solution = ClassicalRegister(3) # adder
    #solution = ClassicalRegister(5) # is_count4, inv_is_count4
    #solution = ClassicalRegister(9) # check_one_board
    #solution = ClassicalRegister(12) # oracle
    qc = QuantumCircuit(address, perm, oracle, aux, solution)

    # answer -------------------------------------------------------------------
    # initialize
    qc.h(address)
    qc.h(perm)
    qc.x(oracle)
    qc.h(oracle)

    for i in range(1):
        phase_oracle(qc, address, perm, oracle, aux, problem_set)
        diffusion(qc, address, perm, aux)

    qc.measure(address, solution)
    # answer: addr == 10 (0b1010)

    # test perm ----------------------------------------------------------------
    #qc.h(perm)
    #qc.x(oracle)
    #qc.h(oracle)

    #create_perm(qc, perm, oracle[0], aux)

    #qc.measure(perm, solution)

    # test adder3 --------------------------------------------------------------
    #qc.h(aux[0:2])
    #qc.x(aux[3])
    #adder3(qc, aux[0:3], aux[3], aux[4:])
    #qc.measure(aux[0:3], solution)

    # test is_count4 -----------------------------------------------------------
    #qc.h(perm[0:4])
    #is_count4(qc, perm[0:6], oracle[0], aux)
    #qc.measure(perm[0:4], solution[0:4])
    #qc.measure(oracle[0], solution[4])

    # test inv_is_count4 -------------------------------------------------------
    #qc.h(perm[0:4])
    #is_count4(qc, perm[0:6], oracle[0], aux)
    #inv_is_count4(qc, perm[0:6], oracle[0], aux)
    #qc.measure(perm[0:4], solution[0:4])
    #qc.measure(oracle[0], solution[4])

    # test check_one_board -----------------------------------------------------
    problem_set = \
        [[['0', '2'], ['1', '0'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '3']],
        [['0', '0'], ['0', '1'], ['1', '2'], ['2', '2'], ['3', '0'], ['3', '3']],
        [['0', '0'], ['1', '1'], ['1', '3'], ['2', '0'], ['3', '2'], ['3', '3']],
        [['0', '0'], ['0', '1'], ['1', '1'], ['1', '3'], ['3', '2'], ['3', '3']],
        [['0', '2'], ['1', '0'], ['1', '3'], ['2', '0'], ['3', '2'], ['3', '3']],
        [['1', '1'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '1'], ['3', '3']],
        [['0', '2'], ['0', '3'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '3']],
        [['0', '0'], ['0', '3'], ['1', '2'], ['2', '2'], ['2', '3'], ['3', '0']],
        [['0', '3'], ['1', '1'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '3']],
        [['0', '0'], ['0', '1'], ['1', '3'], ['2', '1'], ['2', '3'], ['3', '0']],
        [['0', '1'], ['0', '3'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '2']],
        [['0', '0'], ['1', '3'], ['2', '0'], ['2', '1'], ['2', '3'], ['3', '1']],
        [['0', '1'], ['0', '2'], ['1', '0'], ['1', '2'], ['2', '2'], ['2', '3']],
        [['0', '3'], ['1', '0'], ['1', '3'], ['2', '1'], ['2', '2'], ['3', '0']],
        [['0', '2'], ['0', '3'], ['1', '2'], ['2', '3'], ['3', '0'], ['3', '1']],
        [['0', '1'], ['1', '0'], ['1', '2'], ['2', '2'], ['3', '0'], ['3', '1']]]
    #qc.h(perm)
    #qc.x(address)
    #board = problem_set[0]
    #check_one_board(qc, address, perm, oracle, aux, board)
    #qc.measure(perm, solution[0:8])
    #qc.measure(oracle, solution[8])

    # test oracle --------------------------------------------------------------
    #qc.h(perm)
    #qc.h(address)
    #qc.x(oracle)
    #qc.h(oracle)

    #for i in range(2):
    #    create_perm(qc, perm, oracle, aux)
    #    check_one_board(qc, address, perm, oracle, aux, problem_set[10])
    #    inv_create_perm(qc, perm, oracle, aux)

    #    diffusion(qc, address, perm, aux)


    #qc.h(oracle)
    #qc.x(oracle)
    ##qc.measure(perm, solution[0:8])
    #qc.measure(address, solution[8:12])

    return qc
