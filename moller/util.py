import math

def find_mid_of_longest_run(arr, value):
    cur = 0

    run = 0
    pos = 0
    max_pos = 0
    max_run = 0

    while(True):
        if arr[cur] == value:
            if run == 0:
                pos = cur
            run = run + 1
        else:
            if max_run < run:
                max_pos = pos
                max_run = run
            run = 0


        cur = cur + 1

        # Its over, and last value was not part of run
        if cur == len(arr):
            if max_run < run:
                max_run = run
                max_pos = pos
            break

    return max_pos + math.floor(max_run / 2)


def find_mid_of_longest_run_with_wrap(arr, value):
    cur = 0
    pos = 0
    run = 0
    mid_pos = 0
    old_run = 0
    loop = False

    while(True):
        if arr[cur] == value:
            if run == 0:
                pos = cur
            run = run + 1
        else:
            if loop == True:
                if old_run < run:
                    old_run = run
                    mid_pos = pos + math.floor(run / 2)
                    if(mid_pos >= len(arr)):
                        mid_pos = mid_pos - len(arr)

                break
            else:
                if old_run < run:
                    old_run = run
                    mid_pos = pos + math.floor(run / 2)
                    if(mid_pos >= len(arr)):
                        mid_pos = mid_pos - len(arr)
                    pos = cur

            run = 0


        cur = cur + 1

        # Its over, and last value was not part of run
        if cur == len(arr) and (run == 0 or run == len(arr)) :
            if run == len(arr):
                mid_pos = math.floor(len(arr) / 2)
            break

        # Hit end of array, but loop check
        if cur == len(arr) and run != 0:
            loop = True
            cur = 0

    return mid_pos
