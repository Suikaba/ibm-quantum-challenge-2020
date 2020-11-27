def q_or(qc, a, b, out): # itself inv
    qc.cx(a, out)
    qc.cx(b, out)
    qc.ccx(a, b, out)

def phase_oracle_2a(qc, light, flip, oracle, ancillae):
    def proc():
        di = [0, 1, 0, -1]
        dj = [1, 0, -1, 0]
        qc.x(light)
        for i in range(3):
            for j in range(3):
                qc.cx(flip[i * 3 + j], light[i * 3 + j])
                for dir in range(4):
                    ii, jj = i + di[dir], j + dj[dir]
                    if ii < 0 or 3 <= ii or jj < 0 or 3 <= jj:
                        continue
                    qc.cx(flip[i * 3 + j], light[ii * 3 + jj])
    proc()
    qc.mct(light, oracle, ancillae, mode='basic')
    proc() # inverse
    
def diffusion_2a(qc, light, flip, oracle, ancillae):
    qc.h(flip)
    qc.x(flip)
    qc.h(flip[8])
    qc.mct(flip[0:8], flip[8], ancillae, mode='basic')
    qc.h(flip[8])
    qc.x(flip)
    qc.h(flip)
    
# oracle is clean after call
# assume: oracle <- x, h
iter_cnt = 17
def unitary_2a(qc, light, flip, oracle, ancillae):
    for i in range(iter_cnt):
        phase_oracle_2a(qc, light, flip, oracle, ancillae)
        diffusion_2a(qc, light, flip, oracle, ancillae)

def inv_unitary_2a(qc, light, flip, oracle, ancillae):
    for i in range(iter_cnt):
        diffusion_2a(qc, light, flip, oracle, ancillae)
        phase_oracle_2a(qc, light, flip, oracle, ancillae)
        

# write lights to addr == 0b11
def store_lights(qc, addr, data, lights):
    for i in range(9):
        if lights[i] == 1:
            qc.ccx(addr[0], addr[1], data[i])


def store_lightout4(qc, addr, data, lightout4):
    store_lights(qc, addr, data, lightout4[3])
    qc.x(addr[0])
    store_lights(qc, addr, data, lightout4[2])
    qc.x(addr[1])
    store_lights(qc, addr, data, lightout4[0])
    qc.x(addr[0])
    store_lights(qc, addr, data, lightout4[1])
    qc.x(addr[1])


# addr of 4bit (s : 4bit, x : 1bit, carry (ancillae) : 3bit, s = s + x)
def adder(qc, s, x, c):
    qc.ccx(x, s[0], c[0])
    qc.ccx(c[0], s[1], c[1])
    qc.ccx(c[1], s[2], c[2])
    qc.cx(c[2], s[3])
    qc.ccx(c[1], s[2], c[2])
    qc.cx(c[1], s[2])
    qc.ccx(c[0], s[1], c[1])
    qc.cx(c[0], s[1])
    qc.ccx(x, s[0], c[0])
    qc.cx(x, s[0])

def inv_adder(qc, s, x, c):
    qc.cx(x, s[0])
    qc.ccx(x, s[0], c[0])
    qc.cx(c[0], s[1])
    qc.ccx(c[0], s[1], c[1])
    qc.cx(c[1], s[2])
    qc.ccx(c[1], s[2], c[2])
    qc.cx(c[2], s[3])
    qc.ccx(c[1], s[2], c[2])
    qc.ccx(c[0], s[1], c[1])
    qc.ccx(x, s[0], c[0])
    
# if popcnt(xs) <= 3 -> out = 1
def counter(qc, xs, out, ancillae):
    s = [xs[0], ancillae[0], ancillae[1], ancillae[2]]
    for i in range(8):
        adder(qc, s, xs[i + 1], ancillae[3:])
    q_or(qc, s[2], s[3], out)
    qc.x(out)
    for i in reversed(range(8)):
        inv_adder(qc, s, xs[i + 1], ancillae[3:])
        
    
def phase_oracle(qc, addr, data, flip, oracle, ancillae, lightout4):
    store_lightout4(qc, addr, data, lightout4)
    unitary_2a(qc, data, flip, oracle, ancillae)
    
    counter(qc, flip, oracle, ancillae[0:6])
    
    # inverse
    inv_unitary_2a(qc, data, flip, oracle, ancillae)
    store_lightout4(qc, addr, data, lightout4)
                

def diffusion(qc, addr):
    qc.h(addr)
    qc.x(addr)
    qc.h(addr[1])
    qc.cx(addr[0], addr[1])
    qc.h(addr[1])
    qc.x(addr)
    qc.h(addr)

def week2b_ans_func(lightout4):
    address = QuantumRegister(2)
    data = QuantumRegister(9)
    flip = QuantumRegister(9)
    oracle = QuantumRegister(1)
    ancillae = QuantumRegister(7)
    solution = ClassicalRegister(2)
    qc = QuantumCircuit(address, data, flip, oracle, ancillae, solution)
    
    qc.h(address)
    qc.h(flip)
    qc.x(oracle)
    qc.h(oracle)
    
    phase_oracle(qc, address, data, flip, oracle[0], ancillae, lightout4)
    diffusion(qc, address)
    
    qc.h(oracle)
    qc.x(oracle)
    qc.measure(address, solution)
    qc.reverse_bits()
    
    return qc
