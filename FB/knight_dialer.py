NEIGHBORS_MAP = {
    1: (6, 8),
    2: (7, 9),
    3: (4, 8),
    4: (3, 9, 0),
    5: tuple(),  # 5 has no neighbors
    6: (1, 7, 0),
    7: (2, 6),
    8: (1, 3),
    9: (2, 4),
    0: (4, 6),
}

#%% Level 1
def neighbors(position):
    return NEIGHBORS_MAP[position]


def yield_sequences(starting_position, num_hops, sequence=None):
    if sequence is None:
        sequence = [starting_position]
    
    if num_hops == 0:
        yield sequence
        return

    for neighbor in neighbors(starting_position):
        yield from yield_sequences(
            neighbor, num_hops - 1, sequence + [neighbor])


def count_sequences(starting_position, num_hops):
    num_sequences = 0
    for sequence in yield_sequences(starting_position, num_hops):
        num_sequences += 1
    return num_sequences

#%% Level 2 counting -- recursive
# from neighbors import neighbors
def count_sequences(start_position, num_hops):
    if num_hops == 0:
        return 1

    num_sequences = 0
    for position in neighbors(start_position):
        num_sequences += count_sequences(position, num_hops - 1)
    return num_sequences


if __name__ == '__main__':
    print(count_sequences(6, 2))

#%% Level 3 memoization
def count_sequences(start_position, num_hops):
    cache = {}

    def helper(position, num_hops):
        if (position, num_hops) in cache:
            return cache[ (position, num_hops) ]

        if num_hops == 0:
            return 1

        else:
            num_sequences = 0
            for neighbor in neighbors(position):
                num_sequences += helper(neighbor, num_hops - 1)
            cache[ (position, num_hops) ] = num_sequences
            return num_sequences

    res = helper(start_position, num_hops)
    return res