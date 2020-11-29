def qor(qc, a, b, c):
    qc.x(a)
    qc.x(b)
    qc.ccx(a, b, c)
    qc.x(c)
    qc.x(a)
    qc.x(b)

def rqor(qc, a, b, c):
    qc.x(a)
    qc.x(b)
    qc.rccx(a, b, c)
    qc.x(c)
    qc.x(a)
    qc.x(b)

def rqor_dirty(qc, a, b, c):
    qc.x(a)
    qc.x(b)
    qc.rccx(a, b, c)
    qc.x(c)

def inv_rqor_dirty(qc, a, b, c):
    qc.x(c)
    qc.rccx(a, b, c)
    qc.x(b)
    qc.x(a)


def adder2(qc, s, x, c):
    qc.rccx(x, s[0], c)
    qc.cx(c, s[1])
    qc.rccx(x, s[0], c)
    qc.cx(x, s[0])

def adder2_ovf(qc, s, x, c, ovf):
    qc.rccx(x, s[0], c)
    qc.rccx(c, s[1], ovf)
    qc.cx(c, s[1])
    qc.rccx(x, s[0], c)
    qc.cx(x, s[0])

def adder2_dirty(qc, s, x, c):
    qc.rccx(x, s[0], c)
    qc.cx(c, s[1])
    #qc.rccx(x, s[0], c)
    qc.cx(x, s[0])

def adder2_dirty_ovf(qc, s, x, c, ovf):
    qc.rccx(x, s[0], c)
    qc.rccx(c, s[1], ovf)
    qc.cx(c, s[1])
    qc.cx(x, s[0])

def inv_adder2(qc, s, x, c):
    qc.cx(x, s[0])
    qc.rccx(x, s[0], c)
    qc.cx(c, s[1])
    qc.rccx(x, s[0], c)

def inv_adder2_ovf(qc, s, x, c, ovf):
    qc.cx(x, s[0])
    qc.rccx(x, s[0], c)
    qc.cx(c, s[1])
    qc.rccx(c, s[1], ovf)
    qc.rccx(x, s[0], c)

def inv_adder2_dirty(qc, s, x, c):
    qc.cx(x, s[0])
    #qc.rccx(x, s[0], c)
    qc.cx(c, s[1])
    qc.rccx(x, s[0], c)

def inv_adder2_dirty_ovf(qc, s, x, c, ovf):
    qc.cx(x, s[0])
    qc.cx(c, s[1])
    qc.rccx(c, s[1], ovf)
    qc.rccx(x, s[0], c)


def counter3(qc, shots, s, c):
    for i in range(7):
        adder2(qc, s, shots[i+1], c)

def inv_counter3(qc, shots, s, c):
    for i in reversed(range(7)):
        inv_adder2(qc, s, shots[i+1], c)


def is_count3_dirty(qc, shots, out, aux):
    assert len(aux) >= 7
    s = [shots[0], aux[0]]
    ovf = aux[1]
    adder2(qc, s, shots[1], aux[2])
    adder2(qc, s, shots[2], aux[2])
    adder2_ovf(qc, s, shots[3], aux[2], ovf)
    adder2_dirty_ovf(qc, s, shots[4], aux[2], ovf)
    adder2_dirty_ovf(qc, s, shots[5], aux[3], ovf)
    adder2_dirty_ovf(qc, s, shots[6], aux[4], ovf)
    adder2_dirty_ovf(qc, s, shots[7], aux[5], ovf)
    qc.x(ovf)
    qc.mct([ovf, s[0], s[1]], out, aux[6], mode='basic')

def inv_is_count3_dirty(qc, shots, out, aux):
    assert len(aux) >= 7
    s = [shots[0], aux[0]]
    ovf = aux[1]
    qc.mct([ovf, s[0], s[1]], out, aux[6], mode='basic')
    qc.x(ovf)
    inv_adder2_dirty_ovf(qc, s, shots[7], aux[5], ovf)
    inv_adder2_dirty_ovf(qc, s, shots[6], aux[4], ovf)
    inv_adder2_dirty_ovf(qc, s, shots[5], aux[3], ovf)
    inv_adder2_dirty_ovf(qc, s, shots[4], aux[2], ovf)
    inv_adder2_ovf(qc, s, shots[3], aux[2], ovf)
    inv_adder2(qc, s, shots[2], aux[2])
    inv_adder2(qc, s, shots[1], aux[2])


