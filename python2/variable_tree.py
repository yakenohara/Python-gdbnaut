# -*- coding: utf-8 -*-

import gdb

def func_get_type_definition_string(gdbtype_by_this):

    long_code = gdbtype_by_this.code

    # typedef されている場合は オリジナルの宣言状態に戻す
    if long_code == gdb.TYPE_CODE_TYPEDEF:
        gdbtype_by_this = gdbtype_by_this.strip_typedefs()
        long_code = gdbtype_by_this.code

    #note
    # `str(gdbtype_by_this)`では、
    # `volatile` がついていた場合に gdb.lookup_type() の引数として
    # 使用できなくなるので、 `'struct ' + ` のようにする
    if long_code == gdb.TYPE_CODE_STRUCT:
        string_type_definition = 'struct ' + gdbtype_by_this.tag 

    elif long_code == gdb.TYPE_CODE_UNION:
        string_type_definition = 'union ' + gdbtype_by_this.tag

    elif long_code == gdb.TYPE_CODE_ENUM:
        string_type_definition = 'enum ' + gdbtype_by_this.tag

    else:
        string_type_definition = gdbtype_by_this.name
    
    return string_type_definition

def func_get_address_as_int(gdbval_target):

    int_address = 0 # return value

    gdbval_target_address = gdbval_target.address
    gdbtype_target_address = gdbval_target_address.type
    
    gdbtype_uint      = gdb.lookup_type("unsigned int")       # 32bit 長 unsigned 整数型定義
    gdbtype_ulonglong = gdb.lookup_type("unsigned long long") # 64bit 長 unsigned 整数型定義

    if( gdbtype_target_address.sizeof == gdbtype_uint.sizeof ): # 32bit 環境の場合
        int_address = int(gdbval_target_address.cast(gdbtype_uint))
    else:                                                       # 64bit 環境の場合
        int_address = int(gdbval_target_address.cast(gdbtype_ulonglong))
    
    return int_address

