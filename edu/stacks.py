#%% self definitisons
class Stack():
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

# %%
def is_balanced(strings):
    s = Stack()
    open_brackets = "[{("
    matches ={ "}": "{", 
                ")" : "(",
                "]" : "["
                }
    for letter in strings:
        if letter in open_brackets:
            s.push(letter)
        
        if letter in matches:
            if s.pop() == matches[letter]:
                pass
            else:
                return False
    
    if len(s.items) > 0:
        return False
    
    return True

#%%
import checker
checker.Checker.check(True, is_balanced("(){}{[]}"))
checker.Checker.check(False, is_balanced("([)"))


# %%