def opt_is_count3(qc, shots, out, aux):
    s = [shots[0], aux[0]]
    ovf = aux[1]
    adder2(qc, s, shots[1], aux[2])
    adder2_dirty(qc, s, shots[2], aux[2])
    # s[0] and s[1] となりつつ ovf に xor されるのは高々1回であるためこれでよい
    adder2_dirty_ovf(qc, s, shots[3], aux[3], ovf)
    adder2_dirty_ovf(qc, s, shots[4], aux[4], ovf)
    adder2_dirty_ovf(qc, s, shots[5], aux[5], ovf)
    adder2_dirty_ovf(qc, s, shots[6], aux[6], ovf)
    adder2_dirty_ovf(qc, s, shots[7], aux[7], ovf)
    qc.x(ovf)
    qc.rccx(ovf, s[0], aux[8])
    qc.ccx(aux[8], s[1], out)
    qc.rccx(ovf, s[0], aux[8])
    qc.x(ovf)
    inv_adder2_dirty_ovf(qc, s, shots[7], aux[7], ovf)
    inv_adder2_dirty_ovf(qc, s, shots[6], aux[6], ovf)
    inv_adder2_dirty_ovf(qc, s, shots[5], aux[5], ovf)
    inv_adder2_dirty_ovf(qc, s, shots[4], aux[4], ovf)
    inv_adder2_dirty_ovf(qc, s, shots[3], aux[3], ovf)
    inv_adder2_dirty(qc, s, shots[2], aux[2])
    inv_adder2(qc, s, shots[1], aux[2])


def store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux, asteroids):
    for i in range(6):
        r, c = int(asteroids[i][0]), int(asteroids[i][1])
        if r == 0 and c == 0:
            qc.rccx(addr_f, cache_00, data[i])
        elif r == 0 and c == 1:
            qc.rccx(addr_f, cache_01, data[i])
        else:
            rqor_dirty(qc, shots[r], shots[4+c], aux)
            qc.rccx(addr_f, aux, data[i])
            inv_rqor_dirty(qc, shots[r], shots[4+c], aux)


def store_data(qc, addr, data, shots, aux, problem_set):
    cache_addr_lo = aux[0:4]
    cache_addr_hi = aux[4]
    addr_f = aux[5]
    aux_store = aux[6]
    cache_00 = aux[7]
    cache_01 = aux[8]

    qc.rccx(addr[2], addr[3], cache_addr_lo[0b11])
    qc.x(addr[2])
    qc.rccx(addr[2], addr[3], cache_addr_lo[0b01])
    qc.x(addr[3])
    qc.rccx(addr[2], addr[3], cache_addr_lo[0b00])
    qc.x(addr[2])
    qc.rccx(addr[2], addr[3], cache_addr_lo[0b10])
    qc.x(addr[3])

    rqor(qc, shots[0], shots[4], cache_00)
    rqor(qc, shots[0], shots[5], cache_01)


    qc.rccx(addr[0], addr[1], cache_addr_hi)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1111])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1110])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1100])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1101])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)

    qc.rccx(addr[0], addr[1], cache_addr_hi)


    qc.x(addr[1])
    qc.rccx(addr[0], addr[1], cache_addr_hi)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1010])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1011])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1001])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b1000])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)

    qc.rccx(addr[0], addr[1], cache_addr_hi)


    qc.x(addr[0])
    qc.rccx(addr[0], addr[1], cache_addr_hi)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0000])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0001])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0011])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0010])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)

    qc.rccx(addr[0], addr[1], cache_addr_hi)


    qc.x(addr[1])
    qc.rccx(addr[0], addr[1], cache_addr_hi)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0110])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b10], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0111])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b11], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0101])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b01], addr_f)

    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)
    store_asteroids(qc, addr_f, data, shots, cache_00, cache_01, aux_store, problem_set[0b0100])
    qc.rccx(cache_addr_hi, cache_addr_lo[0b00], addr_f)

    qc.rccx(addr[0], addr[1], cache_addr_hi)
    qc.x(addr[0])


    rqor(qc, shots[0], shots[5], cache_01)
    rqor(qc, shots[0], shots[4], cache_00)

    qc.rccx(addr[2], addr[3], cache_addr_lo[0b11])
    qc.x(addr[2])
    qc.rccx(addr[2], addr[3], cache_addr_lo[0b01])
    qc.x(addr[3])
    qc.rccx(addr[2], addr[3], cache_addr_lo[0b00])
    qc.x(addr[2])
    qc.rccx(addr[2], addr[3], cache_addr_lo[0b10])
    qc.x(addr[3])


