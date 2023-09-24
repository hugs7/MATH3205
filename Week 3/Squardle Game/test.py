def get_alphabet_indices(letter):
    # Assuming Alphabet is "abcdefghijklmnopqrstuvwxyz"
    return Alphabet.index(letter.lower())


def get_alphabet_indices_pairs(grid):
    rows = len(grid)
    cols = len(grid[0])
    alphabet_indices_pairs = []

    # Horizontal pairs
    for row in grid:
        for i in range(cols - 1):
            index1 = get_alphabet_indices(row[i])
            index2 = get_alphabet_indices(row[i + 1])
            alphabet_indices_pairs.append((index1, index2))

    # Vertical pairs
    for col in range(cols):
        for i in range(rows - 1):
            index1 = get_alphabet_indices(grid[i][col])
            index2 = get_alphabet_indices(grid[i + 1][col])
            alphabet_indices_pairs.append((index1, index2))

    # Diagonal pairs (top-left to bottom-right)
    for row in range(rows - 1):
        for col in range(cols - 1):
            index1 = get_alphabet_indices(grid[row][col])
            index2 = get_alphabet_indices(grid[row + 1][col + 1])
            alphabet_indices_pairs.append((index1, index2))

    # Diagonal pairs (top-right to bottom-left)
    for row in range(rows - 1):
        for col in range(1, cols):
            index1 = get_alphabet_indices(grid[row][col])
            index2 = get_alphabet_indices(grid[row + 1][col - 1])
            alphabet_indices_pairs.append((index1, index2))

    return alphabet_indices_pairs


# Example usage:
Alphabet = "abcdefghijklmnopqrstuvwxyz"
grid = [
    ["A", "B", "C", "D"],
    ["E", "F", "G", "H"],
    ["I", "J", "K", "L"],
    ["M", "N", "O", "P"],
]

pairs = get_alphabet_indices_pairs(grid)
for pair in pairs:
    print(pair)