def func_traverser(gdbval_target):

    obj_traversing = {}

    # array or not 判定
    gdbtype_specified = gdbval_target.type
    if gdbtype_specified.code == gdb.TYPE_CODE_ARRAY: # array の場合

        objarr_traversed = []
        
        string_type_definition_of_element = func_get_type_definition_string(gdbtype_specified.target()) # elemnent の型定義を取得
        gdbtype_target = gdb.lookup_type(string_type_definition_of_element)

        # 配列要素数を算出
        long_size_of_element = gdbtype_target.sizeof # 配列の 1 要素の size
        long_size_of_array = gdbtype_specified.sizeof # 配列の全体 size
        long_length_of_array = long_size_of_array / long_size_of_element # 配列要素数
        
        # 配列ループ
        for long_index_of_target in range(long_length_of_array):
            obj_traversed = func_traverser(gdbval_target[long_index_of_target])
            objarr_traversed.append(obj_traversed)

        int_target_address = func_get_address_as_int(gdbval_target)
        gdbinferior_current = gdb.selected_inferior()
        chararr_read_memory = gdbinferior_current.read_memory(int_target_address, long_size_of_array)

        obj_traversing = {
            "address":int_target_address,
            "size":long_size_of_array,
            "dump":map(ord, chararr_read_memory),
            "type_code":gdbtype_specified.code,
            "type_definition":str(gdbtype_specified),
            "type_definition_name":gdbtype_specified.name,
            "type_definition_typedef_stripped":string_type_definition_of_element,
            "value":objarr_traversed
        }

    else: # array ではない場合

        string_type_definition_of_target = func_get_type_definition_string(gdbtype_specified)
        gdbtype_target = gdb.lookup_type(string_type_definition_of_target)
        
        if gdbtype_target.code in [
            gdb.TYPE_CODE_STRUCT,
            gdb.TYPE_CODE_UNION,
            gdb.TYPE_CODE_ENUM
            ]:

            gdbfieleds = gdbtype_target.fields()

            if gdbtype_target.code in [
                gdb.TYPE_CODE_STRUCT,
                gdb.TYPE_CODE_UNION
            ]:
                
                obj_members = {}

                int_target_address = func_get_address_as_int(gdbval_target)
                int_target_sizeof = gdbtype_target.sizeof
                gdbinferior_current = gdb.selected_inferior()
                chararr_read_memory = gdbinferior_current.read_memory(int_target_address, int_target_sizeof)
                
                for gdbfield in gdbfieleds:
                    obj_traversed = func_traverser(gdbval_target[gdbfield.name])
                    obj_traversed["identifier"] = gdbfield.name
                    
                    # gdbfield.bitpos は、構造体定義の先頭アドレスからの相対 bit 位置を表すので、
                    # 構造体メンバーアドレスからの相対 bit 位置を算出する
                    obj_traversed["bitpos"] = gdbfield.bitpos - ((obj_traversed["address"] - int_target_address) * 8)

                    # bit size
                    if(gdbfield.bitsize == 0): # bitfield が定義されていない場合は、 この条件にヒットする
                        obj_traversed["bitsize"] = obj_traversed["size"] * 8 # 変数の定義 byte 長 -> bit 長変換
                    else:  # bitfield が定義されている場合
                        obj_traversed["bitsize"] = gdbfield.bitsize
                    
                    obj_members[gdbfield.name] = obj_traversed
                
                obj_traversing = {
                    "address":int_target_address,
                    "size":int_target_sizeof,
                    "dump":map(ord, chararr_read_memory),
                    "type_code":gdbtype_target.code,
                    "type_definition":str(gdbtype_specified),
                    "type_definition_name":gdbtype_specified.name,
                    "type_definition_typedef_stripped":string_type_definition_of_target,
                    "value":obj_members
                }

            elif gdbtype_target.code == gdb.TYPE_CODE_ENUM: # enum

                obj_defs = {}

                for gdbfield in gdbfieleds:
                    obj_defs[gdbfield.name] = gdbfield.enumval
                
                int_target_address = func_get_address_as_int(gdbval_target)
                int_target_sizeof = gdbtype_target.sizeof
                gdbinferior_current = gdb.selected_inferior()
                chararr_read_memory = gdbinferior_current.read_memory(int_target_address, int_target_sizeof)

                obj_traversing = {
                    "address":int_target_address,
                    "size":int_target_sizeof,
                    "dump":map(ord, chararr_read_memory),
                    "type_code":gdbtype_target.code,
                    "type_definition":str(gdbtype_specified),
                    "type_definition_name":gdbtype_specified.name,
                    "type_definition_typedef_stripped":string_type_definition_of_target,
                    "value":int(gdbval_target)
                }

                obj_traversing["enum_dict"] = obj_defs

            else:
                pass
        
        elif gdbtype_target.code in [
            gdb.TYPE_CODE_INT,  # int
            gdb.TYPE_CODE_CHAR, # char
            gdb.TYPE_CODE_FLT   # float
        ]:

            int_target_address = func_get_address_as_int(gdbval_target)
            int_target_sizeof = gdbtype_target.sizeof
            gdbinferior_current = gdb.selected_inferior()
            chararr_read_memory = gdbinferior_current.read_memory(int_target_address, int_target_sizeof)
            
            obj_traversing = {
                "address":func_get_address_as_int(gdbval_target),
                "size":gdbtype_target.sizeof,
                "dump":map(ord, chararr_read_memory),
                "type_code":gdbtype_target.code,
                "type_definition":str(gdbtype_specified),
                "type_definition_name":gdbtype_specified.name,
                "type_definition_typedef_stripped":string_type_definition_of_target
            }

            if gdbtype_target.code == gdb.TYPE_CODE_FLT:
                obj_traversing["value"] = float(gdbval_target)

            else:
                obj_traversing["value"] = int(gdbval_target)
            
        else:
            #todo warn
            pass
            
    
    return obj_traversing

def func_make_variable_tree(string_symbol_name):
    gdbsym_a = gdb.lookup_symbol(string_symbol_name)[0]
    # todo error handling
    gdbval_a = gdbsym_a.value()
    obj_traversed = func_traverser(gdbval_a)
    obj_traversed["identifier"] = string_symbol_name

    return obj_traversed
