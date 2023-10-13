import pandas as pd

df = pd.DataFrame({'user':['admin','jose', 'marilyn'], 'password':['yesyes','#123456', '#123456']})
df.to_csv('zero.csv', index=False)

dff = pd.read_csv('zero.csv')
zero_auth = {}

for i in range(df.shape[0]):
    zero_auth[df['user'].iloc[i]] = df['password'].iloc[i] 

print(zero_auth)
