class A:
    b = '123'
    ww = 'old1'
    def __init__(self):
        self.aa = '456'
        self.ww = 'old'
        # print('hhhaaa', self.b)

def test(a):
    print(a.ww)
w = A()
w.ww = 'new'
test(w)