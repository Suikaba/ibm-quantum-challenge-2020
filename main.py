def qor(qc, a, b, c):
    qc.x(a)
    qc.x(b)
    qc.ccx(a, b, c)
    qc.x(c)

def inv_qor(qc, a, b, c):
    qc.x(c)
    qc.ccx(a, b, c)
    qc.x(a)
    qc.x(b)

# 列と行単位の swap は結果に影響しない
def preprocess(stars):
    board = [[] for i in range(4)]
    for pos in stars:
        r, c = int(pos[0]), int(pos[1])
        board[r].append(c)
    board.sort(key=len)

    def swap_col(i, j):
        for r in range(4):
            for k in range(len(board[r])):
                if board[r][k] == i:
                    board[r][k] = j
                elif board[r][k] == j:
                    board[r][k] = i

    if len(board[0]) != 0:
        swap_col(0, board[0][0])
    if len(board[1]) != 0:
        swap_col(1, board[1][0])

    #print(board)
    return board

# qRAM data format:
# 0...
# .1..
# ..23
# ..45
# 星は 6 個しかないので，適切に前処理しておけば上記の部分だけ記憶するだけで十分である

# write to addr == 1111
def store_data(qc, addr, data, aux, board):
    qc.mct(addr, aux[0], aux[1:], mode='basic')
    if len(board[0]) != 0 and board[0][0] == 0:
        qc.cx(aux[0], data[0])
    if len(board[1]) != 0 and board[1][0] == 1:
        qc.cx(aux[0], data[1])
    for r in range(2, 4):
        for c in board[r]:
            if c == 2:
                qc.cx(aux[0], data[(r-1)*2])
            elif c == 3:
                qc.cx(aux[0], data[(r-1)*2+1])
    qc.mct(addr, aux[0], aux[1:], mode='basic')

# memo: gray_code
# 15, 14, 10, 11, 9, 8, 0, 1, 3, 2, 6, 7, 5, 4, 12, 13
def store_stars(qc, addr, data, aux, problem_set):
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1111]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1110]))
    qc.x(addr[1])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1010]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1011]))
    qc.x(addr[2])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1001]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1000]))
    qc.x(addr[0])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0000]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0001]))
    qc.x(addr[2])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0011]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0010]))
    qc.x(addr[1])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0110]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0111]))
    qc.x(addr[2])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0101]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b0100]))
    qc.x(addr[0])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1100]))
    qc.x(addr[3])
    store_data(qc, addr, data, aux, preprocess(problem_set[0b1101]))
    qc.x(addr[2])



def phase_oracle(qc, addr, data, perm, oracle, aux, problem_set):
    store_stars(qc, addr, data, aux, problem_set)

    qc.ccx(data[0], data[1], aux[0])
    qc.x(perm[0])
    qc.mct([perm[0], data[2], perm[1], data[5]], aux[1], aux[3:], mode='basic')
    qc.x(perm)
    qc.mct([perm[0], data[3], perm[1], data[4]], aux[2], aux[3:], mode='basic')
    qor(qc, aux[1], aux[2], aux[3])

    qc.ccx(aux[0], aux[3], oracle)

    inv_qor(qc, aux[1], aux[2], aux[3])
    qc.mct([perm[0], data[3], perm[1], data[4]], aux[2], aux[3:], mode='basic')
    qc.x(perm)
    qc.mct([perm[0], data[2], perm[1], data[5]], aux[1], aux[3:], mode='basic')
    qc.x(perm[0])
    qc.ccx(data[0], data[1], aux[0])

    store_stars(qc, addr, data, aux, problem_set)


def diffusion(qc, addr, perm, aux):
    tmp = [addr[0], addr[1], addr[2], addr[3], perm[0], perm[1]]
    qc.h(tmp)
    qc.x(tmp)
    qc.h(tmp[5])
    qc.mct(tmp[0:5], tmp[5], aux, mode='basic')
    qc.h(tmp[5])
    qc.x(tmp)
    qc.h(tmp)


def week3_ans_func(problem_set):
    # TODO: test by changing the order
    #problem_set = \
    #    [
    #    [['0', '2'], ['1', '0'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '3']],
    #    [['0', '1'], ['0', '3'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '2']], # answer
    #    [['0', '0'], ['0', '1'], ['1', '2'], ['2', '2'], ['3', '0'], ['3', '3']],
    #    [['0', '0'], ['1', '1'], ['1', '3'], ['2', '0'], ['3', '2'], ['3', '3']],
    #    [['0', '0'], ['0', '1'], ['1', '1'], ['1', '3'], ['3', '2'], ['3', '3']],
    #    [['0', '2'], ['1', '0'], ['1', '3'], ['2', '0'], ['3', '2'], ['3', '3']],
    #    [['1', '1'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '1'], ['3', '3']],
    #    [['0', '2'], ['0', '3'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '3']],
    #    [['0', '0'], ['0', '3'], ['1', '2'], ['2', '2'], ['2', '3'], ['3', '0']],
    #    [['0', '3'], ['1', '1'], ['1', '2'], ['2', '0'], ['2', '1'], ['3', '3']],
    #    [['0', '0'], ['0', '1'], ['1', '3'], ['2', '1'], ['2', '3'], ['3', '0']],
    #    [['0', '0'], ['1', '3'], ['2', '0'], ['2', '1'], ['2', '3'], ['3', '1']],
    #    [['0', '1'], ['0', '2'], ['1', '0'], ['1', '2'], ['2', '2'], ['2', '3']],
    #    [['0', '3'], ['1', '0'], ['1', '3'], ['2', '1'], ['2', '2'], ['3', '0']],
    #    [['0', '2'], ['0', '3'], ['1', '2'], ['2', '3'], ['3', '0'], ['3', '1']],
    #    [['0', '1'], ['1', '0'], ['1', '2'], ['2', '2'], ['3', '0'], ['3', '1']],
    #    ]

    address = QuantumRegister(4)
    data = QuantumRegister(6) # board data
    perm = QuantumRegister(2) # right below
    oracle = QuantumRegister(1)
    aux = QuantumRegister(15)
    solution = ClassicalRegister(4)
    #solution = ClassicalRegister(7)
    qc = QuantumCircuit(address, data, perm, oracle, aux, solution)

    # answer -------------------------------------------------------------------
    # initialize
    # create |01> + |10>
    qc.h(perm[0])
    qc.cx(perm[0], perm[1])
    qc.x(perm[0])
    qc.h(address)
    qc.x(oracle)
    qc.h(oracle)

    for i in range(1):
        phase_oracle(qc, address, data, perm, oracle, aux, problem_set)
        diffusion(qc, address, perm, aux)

    qc.measure(address, solution)
    qc.reverse_bits()
    # answer: addr == 10 (0b1010)

    # test oracle
    #qc.h(perm[0])
    #qc.cx(perm[0], perm[1])
    #qc.x(perm[0])
    #qc.h(address)

    #store_data(qc, address, data, aux, preprocess(problem_set[1]))
    #qc.x(perm[0])
    #qc.mct([perm[0], data[2], perm[1], data[5]], aux[0])
    #qc.x(perm)
    #qc.mct([perm[0], data[3], perm[1], data[4]], aux[1])
    #qor(qc, aux[0], aux[1], oracle)

    #qc.measure(data, solution[0:6])
    #qc.measure(oracle, solution[6])

    return qc
