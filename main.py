import math

def qor(qc, a, b, c):
    qc.x(a)
    qc.x(b)
    qc.ccx(a, b, c)
    qc.x(c)
    qc.x(a)
    qc.x(b)


def adder3(qc, s, x, c):
    qc.ccx(x, s[0], c[0])
    qc.ccx(c[0], s[1], c[1])
    qc.cx(c[1], s[2])
    qc.ccx(c[0], s[1], c[1])
    qc.cx(c[0], s[1])
    qc.ccx(x, s[0], c[0])
    qc.cx(x, s[0])

def inv_adder3(qc, s, x, c):
    qc.cx(x, s[0])
    qc.ccx(x, s[0], c[0])
    qc.cx(c[0], s[1])
    qc.ccx(c[0], s[1], c[1])
    qc.cx(c[1], s[2])
    qc.ccx(c[0], s[1], c[1])
    qc.ccx(x, s[0], c[0])


def is_count3(qc, shots, out, aux):
    s = [shots[0], aux[0], aux[1]]
    c = aux[3:5]
    for i in range(7):
        adder3(qc, s, shots[i+1], c)
    qc.x(s[2])
    qc.mct(s, out, aux[5:], mode='basic')
    qc.x(s[2])
    for i in reversed(range(7)):
        inv_adder3(qc, s, shots[i+1], c)


def store_asteroids(qc, addr, data, shots, aux, asteroids):
    aux2 = aux[1:]
    qc.mct(addr, aux[0], aux2, mode='basic')
    for i in range(6):
        r, c = int(asteroids[i][0]), int(asteroids[i][1])
        qc.cx(shots[r], aux2[0])
        qc.cx(shots[4+c], aux2[1])
        qor(qc, aux2[0], aux2[1], aux2[2])
        qc.ccx(aux[0], aux[2], data[i])
        qor(qc, aux2[0], aux2[1], aux2[2])
        qc.cx(shots[r], aux2[0])
        qc.cx(shots[4+c], aux2[1])
    qc.mct(addr, aux[0], aux2, mode='basic')


def store_data(qc, addr, data, shots, aux, problem_set):
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1111])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1110])
    qc.x(addr[1])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1010])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1011])
    qc.x(addr[2])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1001])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1000])
    qc.x(addr[0])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0000])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0001])
    qc.x(addr[2])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0011])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0010])
    qc.x(addr[1])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0110])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0111])
    qc.x(addr[2])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0101])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b0100])
    qc.x(addr[0])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1100])
    qc.x(addr[3])
    store_asteroids(qc, addr, data, shots, aux, problem_set[0b1101])
    qc.x(addr[2])


# find 3-shots
def inner_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set):
    store_data(qc, addr, data, shots, aux, problem_set)
    is_count3(qc, shots, aux[0], aux[1:])
    qc.mct(data, aux[1], aux[2:])

    qc.ccx(aux[0], aux[1], oracle)

    qc.mct(data, aux[1], aux[2:])
    is_count3(qc, shots, aux[0], aux[1:])
    store_data(qc, addr, data, shots, aux, problem_set)


def inner_diffusion(qc, addr, shots, aux):
    tmp = [None] * 12
    for i in range(4):
        tmp[i] = addr[i]
    for i in range(8):
        tmp[i+4] = shots[i]

    qc.h(tmp)
    qc.x(tmp)
    qc.h(tmp[11])
    qc.mct(tmp[0:11], tmp[11], aux, mode='basic')
    qc.h(tmp[11])
    qc.x(tmp)
    qc.h(tmp)

inner_iter_cnt = 30
def inner_grover(qc, addr, data, shots, oracle, aux, problem_set):
    for i in range(inner_iter_cnt):
        inner_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set)
        inner_diffusion(qc, addr, shots, aux)

def inv_inner_grover(qc, addr, data, shots, oracle, aux, problem_set):
    for i in range(inner_iter_cnt):
        inner_diffusion(qc, addr, shots, aux)
        inner_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set)


def outer_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set):
    inner_grover(qc, addr, data, shots, oracle, aux, problem_set)

    # All outer grover needs is only diffusion

    inv_inner_grover(qc, addr, data, shots, oracle, aux, problem_set)

def outer_diffusion(qc, addr, aux):
    qc.h(addr)
    qc.x(addr)
    qc.h(addr[3])
    qc.mct(addr[0:3], addr[3], aux, mode='basic')
    qc.h(addr[3])
    qc.x(addr)
    qc.h(addr)


# pretest
prob1 = \
    [[['0', '1'], ['0', '2'], ['1', '0'], ['2', '0'], ['3', '1'], ['3', '3']],
    [['0', '2'], ['0', '3'], ['1', '1'], ['1', '3'], ['2', '0'], ['2', '1']],
    [['0', '0'], ['0', '3'], ['2', '1'], ['2', '2'], ['3', '0'], ['3', '1']],
    [['0', '0'], ['0', '1'], ['0', '2'], ['1', '1'], ['2', '0'], ['3', '2']],
    [['0', '1'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '0'], ['3', '1']],
    [['0', '2'], ['0', '3'], ['1', '1'], ['2', '0'], ['2', '1'], ['3', '0']],
    [['0', '0'], ['0', '3'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '3']], # answer: 6
    [['0', '2'], ['1', '1'], ['1', '3'], ['2', '0'], ['2', '3'], ['3', '2']],
    [['0', '1'], ['0', '3'], ['2', '0'], ['2', '2'], ['3', '0'], ['3', '3']],
    [['0', '0'], ['0', '2'], ['1', '0'], ['2', '2'], ['2', '3'], ['3', '3']],
    [['1', '0'], ['1', '3'], ['2', '1'], ['2', '2'], ['3', '2'], ['3', '3']],
    [['0', '0'], ['1', '0'], ['2', '1'], ['2', '2'], ['3', '2'], ['3', '3']],
    [['0', '0'], ['1', '1'], ['1', '2'], ['2', '1'], ['2', '3'], ['3', '0']],
    [['0', '1'], ['0', '3'], ['2', '1'], ['2', '2'], ['3', '0'], ['3', '1']],
    [['0', '0'], ['0', '1'], ['1', '1'], ['1', '3'], ['3', '2'], ['3', '3']],
    [['0', '0'], ['0', '3'], ['1', '2'], ['1', '3'], ['3', '0'], ['3', '1']]]
