
class Test:

    WHAT = 1

    def self_inc(self):
        self.WHAT += 1

    def cls_inc(self):
        self.__class__.WHAT += 1

    def self_set(self, v):
        self.WHAT = v

    def cls_set(self, v):
        self.__class__.WHAT = v


class SubTest(Test):
    pass


class Sub2Test(Test):
    pass


def p(*args):
    print(args, type(args))


p(1, 2, 3)

