def ToyInstance():

    nodes = {}
    for j in range(6):
        for i in range(6):
            nodes[len(nodes)] = (i, j)

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5),
        (1, 0), (2, 1), (3, 2), (4, 3), (5, 4),
        (6, 7), (7, 8), (8, 9), (9, 10), (10, 11),
        (7, 6), (8, 7), (9, 8), (10, 9), (11, 10),
        (12, 13), (13, 14), (14, 15), (15, 16), (16, 17),
        (13, 12), (14, 13), (15, 14), (16, 15), (17, 16),
        (18, 19), (19, 20), (20, 21), (21, 22), (22, 23),
        (19, 18), (20, 19), (21, 20), (22, 21), (23, 22),
        (24, 25), (25, 26), (26, 27), (27, 28), (28, 29),
        (25, 24), (26, 25), (27, 26), (28, 27), (29, 28),
        (30, 31), (31, 32), (32, 33), (33, 34), (34, 35),
        (31, 30), (32, 31), (33, 32), (34, 33), (35, 34),
        (0, 6), (6, 12), (12, 18), (18, 24), (24, 30),
        (6, 0), (12, 6), (18, 12), (24, 18), (30, 24),
        (1, 7), (7, 13), (13, 19), (19, 25), (25, 31),
        (7, 1), (13, 7), (19, 13), (25, 19), (31, 25),
        (2, 8), (8, 14), (14, 20), (20, 26), (26, 32),
        (8, 2), (14, 8), (20, 14), (26, 20), (32, 26),
        (3, 9), (9, 15), (15, 21), (21, 27), (27, 33),
        (9, 3), (15, 9), (21, 15), (27, 21), (33, 27),
        (4, 10), (10, 16), (16, 22), (22, 28), (28, 34),
        (10, 4), (16, 10), (22, 16), (28, 22), (34, 28),
        (5, 11), (11, 17), (17, 23), (23, 29), (29, 35),
        (11, 5), (17, 11), (23, 17), (29, 23), (35, 29)
    ]

    length = {
        (0, 1):5, (1, 2):5, (2, 3):4, (3, 4):5, (4, 5):4,
        (1, 0):7, (2, 1):8, (3, 2):6, (4, 3):8, (5, 4):8,
        (6, 7):6, (7, 8):4, (8, 9):5, (9, 10):6, (10, 11):6,
        (7, 6):6, (8, 7):6, (9, 8):8, (10, 9):6, (11, 10):8,
        (12, 13):5, (13, 14):6, (14, 15):5, (15, 16):4, (16, 17):5,
        (13, 12):7, (14, 13):8, (15, 14):7, (16, 15):7, (17, 16):6,
        (18, 19):6, (19, 20):4, (20, 21):5, (21, 22):4, (22, 23):4,
        (19, 18):7, (20, 19):7, (21, 20):8, (22, 21):8, (23, 22):8,
        (24, 25):6, (25, 26):4, (26, 27):4, (27, 28):6, (28, 29):5,
        (25, 24):7, (26, 25):7, (27, 26):8, (28, 27):7, (29, 28):6,
        (30, 31):6, (31, 32):6, (32, 33):6, (33, 34):4, (34, 35):4,
        (31, 30):8, (32, 31):8, (33, 32):6, (34, 33):8, (35, 34):7,
        (0, 6):3, (6, 12):4, (12, 18):2, (18, 24):4, (24, 30):3,
        (6, 0):8, (12, 6):8, (18, 12):8, (24, 18):9, (30, 24):8,
        (1, 7):2, (7, 13):2, (13, 19):2, (19, 25):3, (25, 31):3,
        (7, 1):8, (13, 7):8, (19, 13):7, (25, 19):8, (31, 25):9,
        (2, 8):4, (8, 14):2, (14, 20):2, (20, 26):3, (26, 32):4,
        (8, 2):8, (14, 8):9, (20, 14):9, (26, 20):8, (32, 26):9,
        (3, 9):3, (9, 15):4, (15, 21):3, (21, 27):4, (27, 33):4,
        (9, 3):7, (15, 9):7, (21, 15):7, (27, 21):7, (33, 27):9,
        (4, 10):4, (10, 16):4, (16, 22):3, (22, 28):2, (28, 34):4,
        (10, 4):8, (16, 10):9, (22, 16):9, (28, 22):9, (34, 28):7,
        (5, 11):3, (11, 17):4, (17, 23):2, (23, 29):3, (29, 35):3,
        (11, 5):9, (17, 11):7, (23, 17):9, (29, 23):7, (35, 29):9
    }

    return nodes, edges, length