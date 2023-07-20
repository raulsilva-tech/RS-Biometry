
import psutil

avg = 0
count = 20

# for i in range(count):
#     usage = psutil.cpu_times_percent(interval=1, percpu=False)
#     print(psutil.cpu_percent(interval=1, percpu=False))
#     current = 100 - usage.idle
#     avg += current
#     print(usage)

for i in range(count):
    usage = psutil.cpu_percent(interval=0.5, percpu=False)
    avg += usage
    print(usage)


avg = avg / count
print("Média: ", round(avg,2))


# print(psutil.virtual_memory())  # physical memory usage
# print('memory % used:', psutil.virtual_memory()[2])