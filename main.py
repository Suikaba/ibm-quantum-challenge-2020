import math

def qor(qc, a, b, c):
    qc.x(a)
    qc.x(b)
    qc.ccx(a, b, c)
    qc.x(c)
    qc.x(a)
    qc.x(b)


def adder2(qc, s, x, c):
    qc.ccx(x, s[0], c)
    qc.cx(c, s[1])
    qc.ccx(x, s[0], c)
    qc.cx(x, s[0])

def inv_adder2(qc, s, x, c):
    qc.cx(x, s[0])
    qc.ccx(x, s[0], c)
    qc.cx(c, s[1])
    qc.ccx(x, s[0], c)


def counter3(qc, shots, s, c):
    for i in range(7):
        adder2(qc, s, shots[i+1], c)

def inv_counter3(qc, shots, s, c):
    for i in reversed(range(7)):
        inv_adder2(qc, s, shots[i+1], c)

def is_count3(qc, shots, out, aux):
    assert len(aux) >= 6
    s = [shots[0], aux[0]]
    qc.mct(shots[0:4], aux[1], aux[2:], mode='basic')
    qc.mct(shots[4:8], aux[2], aux[3:], mode='basic')
    qc.x([aux[1], aux[2]])
    qc.ccx(aux[1], aux[2], aux[3])
    counter3(qc, shots, s, aux[4])
    qc.mct([aux[3], s[0], s[1]], out, aux[5:])
    inv_counter3(qc, shots, s, aux[4])
    qc.ccx(aux[1], aux[2], aux[3])
    qc.x([aux[1], aux[2]])
    qc.mct(shots[4:8], aux[2], aux[3:], mode='basic')
    qc.mct(shots[0:4], aux[1], aux[2:], mode='basic')

def store_asteroids(qc, addr, data, shots, aux, asteroids):
    qc.mct(addr, aux[0], aux[1:], mode='basic')
    for i in range(6):
        r, c = int(asteroids[i][0]), int(asteroids[i][1])
        qor(qc, shots[r], shots[4+c], aux[1])
        qc.rccx(aux[0], aux[1], data[i])
        qor(qc, shots[r], shots[4+c], aux[1])
    qc.mct(addr, aux[0], aux[1:], mode='basic')


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
    qc.mct(data, aux[2], aux[3:], mode='basic')

    qc.ccx(aux[0], aux[2], oracle)

    qc.mct(data, aux[2], aux[3:], mode='basic')
    is_count3(qc, shots, aux[0], aux[1:])
    store_data(qc, addr, data, shots, aux, problem_set)


def inner_diffusion(qc, addr, shots, aux):
    #tmp = addr[:]
    tmp = shots[:]
    qc.h(tmp)
    qc.x(tmp)
    qc.h(tmp[7])
    qc.mct(tmp[0:7], tmp[7], aux, mode='basic')
    qc.h(tmp[7])
    qc.x(tmp)
    qc.h(tmp)

inner_iter_cnt = 11
def inner_grover(qc, addr, data, shots, oracle, aux, problem_set):
    for i in range(inner_iter_cnt):
        inner_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set)
        inner_diffusion(qc, addr, shots, aux)

def inv_inner_grover(qc, addr, data, shots, oracle, aux, problem_set):
    for i in range(inner_iter_cnt):
        inner_diffusion(qc, addr, shots, aux)
        inner_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set)

def outer_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set):
    s = [shots[0], aux[0]]
    inner_grover(qc, addr, data, shots, oracle, aux, problem_set)
    counter3(qc, shots, s, aux[1])

    qc.ccx(s[0], s[1], oracle)

    inv_counter3(qc, shots, s, aux[1])
    inv_inner_grover(qc, addr, data, shots, oracle, aux, problem_set)

def outer_diffusion(qc, addr, shots, aux):
    tmp = addr[:]
    #tmp = shots[:]
    qc.h(tmp)
    qc.x(tmp)
    qc.h(tmp[3])
    qc.mct(tmp[0:3], tmp[3], aux, mode='basic')
    qc.h(tmp[3])
    qc.x(tmp)
    qc.h(tmp)


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
    solution = ClassicalRegister(4) # answer
    #solution = ClassicalRegister(2) # adder
    #solution = ClassicalRegister(5) # is_count4, inv_is_count4
    #solution = ClassicalRegister(10) # store_asteroids
    #solution = ClassicalRegister(12) # inner grover
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
        outer_diffusion(qc, address, data, aux)

    qc.measure([address[3], address[2], address[1], address[0]], solution)

    # test store_data ----------------------------------------------------------
    #qc.h(address)
    #qc.x([shots[0], shots[1], shots[4]])

    #store_data(qc, address, data, shots, aux, problem_set)

    #qc.measure(data, solution[0:6])
    #qc.measure([address[3], address[2], address[1], address[0]], solution[6:10])

    # test inner grover --------------------------------------------------------
    #qc.h(address)
    #qc.h(shots)
    #qc.x(oracle)
    #qc.h(oracle)

    ##store_data(qc, address, data, shots, aux, problem_set)
    #inner_grover(qc, address, data, shots, oracle, aux, problem_set)

    #qc.measure(shots, solution[0:8])
    #qc.measure([address[3], address[2], address[1], address[0]], solution[8:12])

    # test oracle --------------------------------------------------------------
    #qc.h(address)
    #qc.h(shots)
    #qc.x(oracle)
    #qc.h(oracle)

    #for i in range(1):
    #    outer_phase_oracle(qc, address, data, shots, oracle, aux, problem_set)
    #    outer_diffusion(qc, address, shots, aux)

    ##qc.measure(shots, solution[0:8])
    #qc.measure([address[3], address[2], address[1], address[0]], solution[8:12])

    return qc


# for test
#qc = week3_ans_func(prob1)
#
#job = execute(qc, backend=backend, shots=1000, seed_simulator=12345, backend_options={"fusion_enable":True})
#result = job.result()
#count = result.get_counts()

count
