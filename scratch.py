age = 30
st='2,40'
print(any(age >= int(specialage) for specialage in str(st).split(",")))
