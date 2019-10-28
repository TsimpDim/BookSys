import asyncio, requests, sys, time, concurrent.futures

start = time.time()
times = []

def average(arr):
    arr_sum = 0
    for i in arr:
        arr_sum += i
    
    return arr_sum/len(arr)
    

async def main():

    with concurrent.futures.ThreadPoolExecutor(max_workers=int(sys.argv[2])) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                None, 
                requests.get, 
                'http://localhost:5000'
            )
            for i in range(int(sys.argv[1]))
        ]
        for response in await asyncio.gather(*futures):
            times.append(time.time() - start)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

print(f"{average(times)}s")