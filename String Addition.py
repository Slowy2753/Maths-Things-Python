# Add two strings together


def string_add(n1,n2):

    # Adjust the strings to be the same length (and add an inial zero incase of needing an extra digit)
    nec_len = max(len(n1), len(n2)) + 1
    for i in range(0, nec_len - len(n1)):
        n1 = "0" + n1
    for j in range(0, nec_len - len(n2)):
        n2 = "0" + n2

    # Loops through digits starting right to left, adding the digits and
    # any overflow from the previous digit then left appening the result
    overflow=0
    result=""
    for digit in range(1, nec_len+1):
        add = int(n1[-digit]) + int(n2[-digit]) + overflow
        overflow = add//10
        result = str( (add)%10 ) + result

    # Removes any leading zeros
    while True:
        if result[0]=="0":
            result = result[1:]
        else:
            break

    return(result)


print(string_add("99","6"))
print(type(string_add("31504","546")))