prob2 = \
    [[['0', '0'], ['0', '2'], ['1', '0'], ['1', '1'], ['3', '1'], ['3', '3']],
    [['0', '2'], ['0', '3'], ['1', '1'], ['1', '3'], ['2', '0'], ['2', '1']],
    [['0', '0'], ['1', '0'], ['2', '1'], ['2', '3'], ['3', '2'], ['3', '3']],
    [['0', '2'], ['0', '3'], ['1', '1'], ['1', '2'], ['3', '0'], ['3', '2']],
    [['0', '2'], ['0', '3'], ['2', '0'], ['2', '1'], ['3', '1'], ['3', '3']],
    [['0', '1'], ['0', '3'], ['1', '2'], ['1', '3'], ['2', '2'], ['3', '1']],
    [['0', '0'], ['1', '0'], ['2', '2'], ['2', '3'], ['3', '1'], ['3', '3']],
    [['0', '0'], ['0', '1'], ['1', '2'], ['2', '0'], ['3', '1'], ['3', '2']],
    [['0', '1'], ['0', '2'], ['1', '0'], ['1', '3'], ['3', '0'], ['3', '1']],
    [['0', '0'], ['0', '2'], ['1', '0'], ['1', '3'], ['2', '1'], ['2', '2']],
    [['0', '0'], ['0', '1'], ['0', '3'], ['1', '0'], ['2', '1'], ['3', '3']],
    [['0', '0'], ['0', '3'], ['1', '1'], ['1', '3'], ['2', '0'], ['2', '2']],
    [['0', '1'], ['1', '3'], ['2', '0'], ['2', '1'], ['2', '3'], ['3', '0']],
    [['0', '0'], ['1', '1'], ['2', '0'], ['2', '3'], ['3', '1'], ['3', '2']], # answer: 13
    [['0', '0'], ['0', '3'], ['1', '2'], ['2', '2'], ['3', '1'], ['3', '3']],
    [['0', '2'], ['0', '3'], ['1', '0'], ['1', '2'], ['2', '1'], ['2', '2']]]
prob3 = \
    [[['0', '2'], ['0', '3'], ['1', '1'], ['2', '0'], ['3', '0'], ['3', '1']],
    [['0', '1'], ['0', '3'], ['2', '0'], ['2', '2'], ['3', '0'], ['3', '1']],
    [['0', '0'], ['0', '3'], ['1', '1'], ['1', '3'], ['2', '2'], ['2', '3']],
    [['0', '2'], ['0', '3'], ['1', '0'], ['1', '1'], ['2', '3'], ['3', '1']], # answer: 3
    [['0', '1'], ['0', '2'], ['1', '0'], ['2', '0'], ['2', '3'], ['3', '3']],
    [['0', '3'], ['1', '0'], ['1', '2'], ['2', '1'], ['2', '2'], ['3', '3']],
    [['0', '1'], ['0', '3'], ['2', '0'], ['2', '3'], ['3', '2'], ['3', '3']],
    [['1', '0'], ['1', '1'], ['2', '1'], ['2', '3'], ['3', '2'], ['3', '3']],
    [['0', '1'], ['0', '2'], ['1', '0'], ['1', '3'], ['2', '3'], ['3', '0']],
    [['0', '0'], ['1', '1'], ['1', '3'], ['2', '0'], ['3', '2'], ['3', '3']],
    [['0', '1'], ['0', '2'], ['1', '3'], ['2', '0'], ['3', '0'], ['3', '3']],
    [['0', '0'], ['0', '1'], ['2', '0'], ['2', '3'], ['3', '2'], ['3', '3']],
    [['0', '3'], ['1', '0'], ['1', '2'], ['2', '2'], ['3', '0'], ['3', '3']],
    [['0', '0'], ['0', '3'], ['1', '0'], ['1', '1'], ['2', '0'], ['2', '2']],
    [['0', '1'], ['0', '3'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '2']],
    [['0', '2'], ['0', '3'], ['1', '3'], ['2', '0'], ['2', '2'], ['3', '0']]]


def week3_ans_func(problem_set):
    address = QuantumRegister(4)
    data = QuantumRegister(6) # is each star corresponding to one permutation?
    shots = QuantumRegister(8) # row and col
    oracle = QuantumRegister(1)
    aux = QuantumRegister(9)
    solution = ClassicalRegister(4)
    #solution = ClassicalRegister(6) # perm
    #solution = ClassicalRegister(2) # adder
    #solution = ClassicalRegister(5) # is_count4, inv_is_count4
    #solution = ClassicalRegister(9) # store_asteroids
    #solution = ClassicalRegister(12) # oracle
    qc = QuantumCircuit(address, data, shots, oracle, aux, solution)

    # answer -------------------------------------------------------------------
    # initialize
    qc.h(address)
    qc.h(shots)
    qc.x(oracle)
    qc.h(oracle)

    for i in range(1):
        outer_phase_oracle(qc, address, data, shots, oracle, aux, problem_set)
        outer_diffusion(qc, address, aux)

    qc.measure(address, solution)
    # answer: addr == 10 (0b1010)

    return qc
