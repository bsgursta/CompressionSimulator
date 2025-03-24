import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 SIM.py [1|2]")
        print("1 for compression, 2 for decompression")
        return

    option = sys.argv[1]

    if option == '1':
        compress()
    elif option == '2':
        decompress()
    else:
        print("Invalid option. Use '1' for compression or '2' for decompression.")

def compress():
    #Create dictionary to create the 16 entry dictionary
    indexed_dictionary= createDictionary("original.txt")

    with open("cout.txt","w") as file:
        pass
    compressCode("original.txt",indexed_dictionary)

def decompress():
    ##createdictionary from
    print("hi")



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
        rle_count = 0
        for i in range(0, len(read_data), 32):
            temp_bit_string = read_data[i:i + 32]

            ## first time, keep going, also check rle
            if i == 0:
                pass
            elif rle_count == 8:
                pass
            elif prev_bitstring == temp_bit_string:
                rle_count += 1
                continue
            elif prev_bitstring !=  temp_bit_string:
                pass

            #compress code -> direct matching, 1-bit mismatch, 2-bit consecutive, 4-bit consecutive, bitmask, 2-bit mismatch, uncompressed
            #check if in library to just compress
            if libraryExistence(temp_bit_string, reg_dict):
                partial_string = getdirectmatching(temp_bit_string,reg_dict)

            #found out what other compression to use
            else:
                #check 1-bit,2-bit(cons),4-bit(cons) mismatch, 2-bit non-consecutive mismatch
                partial_string = get_mismatch_string(temp_bit_string,reg_dict)

                #check bitmask

                if partial_string is None:
                    #uncompressed
                    partial_string = f"000{temp_bit_string}"
                else:
                    pass

            #check if RLE should be added to beginning of string
            if rle_count != 0:
                rle_string = getRLEstring(rle_count)
                write_string = rle_string + partial_string
                rle_count = 0
            else:
                write_string = partial_string

            buffer += write_string
            writechar_count += len(write_string)

            # write specific number of characters when over 32 bits
            while writechar_count >= 32:
                file.write(buffer[:32] + "\n")
                buffer = buffer[32:]
                #adjust value
                writechar_count -= 32

            #maintain the current bitstring so that next iteration you can check if it's repeating.
            prev_bitstring =  temp_bit_string

        #pad with 0s if necessary and write final 32 bit line
        file.write(buffer)
        for i in range(32-writechar_count):
            file.write('0')
        file.write('\n')

        #write dictionary into file
        file.write("xxxx\n")
        for key, value in reg_dict.items():
            file.write(f"{value}\n")
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

def getRLEstring(num_repetitions):
    binary_val = f'{(num_repetitions - 1):03b}'
    return f"001{binary_val}"

#return string
def get_mismatch_string(bitstring,passdict):

    #check if there is exactly 1 mismatch
    for key, value in passdict.items():
        result = get_bit_differences(bitstring,value)
        if result[0] == 1:
            index = result[1].index('1')
            return f"011{index:05b}{key}"
        #check if consecutive bits, first 2 then 4
        elif result[0] == 2:
            if consecutive_bits(result[1]) == 2:
                index = result[1].index('1')
                return f"100{index:05b}{key}"
        elif result[0] == 4:
            if consecutive_bits(result[1]) == 4:
                index = result[1].index('1')
                return f"101{index:05b}{key}"
    #check for 4-bit masking
    for key, value in passdict.items():
        result = get_bit_differences(bitstring, value)
        if 0 < result[0] <= 4:
            first_index = 0
            #get index of first bit mismatch
            for index,char in enumerate(result[1]):
                if char == '1':
                    first_index = index
                    break
            #return cause not enough space
            if first_index > 29:
                return None
            current_bits = 1
            bitmask = result[1][first_index:first_index + 4]

            for char in bitmask[1:]:
                if char == '1':
                    current_bits += 1
            if current_bits != result[0]:
                continue
            else:
                return f"010{first_index:05b}{bitmask}{key}"




    #check for 2-bit mismatch anywhere
    for key, value in passdict.items():
        result = get_bit_differences(bitstring, value)
        if result[0] == 2:
            indexes = []
            for index,char in enumerate(result[1]):
                if char == '1':
                    indexes.append(index)
            return f"110{indexes[0]:05b}{indexes[1]:05b}{key}"

    return None



#returns the number of mismatches and the binary string itself
def get_bit_differences(current_bitstring,dict_bitstring):
    xor_calc = int(current_bitstring,2) ^ int(dict_bitstring,2)

    num_mismatches = bin(xor_calc).count('1')
    new_binary = bin(xor_calc)[2:].zfill(32)
    return num_mismatches, new_binary

def consecutive_bits(xor):
    max_count = 0
    current_count = 0

    for bit in xor:
        if bit == '1':
            current_count += 1
            max_count = max(max_count, current_count)
        else:
            current_count = 0
    return max_count




if __name__ == "__main__":
    main()