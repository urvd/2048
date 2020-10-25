class Case:
    def __init__(self, x, y, value = 0):
        self.x = x
        self.y = y
        self.value = value

    def set(self,x,y,val): #methodes d'affectation
        self.x = x
        self.y = y
        self.value = val

    def is_empty(self):
        return self.value == 0
    def forbiddenCase(self):
        return  self.x == -1 and self.y == -1 and self.value == -1

    def set_empty(self):
        self.value = 0

    def __eq__(self, obj):
        return  self.x == obj.x and self.y == obj.y and self.value == obj.value

    def toString(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')=' + str(self.value)