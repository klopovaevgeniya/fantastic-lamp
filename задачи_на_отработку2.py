numbers = [43, 54, 157, 69, 28]
print (numbers)
print (min (numbers))
print (max (numbers))


words = ['orange', 'football', 'banana', 'train', 'apple']
words.sort()
print (words)


student = {'Popov': 5, 'Petrova': 3, 'Volkov': 4, 'Lihachev': 5}
items = student.items()
print (student)


word_list = (x.lower() for x in  (input("¬ведите текст:")).split(' '))
unique = set()
for word in word_list:
    if word not in unique:
        unique.add(word)
print(*unique)


a = {0, 1, 2, 3}
b = {4, 3, 2, 1}
c = a.intersection(b)
print (c)


