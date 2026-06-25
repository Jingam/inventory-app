print('test')
def main():
    print("Test")
    while True:
        print("================", "\n")
        print("Main Menu" , sep="\n")
        testValue = input("Enter X to Exit\n")
        if testValue == 'X':
            break
        else:
            print("Invalid Try Again")
            continue

main()