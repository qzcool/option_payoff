# coding=utf-8
"""..."""
import math


def test(data):
    res = []
    for sub_data in data:
        real = [item for item in sub_data if item]

        step = 1
        for num in sub_data[sub_data.index(real[0]) + 1:]:
            if num:
                break
            step += 1

        tail = 0
        while tail < step:
            if sub_data[- (tail + 1)]:
                break
            tail += 1

        output = [None] * (step * 2 + sub_data.index(real[0]))
        for i in range(2, len(real)):
            ans = (real[i] - 2 * real[i - 1] + real[i - 2]) / step / step
            output.extend([ans] + [None] * (step - 1))
        res.append(output[: - (step - 1)] + [None] * tail)

    return res


def test2(num):
    res = 0
    for n in range(3, num, 2):
        if num % n == 0 and num / n >= (n + 1) / 2:
            res += 1
    for n in range(2, num, 2):
        if num / n - num // n == 0.5 and num / n >= (n + 1) / 2:
            res += 1
    return res


def find_comp(num, threshold):
    res = []
    for i in range(threshold + 1, num + 1):
        if num % i == 0:
            res.append(i)
    return res


def judge(city1, city2, path_ref, cache):
    if city2 in cache[city1]:
        return True
    for path in path_ref[city1]:
        if path in path_ref[city2]:
            cache[city1].add(city2)
            cache[city2].add(city1)
            return True
    return False


def broad_judge(city1, city2, path_ref, city_list, black_list, cache):
    if judge(city1, city2, path_ref, cache):
        return True
    for city in set(city_list) - set(black_list):
        if judge(city1, city, path_ref, cache):
            black_list.append(city)
            if broad_judge(city, city2, path_ref, city_list, black_list, cache):
                cache[city].add(city2)
                cache[city2].add(city)
                return True
    return False


def test4(n, g, originCities, destinationCities):
    city_list = list(range(1, n + 1))
    path_ref = [[]] + [find_comp(city, g) for city in city_list]
    cache = [set() for i in range(n + 1)]

    res = []
    for i in range(len(originCities)):
        black_list = [originCities[i], destinationCities[i]]
        res.append(int(broad_judge(originCities[i], destinationCities[i], path_ref, city_list, black_list, cache)))
    return res


def test3(data):
    num_city = data.pop(0)
    threshold = data.pop(0)
    origin = data[1:int(len(data) / 2)]
    destination = data[int(len(data) / 2 + 1):]
    city_list = list(range(1, num_city + 1))

    path_ref = [[]] + [find_comp(n, threshold) for n in range(1, num_city + 1)]

    for task in range(len(origin)):
        print(broad_judge(origin[task], destination[task], path_ref, city_list, [origin[task], destination[task]]))


def ts_diff_2(data):
    res = []
    for _lis in data:
        _out = _lis.copy()
        _index = []
        for i in range(len(_lis)):
            if _lis[i] is None:
                continue
            _index.append(i)
        for i in range(2, len(_index)):
            h = _index[i] - _index[i - 1]
            x = _index[i]
            _out[x] = (h ** (-2)) * (_lis[x] - 2 * _lis[x - h] + _lis[x - 2 * h])
            print('{} | {}'.format(_lis[x], x))
        _out[_index[0]] = None
        _out[_index[1]] = None
    res.append(_out)
    return res


if __name__ == '__main__':
    # data = [[None, 9, None, None, None, 4, None, None, None, 3, None, None, None]]
    # print(test(data))
    # print(test2(10))
    # data = [6, 1, 4, 1, 4, 3, 6, 4, 3, 6, 2, 5]
    # test3(data)
    print(test4(6, 1, [6, 4, 3, 6], [5, 6, 2, 5]))
    # data = [[None, 9, None, None, None, 4, None, None, None, 3, None, None, None]]
    # print(ts_diff_2([[1, None, 4, None, 2, None, 6]]))
    # print(ts_diff_2(data))
