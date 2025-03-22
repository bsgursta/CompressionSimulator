import heapq

def main():
    #Create dictionary to create the 16 entry dictionary
    indexed_dictionary= createDictionary("original.txt")

    with open("cout.txt","w") as file:
        pass
    compressCode("original.txt",indexed_dictionary)

def createDictionary(filename):
    #string of index, number of times appeared
    reg_dict = {}
    appearance_order = {}
    with open(filename,'r') as reg:
        read_data = reg.read().replace('\n', '')

        for i in range(0, len(read_data),32):
            temp_bit_val = read_data[i:i + 32]
            if temp_bit_val not in reg_dict:
                    reg_dict[temp_bit_val] = 1
                    appearance_order[temp_bit_val] = i
            else:
                reg_dict[temp_bit_val] += 1
    reg.close()
    #Get 16 most common in indexes
    sorted_vals = sorted(reg_dict.keys(), key=lambda x: (-reg_dict[x], appearance_order[x]))
    res = sorted_vals[:16]
    #for val in res:
        #print(f"{val}: {reg_dict[val]} occurrences")

    #Create indexed dictionary with string values
    indexed_dict = {}
    for i in range(0, 16):
        #get binary value and turn into string
        binary_val = f'{i:04b}'
        indexed_dict[binary_val] = res[i]

    #for key, value in indexed_dict.items():
        #print(key, value)
    return indexed_dict



#take in filepath and indexed dictionary
def compressCode(filename,reg_dict):
    writechar_count = 0
    buffer = ""
    file = open("cout.txt", "w")

    with open(filename, 'r') as reg:
        read_data = reg.read().replace('\n', '')
        #index 32-bit strings
        for i in range(0, len(read_data), 32):
            temp_bit_string = read_data[i:i + 32]

            #compress code -> direct matching, 1-bit mismatch, 2-bit consecutive, 4-bit consecutive, bitmask, 2-bit mismatch, uncompressed
            #CHECK RLE AFTER COMPRESSION

            #check if in library to just compress
            if libraryExistence(temp_bit_string, reg_dict):
                writestring = getdirectmatching(temp_bit_string,reg_dict)

            #found out what other compression to use
            else:
                writestring = f"000{temp_bit_string}"

            buffer += writestring
            writechar_count += len(writestring)

            # write specific number of characters when over 32 bits
            while writechar_count >= 32:
                file.write(buffer[:32] + "\n")
                buffer = buffer[32:]
                #adjust value
                writechar_count -= 32

            #check for repetitions for RLE

    reg.close()



# check if in library
def libraryExistence(bitstring, checkdict):
    if bitstring in checkdict.values():
        return True
    else:
        return False

def getdirectmatching(bitstring,passdict):
    for key,value in passdict.items():
        if value == bitstring:
            return f"111{key}"



if __name__ == "__main__":
    main()