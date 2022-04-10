import numpy as np
import matplotlib.pyplot as plt

data = []
mean = 20.63275667

for i in range(10000):
  data.append(np.random.exponential(mean)) # mean goes here for specific process distribution

plt.hist(data, bins=18)
plt.show()

print(f"The average is {sum(data) / len(data)}")
print(f"The difference between the expected and generated is {mean - (sum(data) / len(data))} or {abs(mean / (sum(data) / len(data)))}%")