# 3発のやつだけとりあえず選んでおく
# これだけなら qRAM いらんので比較的高速にできてうれしい
def inner_phase_oracle_1(qc, shots, oracle, aux):
    opt_is_count3(qc, shots, oracle, aux)

def inner_diffusion_1(qc, shots, aux):
    qc.h(shots)
    qc.x(shots)
    qc.h(shots[7])
    qc.mct(shots[0:7], shots[7], aux, mode='basic')
    qc.h(shots[7])
    qc.x(shots)
    qc.h(shots)

inner_cnt_1 = 1
def inner_grover_1(qc, shots, oracle, aux):
    for i in range(inner_cnt_1):
        inner_phase_oracle_1(qc, shots, oracle, aux)
        inner_diffusion_1(qc, shots, aux)

def inv_inner_grover_1(qc, shots, oracle, aux):
    for i in range(inner_cnt_1):
        inner_diffusion_1(qc, shots, aux)
        inner_phase_oracle_1(qc, shots, oracle, aux)


def inner_phase_oracle_2(qc, addr, data, shots, oracle, aux, problem_set):
    inner_grover_1(qc, shots, oracle, aux)
    store_data(qc, addr, data, shots, aux, problem_set)
    qc.mct(data, aux[0], aux[1:], mode='basic')
    is_count3_dirty(qc, shots, aux[1], aux[2:])

    qc.ccx(aux[0], aux[1], oracle)

    inv_is_count3_dirty(qc, shots, aux[1], aux[2:])
    qc.mct(data, aux[0], aux[1:], mode='basic')
    store_data(qc, addr, data, shots, aux, problem_set)
    inv_inner_grover_1(qc, shots, oracle, aux)


def inner_diffusion_2(qc, addr, shots, aux):
    qc.h(shots)
    qc.x(shots)
    qc.h(shots[7])
    qc.mct(shots[0:7], shots[7], aux, mode='basic')
    qc.h(shots[7])
    qc.x(shots)
    qc.h(shots)

inner_cnt_2 = 4 # must >= 4
def inner_grover_2(qc, addr, data, shots, oracle, aux, problem_set):
    for i in range(inner_cnt_2):
        inner_phase_oracle_2(qc, addr, data, shots, oracle, aux, problem_set)
        inner_diffusion_2(qc, addr, shots, aux)

def inv_inner_grover_2(qc, addr, data, shots, oracle, aux, problem_set):
    for i in range(inner_cnt_2):
        inner_diffusion_2(qc, addr, shots, aux)
        inner_phase_oracle_2(qc, addr, data, shots, oracle, aux, problem_set)


def outer_phase_oracle(qc, addr, data, shots, oracle, aux, problem_set):
    inner_grover_2(qc, addr, data, shots, oracle, aux, problem_set)

    opt_is_count3(qc, shots, oracle, aux)

    inv_inner_grover_2(qc, addr, data, shots, oracle, aux, problem_set)

def outer_diffusion(qc, addr, shots, aux):
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
    solution = ClassicalRegister(4) # answer
    #solution = ClassicalRegister(2) # adder
    #solution = ClassicalRegister(5) # is_count4, inv_is_count4
    #solution = ClassicalRegister(10) # store_asteroids
    #solution = ClassicalRegister(12) # inner_grover 1, 2, 1 and 2
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

    qc.measure([address[0], address[1], address[2], address[3]], solution)

    # test store_data ----------------------------------------------------------
    #qc.h(address)
    #qc.x([shots[0], shots[1], shots[4]])

    #store_data(qc, address, data, shots, aux, problem_set)

    #qc.measure(data, solution[0:6])
    #qc.measure([address[3], address[2], address[1], address[0]], solution[6:10])

    # test inner_grover_1 --------------------------------------------------------
    #qc.h(address)
    #qc.h(shots)
    #qc.x(oracle)
    #qc.h(oracle)

    #inner_grover_1(qc, shots, oracle, aux)

    #qc.measure(shots, solution[0:8])

    # test inner_grover_2 --------------------------------------------------------
    #qc.h(address)
    #qc.h(shots)
    #qc.x(oracle)
    #qc.h(oracle)

    #inner_grover_2(qc, address, data, shots, oracle, aux, problem_set)

    #qc.measure(shots, solution[0:8])
    #qc.measure([address[3], address[2], address[1], address[0]], solution[8:12])


    return qc


# for test
#qc = week3_ans_func(prob3)
#
#job = execute(qc, backend=backend, shots=1000, seed_simulator=12345, backend_options={"fusion_enable":True})
#result = job.result()
#count = result.get_counts()
#
#count
