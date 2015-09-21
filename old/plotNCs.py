trgDir = '/Users/michaesm/Documents/repositories/uframe/'

for root, dirs, files in os.walk(trgDir):
for file in files:
...             if file.endswith(".nc"):
...                     print(os.path.join(root,file))