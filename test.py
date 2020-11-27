from faker import Faker
import pandas as pd

fake = Faker()

num_rows = 100000

totol_rows = []

for _ in range(num_rows) :
	single_row = []
	single_row.append(fake.name())
	single_row.append(fake.address())

	totol_rows.append(single_row)


df = pd.DataFrame(data=totol_rows, columns=['name', 'address'])
df.to_csv("test.csv")