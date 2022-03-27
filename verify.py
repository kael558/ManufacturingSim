import numpy as np
import matplotlib.pyplot as plt

data = []
rng = np.random.default_rng()

for i in range(300):
  data.append(rng.exponential(4.604416667)) # mean goes here for specific process distribution

plt.hist(data, bins=18)
plt.show()

print(f"The average is {sum(data) / len(data)}")
print(f"The difference between the expected and generated is {4.604416667 - (sum(data) / len(data))} or {abs(4.604416667 / (sum(data) / len(data)))}%")