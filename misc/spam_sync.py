import requests, time, sys

start = time.time()
times = []

def average(arr):
    arr_sum = 0
    for i in arr:
        arr_sum += i
    
    return arr_sum/len(arr)
    
for i in range(int(sys.argv[1])):
    requests.get('http://localhost:5000')
    times.append(time.time() - start)



print(f"{average(times)}s")