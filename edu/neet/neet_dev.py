# %%
t1, t2 = "oxcpqrsvwf", "shmtulqrypy"
common = set(t1).intersection(set(t2))
# is & intersection faster than set union?
# leave only common characters
n1 = [c for c in t1 if c in common]
n2 = [c for c in t2 if c in common]
print(n1, n2)
# %%
