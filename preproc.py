
def preprocess(stars):
    board = [[] for i in range(4)]
    for pos in stars:
        r, c = int(pos[0]), int(pos[1])
        board[r].append(c)
    board.sort(key=len)
    print(board)

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

    return board

stars = [['0', '1'], ['0', '3'], ['1', '2'], ['1', '3'], ['2', '0'], ['3', '2']]
board = preprocess(stars)
print(board)
