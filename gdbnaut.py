# -*- coding: utf-8 -*-

# <License>------------------------------------------------------------

#  Copyright (c) 2019 Shinnosuke Yakenohara

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -----------------------------------------------------------</License>

"""
GDB utility module
"""

import gdb
import json
import sys
import inspect
import collections

class SymbolInfo:
    """
    Managing scanning result about symbol which specified by str
    """

    #<caution 将来使えなくなる可能性が高い>----------------------------------------------------------

    # オブジェクトの型が以下のいづれかの場合は、
    # なぜか `.unqualified()`` しても `volatile` が消せない
    #  - `gdb.TYPE_CODE_PTR`
    #  - `gdb.TYPE_CODE_ARRAY`
    # なので、この関数内で正規表現置換を使ってでむりやり削除する
    def _func_force_unq(self, str_from_this):
        import re
        str_tmp = str_from_this
        str_tmp = re.sub(r'volatile', '', str_tmp)
        str_tmp = re.sub(r'const', '', str_tmp)
        str_tmp = re.sub(r'^ +', '', str_tmp)
        str_tmp = re.sub(r' +$', '', str_tmp)
        str_tmp = re.sub(r' {2,}', ' ', str_tmp)

        return str_tmp

    # address から symbol を求める API が存在しないので、
    # しかたなく gdb の `info symbol addr` の実行結果をパースして求める
    # https://sourceware.org/gdb/current/onlinedocs/gdb/Symbols.html
    # note:
    # 関数なら以下ページのように address から function name を求めることが可能だけど、
    # 少なくともグローバル変数については同様の方法が通用しない
    # (`.block_for_pc()` method で `RuntimeError: Cannot locate object file for block.` になってしまう)
    # https://gdb.sourceware.narkive.com/llzhRD4K/info-symbol-equivalent-in-python
    # https://stackoverflow.com/questions/47916564/gdb-python-api-getting-symbol-name-from-address?rq=1
    def _func_get_symbol_name_from_addr(self, int_address):
        import re
        str_gdbcmd = "info symbol " + str(hex(int_address))
        str_out = gdb.execute(str_gdbcmd, False, True) # 2nd argment: user invoking interactively を指定しない
                                                       # 3rd argment: 実行結果を standard out ではなく string として返却させる
        
        str_ret = None
        itr_found = re.finditer(r' +in section', str_out)
        for itr_found_elem in itr_found:
            str_ret = str_out[:itr_found_elem.start()] # `in section` 文字列の手前までが symbol name
            break
        
        itr_found = re.finditer(r' +\+', str_out)
        for itr_found_elem in itr_found:
            str_ret = str_out[:itr_found_elem.start()] #バイト数の ズレを表示している部分 ( `+[0-9]+` を削除 )
            break

        return str_ret # 見つからない場合(= `No symbol matches 0x???.` のような場合) は、 None のまま返す

    #---------------------------------------------------------</caution 将来使えなくなる可能性が高い>

    def _func_dump_memory(self, int_start_address, int_size):
        chararr_read_memory = self._gdbifr_specified.read_memory(int_start_address, int_size)
        obj_dump = collections.OrderedDict()
        int_address_counter = int_start_address
        for mem in chararr_read_memory:
            obj_dump[(self._address_hex_format.format(int_address_counter))] = '0x{:02x}'.format(ord(mem))
            int_address_counter += 1

        return obj_dump

    def _get_address_hex_format(self):
        str_address_hex_format = None
        gdbtype_uint    = gdb.lookup_type("unsigned int")       # 32bit 長 unsigned 整数型定義
        int_sizeof_intp = gdb.lookup_type("int").pointer().sizeof

        if( int_sizeof_intp == gdbtype_uint.sizeof ): # 32bit 環境の場合
            str_address_hex_format = '0x{:08x}'
        else:                                         # 64bit 環境の場合
            str_address_hex_format = '0x{:016x}'
        
        return str_address_hex_format

    def _func_get_address_length_uint(self):
        gdbtype_to_ret_type = None
        gdbtype_uint      = gdb.lookup_type("unsigned int")       # 32bit 長 unsigned 整数型定義
        gdbtype_ulonglong = gdb.lookup_type("unsigned long long") # 64bit 長 unsigned 整数型定義

        int_sizeof_intp = gdb.lookup_type("int").pointer().sizeof

        if( int_sizeof_intp == gdbtype_uint.sizeof ): # 32bit 環境の場合
            gdbtype_to_ret_type = gdbtype_uint
        else:                                         # 64bit 環境の場合
            gdbtype_to_ret_type = gdbtype_ulonglong
        
        return gdbtype_to_ret_type

    def _func_scan_gdb_val(self, gdbval_specified, int_hierarchy_level):

        obj_scanning = collections.OrderedDict()
        gdbtype_specified = gdbval_specified.type

        # array / pointer / それ以外 判定
        if (gdbtype_specified.code == gdb.TYPE_CODE_ARRAY): # array の場合

            obarr_scanned = []
            gdbtype_target_of_element = gdbtype_specified.target()
            
            # 配列要素数を算出
            int_size_of_element = gdbtype_target_of_element.sizeof # 配列の 1 要素の size
            int_size_of_array = gdbtype_specified.sizeof # 配列の全体 size
            int_length_of_array = int(int_size_of_array / int_size_of_element) # 配列要素数
            
            # 配列ループ
            for int_index_of_target in range(int_length_of_array):
                obj_scanned = self._func_scan_gdb_val(gdbval_specified[int_index_of_target], int_hierarchy_level + 1)

                if (obj_scanned is None) : # 不明な型が存在した為に scan 失敗した場合
                    return None # None を返して終了

                obj_scanned["identifier"] = int_index_of_target
                obarr_scanned.append(obj_scanned)

            int_target_address = int(gdbval_specified.address.cast(self._gdbtyp_address_length_uint))
            
            obj_scanning = collections.OrderedDict()
            
            obj_scanning["identifier"] = None # caller で設定する
            obj_scanning["address"] = self._address_hex_format.format(int_target_address)
            obj_scanning["size"] = int_size_of_array
            obj_scanning["type_code"] = gdbtype_specified.code
            obj_scanning["type_declared"] = str(gdbtype_specified)
            obj_scanning["type_primitive"] = self._func_force_unq(str(gdbtype_specified)) # caution <- .unqualified() してもなぜか volatile が消せないので、無理やり文字列置換で取得している
            obj_scanning["value"] = obarr_scanned
            
            
            obj_scanning["dump"] = self._func_dump_memory(int_target_address, int_size_of_array)

        elif(gdbtype_specified.code == gdb.TYPE_CODE_PTR): # pointer の場合

            int_target_address = int(gdbval_specified.address.cast(self._gdbtyp_address_length_uint))
            
            obj_scanning = collections.OrderedDict()

            obj_scanning["identifier"] = None # caller で設定する
            obj_scanning["address"] = self._address_hex_format.format(int_target_address)
            obj_scanning["size"] = gdbtype_specified.sizeof
            obj_scanning["type_code"] = gdbtype_specified.code
            obj_scanning["type_declared"] = str(gdbtype_specified)
            obj_scanning["type_primitive"] = self._func_force_unq(str(gdbtype_specified)) # caution <- .unqualified() してもなぜか volatile が消せないので、無理やり文字列置換で取得している
            obj_scanning["value"] = self._address_hex_format.format(int(gdbval_specified.cast(self._gdbtyp_address_length_uint)))


            obj_scanning["dump"] = self._func_dump_memory(int_target_address, gdbtype_specified.sizeof)

            self._gdbval_ptr_queue_arr.append(gdbval_specified) # pointer list に queue
            
        else: # array でも pointer でもない場合

            gdbtype_specified_unq = gdbtype_specified.unqualified() # volatile, const キーワードの削除
            gdbtype_specified_unq_strptypdef = gdbtype_specified_unq.strip_typedefs()

            if (gdbtype_specified_unq_strptypdef.name is None): # .name が無い場合 
                                                                # (ex: typedef struct{...}xxx_t; のように、struct xxx を省略記載している場合)
                str_primitive_type_name = str(gdbtype_specified_unq)

            else: # .name が存在する場合 
                str_primitive_type_name = str(gdbtype_specified_unq_strptypdef)

            # field を持つタイプ or not 判定
            if gdbtype_specified_unq_strptypdef.code in [ # field を持つタイプの場合
                gdb.TYPE_CODE_STRUCT,
                gdb.TYPE_CODE_UNION,
                gdb.TYPE_CODE_ENUM
                ]:

                gdbfieleds = gdbtype_specified_unq_strptypdef.fields()

                if gdbtype_specified_unq_strptypdef.code in [
                    gdb.TYPE_CODE_STRUCT,
                    gdb.TYPE_CODE_UNION
                ]:

                    obj_members = collections.OrderedDict()

                    int_target_address = int(gdbval_specified.address.cast(self._gdbtyp_address_length_uint))
                    
                    for gdbfield in gdbfieleds:
                        obj_scanned = self._func_scan_gdb_val(gdbval_specified[gdbfield.name], int_hierarchy_level + 1)
                        
                        if (obj_scanned is None) : # 不明な型が存在した為に scan 失敗した場合
                            return None # None を返して終了

                        obj_scanned["identifier"] = gdbfield.name
                        
                        # gdbfield.bitpos は、構造体定義の先頭アドレスからの相対 bit 位置を表すので、
                        # 構造体メンバーアドレスからの相対 bit 位置を算出する
                        obj_scanned["bitpos"] = gdbfield.bitpos - (( int(obj_scanned["address"], 0) - int_target_address) * 8)

                        # bit size
                        if(gdbfield.bitsize == 0): # bitfield が定義されていない場合は、 この条件にヒットする
                            obj_scanned["bitsize"] = obj_scanned["size"] * 8 # 変数の定義 byte 長 -> bit 長変換
                        else:  # bitfield が定義されている場合
                            obj_scanned["bitsize"] = gdbfield.bitsize
                        
                        obj_members[gdbfield.name] = obj_scanned
                    
                    obj_scanning = collections.OrderedDict()
                    
                    obj_scanning["identifier"] = None # caller で設定する
                    obj_scanning["address"] = self._address_hex_format.format(int_target_address)
                    obj_scanning["size"] = gdbtype_specified_unq_strptypdef.sizeof
                    obj_scanning["type_code"] = gdbtype_specified_unq_strptypdef.code
                    obj_scanning["type_declared"] = str(gdbtype_specified)
                    obj_scanning["type_primitive"] = str_primitive_type_name
                    obj_scanning["value"] = obj_members
                    

                    obj_scanning["dump"] = self._func_dump_memory(int_target_address, gdbtype_specified_unq_strptypdef.sizeof)

                elif gdbtype_specified_unq_strptypdef.code == gdb.TYPE_CODE_ENUM: # enum

                    obj_defs = collections.OrderedDict()

                    for gdbfield in gdbfieleds:
                        obj_defs[gdbfield.name] = gdbfield.enumval
                    
                    int_target_address = int(gdbval_specified.address.cast(self._gdbtyp_address_length_uint))
                    
                    obj_scanning = collections.OrderedDict()
                    
                    obj_scanning["identifier"] = None # caller で設定する
                    obj_scanning["address"] = self._address_hex_format.format(int_target_address)
                    obj_scanning["size"] = gdbtype_specified_unq_strptypdef.sizeof
                    obj_scanning["type_code"] = gdbtype_specified_unq_strptypdef.code
                    obj_scanning["type_declared"] = str(gdbtype_specified)
                    obj_scanning["type_primitive"] = str_primitive_type_name
                    obj_scanning["value"] = int(gdbval_specified)
                    

                    obj_scanning["dump"] = self._func_dump_memory(int_target_address, gdbtype_specified_unq_strptypdef.sizeof)

                    obj_scanning["enum_dict"] = obj_defs

                else: # Unkownなルートの場合(=実装ミスの場合)

                    # エラー表示
                    insobj_curframe_b_back = inspect.currentframe().f_back
                    sys.stderr.write(
                        "[error] An unknown processing route was executed." + "\n" +
                        "[error] File:" + insobj_curframe_b_back.f_code.co_filename + "\n" +
                        "[error] Function:" + insobj_curframe_b_back.f_code.co_name + "\n" +
                        "[error] Line no:" + str(insobj_curframe_b_back.f_lineno) + "\n"
                    )
                    
                    return None # None を返して終了
            
            else: # field を持たないタイプの場合

                if gdbtype_specified_unq_strptypdef.code in [ # primitive の場合
                    gdb.TYPE_CODE_INT,  # int
                    gdb.TYPE_CODE_CHAR, # char
                    gdb.TYPE_CODE_FLT   # float
                ]:

                    int_target_address = int(gdbval_specified.address.cast(self._gdbtyp_address_length_uint))

                    obj_scanning = collections.OrderedDict()

                    obj_scanning["identifier"] = None # caller で設定する
                    obj_scanning["address"] = self._address_hex_format.format(int_target_address)
                    obj_scanning["size"] = gdbtype_specified_unq_strptypdef.sizeof
                    obj_scanning["type_code"] = gdbtype_specified_unq_strptypdef.code
                    obj_scanning["type_declared"] = str(gdbtype_specified)
                    obj_scanning["type_primitive"] = str_primitive_type_name
                    

                    if gdbtype_specified_unq_strptypdef.code == gdb.TYPE_CODE_FLT:
                        obj_scanning["value"] = float(gdbval_specified)

                    else:
                        obj_scanning["value"] = int(gdbval_specified)

                    obj_scanning["dump"] = self._func_dump_memory(int_target_address, gdbtype_specified_unq_strptypdef.sizeof)

                else:
                    # Unkdown な type の場合
                    insobj_curframe_b_back = inspect.currentframe().f_back
                    sys.stderr.write(
                        "[error] Unkwon type was specified." + "\n" +
                        "[error] type_code:" + str(gdbtype_specified_unq_strptypdef.code) + "\n" +
                        "[error] type_declared:" + str(gdbtype_specified) + "\n" +
                        "[error] value:" + str(gdbval_specified) + "\n"
                    )
                    return None # None を返して終了
                
        return obj_scanning

    def _func_get_address_range(self, gdbsym_specified):
        """
        gdb.Symbol が表す symbol の専有アドレス範囲を返す
        不明な gdb.Symbol が指定された場合は、(None, None) を返す
        """

        tpl_range = (None, None)

        if (gdbsym_specified.is_variable or # variable
            gdbsym_specified.is_argument or # 引数
            gdbsym_specified.is_constant
        ):
            
            gdbval_specified = gdbsym_specified.value(gdb.selected_frame())
            int_first_address = int(gdbval_specified.address.cast(self._gdbtyp_address_length_uint))
            int_last_address =  int_first_address + gdbval_specified.type.sizeof - 1

            tpl_range = (int_first_address, int_last_address)

        elif (gdbsym_specified.is_function): # function
            gdbval_func_adr = gdbsym_specified.value(gdb.selected_frame())
            int_func_adr = int(gdbval_func_adr.cast(self._gdbtyp_address_length_uint)) # function を表す symbol の場合は、
                                                                                    # .value() で返ってくる gdb.Value に対して
                                                                                    # 直接 int へ cast できない。(理由は不明)
            # gdbblk_target = gdb.block_for_pc(int_func_adr) # 関数が配置されている アドレスの block を取得
            gdbblk_target = gdb.block_for_pc(int_func_adr)
            int_first_address = gdbblk_target.start
            int_last_address = gdbblk_target.end

            tpl_range = (int_first_address, int_last_address)

        else: # unkown なシンボルの場合
            
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] Cannot calculate address range Because of" + "\n" +
                "[error] specified gdb.Symbol object has unkown type." + "\n" +
                "[error] Which is not variable, argment, constant, nor function." + "\n" +
                "[error] str(gdb.Symbol):" + str(gdbsym_specified) + "\n" +
                "[error] The corresponding code part is" + "\n" +
                "[error] File:" + insobj_curframe_b_back.f_code.co_filename + "\n" +
                "[error] Function:" + insobj_curframe_b_back.f_code.co_name + "\n" +
                "[error] Line no:" + str(insobj_curframe_b_back.f_lineno) + "\n"
            )

        return tpl_range

    def _func_scan_gdb_sym(self, gdbsym_specified):

        obj_ret = None

        if (gdbsym_specified.is_variable or # variable
            gdbsym_specified.is_argument or # 引数
            gdbsym_specified.is_constant
        ):
            gdbval_a = gdbsym_specified.value(gdb.selected_frame())
            obj_scanned = self._func_scan_gdb_val(gdbval_a, 0)

            if (obj_scanned is None):
                return None # None を返して終了

            obj_scanned["identifier"] = gdbsym_specified.name
            obj_ret = obj_scanned

        elif (gdbsym_specified.is_function): # function
            
            int_first_address_of_function, int_last_address_of_function = self._func_get_address_range(gdbsym_specified)
            int_size_of_function = int_last_address_of_function - int_first_address_of_function + 1
            gdbtyp_function = gdbsym_specified.type

            obj_scanned = collections.OrderedDict()

            obj_scanned["identifier"] = gdbsym_specified.name
            obj_scanned["address"] = self._address_hex_format.format(int_first_address_of_function)
            obj_scanned["size"] = int_size_of_function
            obj_scanned["type_code"] = gdbtyp_function.code
            obj_scanned["type_declared"] = str(gdbtyp_function)
            obj_scanned["type_primitive"] = self._func_force_unq(str(gdbtyp_function)) # caution <- .unqualified() してもなぜか volatile が消せないので、無理やり文字列置換で取得している
            
            obj_scanned["dump"] = self._func_dump_memory(int_first_address_of_function, int_size_of_function)

            obj_ret = obj_scanned

        else: # unkown なシンボルの場合
            
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] Cannot scan specified gdb.Symbol." + "\n" +
                "[error] Specified gdb.Symbol object has unkown type." + "\n" +
                "[error] Which is not variable, argment, constant, nor function." + "\n" +
                "[error] str(gdb.Symbol):" + str(gdbsym_specified) + "\n" +
                "[error] The corresponding code part is" + "\n" +
                "[error] File:" + insobj_curframe_b_back.f_code.co_filename + "\n" +
                "[error] Function:" + insobj_curframe_b_back.f_code.co_name + "\n" +
                "[error] Line no:" + str(insobj_curframe_b_back.f_lineno) + "\n"
            )

        return obj_ret

    def _func_check_already_scanned(self, gdbsym_a, obj_scanning):
        """
        指定された gdb.Symbol の専有アドレス範囲に対して scan 済かどうかを返す

        Returns
        -------
        tpl_already_scanned : tuple  
            [0] -> 終了ステータス。  
                   指定された gdb.Symbol の専有アドレス範囲の取得に失敗した場合に False  
                   成功した場合に True  
            [1] -> scan 済みなら True, 未 scan なら False  
        """

        int_first_address_target, int_last_address_target = self._func_get_address_range(gdbsym_a) # gdb.Symbol から 占有 address 範囲を取得

        if (int_first_address_target is None): # 指定された gdb.Symbol の専有アドレス範囲の取得に失敗
            return (False, False)

        # 走査済み address かどうかのチェック
        tpl_already_scanned = (True, False)
        
        for obj_symbol_key, obj_symbol in obj_scanning.items():

            int_first_address_of_scanned  = int(obj_symbol["address"], 0)
            int_last_address_of_scanned   = int_first_address_of_scanned + obj_symbol["size"] - 1
            
            if ( # 走査済みアドレス範囲の場合
                (int_first_address_of_scanned   <= int_first_address_target      ) and
                (int_first_address_target       <= int_last_address_of_scanned   ) and
                (int_first_address_of_scanned   <= int_last_address_target       ) and
                (int_last_address_target        <= int_last_address_of_scanned   )
            ):
                tpl_already_scanned = (True, True) # 走査済み を格納
                break
            
            elif(( # 走査済みアドレス範囲から一部がはみ出している場合
                (int_first_address_of_scanned   <= int_first_address_target      ) and
                (int_first_address_target       <= int_last_address_of_scanned   )
            ) or (
                (int_first_address_of_scanned   <= int_last_address_target       ) and
                (int_last_address_target        <= int_last_address_of_scanned   )
            )):
                
                print(
                    "[warning] Only some of part address range are scanned." + "\n" +
                    "[warning] Specified symbol :" + str(gdbsym_a) + "\n" +
                    "[warning] First address :" + self._address_hex_format.format(int_first_address_target) + "\n"
                    "[warning] Last address  :" + self._address_hex_format.format(int_last_address_target) + "\n" +
                    "[warning] Already scanned symbol :" + obj_symbol_key + "\n" +
                    "[warning] First address :" + self._address_hex_format.format(int_first_address_of_scanned) + "\n" +
                    "[warning] Last address  :" + self._address_hex_format.format(int_last_address_of_scanned)
                )

        return tpl_already_scanned
        
    def _func_scan(self, strarr_symbol_name):
        
        obj_scanning = collections.OrderedDict()

        # symbol 名毎の走査ループ
        for str_symbol_name in strarr_symbol_name:
            
            gdbsym_a = gdb.lookup_symbol(str_symbol_name)[0]

            if (gdbsym_a is None): # symbol が見つからなかった場合
                
                insobj_curframe_b_back = inspect.currentframe().f_back
                sys.stderr.write(
                    "[error] Specified symbol name`" + str_symbol_name + "` not found." + "\n"
                )
                return None # None を返して終了

            else:
                bool_already_scannced_status, bool_already_scannced = self._func_check_already_scanned(gdbsym_a, obj_scanning)

                if not(bool_already_scannced_status) : # アドレス算出異常の場合
                    return None # None を返して終了
                
                if not(bool_already_scannced) : # symbol が見つかった & 走査済みでない場合
            
                    self._gdbval_ptr_queue_arr = []
                    obj_scanned = self._func_scan_gdb_sym(gdbsym_a)

                    if (obj_scanned is None): # scan に失敗した場合
                        return None # None を返して終了

                    obj_scanning[str_symbol_name] = obj_scanned

                    while (len(self._gdbval_ptr_queue_arr) > 0): # 走査中に pointer 型が見つかった場合
                        
                        gdbval_ptr_processing_arr = self._gdbval_ptr_queue_arr # 
                        self._gdbval_ptr_queue_arr = []

                        # 走査中にみつかった pointer のアクセス先に対する走査ループ
                        for gdbval_pointer in gdbval_ptr_processing_arr:

                            str_located_symbol_name = self._func_get_symbol_name_from_addr(int(gdbval_pointer.cast(self._gdbtyp_address_length_uint))) #caution gdb の `info symbol addr` の実行結果をパースして無理やり求めている

                            if not(str_located_symbol_name is None): # シンボルが配置されている場合

                                gdbsym_a = gdb.lookup_symbol(str_located_symbol_name)[0] # gdb.Symbol を取得
                                
                                bool_already_scannced_status, bool_already_scannced = self._func_check_already_scanned(gdbsym_a, obj_scanning)

                                if not(bool_already_scannced_status) : # アドレス算出異常の場合
                                    return None # None を返して終了

                                if not(bool_already_scannced) : # symbol が見つかった & 走査済みでない場合
                                    obj_scanned = self._func_scan_gdb_sym(gdbsym_a)

                                    if (obj_scanned is None): # scan に失敗した場合
                                        return None # None を返して終了

                                    obj_scanning[str_located_symbol_name] = obj_scanned

        return obj_scanning

    # < completely same as gdbnaut.py >-----------------------------------------------------------------------------------------
    
    def _func_convert_to_list(self, target, str_arg_name):
        """
        指定オブジェクトを str list に変換する  
        変換不可能な場合は、 None を返す
        """
        
        if (target is None): # None は None のまま返す
            return None

        str_target_arr = []
        if (isinstance(target, tuple)) :
            target = list(target) # list に変更

        if (isinstance(target, list)) :
            for elem in target:
                if isinstance(elem, str):
                    if (len(elem) == 0): # 空文字列の場合
                        print(
                            "[warning] Empty string was found in `" + str_arg_name + "` argment. This will be ignored."
                        )

                    elif (elem in str_target_arr): # シンボル名の重複指定の場合
                        print(
                            "[warning] Duplicate difinition `" + elem + "` was found in `" + str_arg_name + "` argment. This will be ignored."
                        )

                    else: # シンボル名の重複指定でない場合
                        str_target_arr.append(elem)

                else: # string でない場合
                    print(
                        "[warning] Type `" + str(type(elem)) + "` (value:`" + str(elem) + "`) was specified as " + "\n" +
                        "[warning] element of `" + str_arg_name + "` argment. This will be ignored."
                    )

        elif (isinstance(target, str)) :
            if (len(target) == 0): # 空文字列の場合
                print(
                    "[warning] An empty string cannot be specified as `" + str_arg_name + "` argment."
                )
                return None

            else: # 空文字列でない場合
                str_target_arr.append(target)

        else: # Unknown type な場合
            print(
                "[warning] No valid string found in `" + str_arg_name + "` argment."
            )
            return None

        if (len(str_target_arr) == 0): #配列変換した結果、要素数が 0 の場合
            print(
                "[warning] No valid string found in `" + str_arg_name + "` argment."
            )
            return None

        return str_target_arr

    def _func_sort_copy(self, node, bool_sort):
        obj_to_return = None

        if isinstance(node, list):
            for obj_one_elem in node:
                obj_to_return = self._func_sort_copy(obj_one_elem, bool_sort)

        if isinstance(node, dict):
            lst_keys = []
            obj_to_return = collections.OrderedDict()
            for str_key, obj_one_elem in node.items():
                lst_keys.append(str_key)

            if(bool_sort):
                lst_keys.sort()

            for str_key in lst_keys:
                obj_to_return[str_key] = self._func_sort_copy(node[str_key], bool_sort)

        else:
            obj_to_return = node

        return obj_to_return

    def _func_scrape_copy(self, node, int_hierarchy_level, lst_attr, bool_scrape, bool_dump_only_1stL, bool_sort):

        obj_scraping = collections.OrderedDict()

        lst_keys = []
        for str_key, obj_val in node.items():
            lst_keys.append(str_key)

        if bool_sort :
            lst_keys.sort()

        for str_key in lst_keys:
            
            if   ( (str_key == "value") and (isinstance(node[str_key], list)) ):

                obj_scraped = []
                for obj_field_element in node[str_key]:
                    obj_scraped.append( self._func_scrape_copy(obj_field_element, int_hierarchy_level + 1, lst_attr, bool_scrape, bool_dump_only_1stL, bool_sort) )

                obj_scraping[str_key] = obj_scraped

            elif ( (str_key == "value") and (isinstance(node[str_key], dict)) ):

                lst_field_keys = []
                for obj_field_key, obj_field_val in node[str_key].items():
                    lst_field_keys.append(obj_field_key)

                if bool_sort:
                    lst_field_keys.sort()

                obj_scraped = collections.OrderedDict()
                for obj_field_key in lst_field_keys:
                    obj_scraped[obj_field_key] = self._func_scrape_copy(node[str_key][obj_field_key], int_hierarchy_level + 1, lst_attr, bool_scrape, bool_dump_only_1stL, bool_sort)

                obj_scraping[str_key] = obj_scraped

            else:

                bool_copy = True

                if (lst_attr is None) : # 属性指定なしの場合
                    bool_copy = True

                else: # 属性指定ありの場合
                    
                    if bool_scrape : # 指定属性を **削除** する指定の場合
                        
                        for str_attr in lst_attr: # 指定属性リストにマッチするかどうかチェックするループ
                            if (str_attr == str_key):
                                bool_copy = False
                                break
                        
                    else: # 指定属性を **残す** 指定の場合

                        bool_matched = False
                        for str_attr in lst_attr: # 指定属性リストにマッチするかどうかチェックするループ
                            if (str_attr == str_key):
                                bool_matched = True
                                break
                        
                        if not(bool_matched): # 指定属性リストにマッチしなかった場合
                            bool_copy = False
                
                if( (str_key == "dump")       and # 1階層目だけの memory dump を残す指定の場合
                    (bool_dump_only_1stL)     and
                    (int_hierarchy_level > 0)):
                    bool_copy = False

                if bool_copy:
                    obj_scraping[str_key] = self._func_sort_copy(node[str_key], bool_sort)

        return obj_scraping

    def _func_traverser(self, tpl_hierarchy, func_callback):

        obj_target = tpl_hierarchy[len(tpl_hierarchy)-1]
        
        func_callback(obj_target, tpl_hierarchy)

        if (obj_target["type_code"] == gdb.TYPE_CODE_ARRAY) : # array の場合
            
            for obj_value in obj_target["value"]: # list 要素を網羅

                self._func_traverser((tpl_hierarchy + (obj_value, )), func_callback)

        elif (obj_target["type_code"] in [ # member を持つ型の場合
            gdb.TYPE_CODE_STRUCT,
            gdb.TYPE_CODE_UNION,
        ]):
            for obj_value in obj_target["value"].values(): # dictionary の各値を網羅

                self._func_traverser((tpl_hierarchy + (obj_value, )), func_callback)

    def info(self, attr = None, scrape = False, dump_only_1stL = False, do_sort = False):
        """
        Returns scanning result as dictionary.
        This dictionary object will have hierarchy structure in case of
        scanned object represents `array`, `structure`, `union`, which has fields.
        In this case each field will be set in `value` attribute.

        Parameters
        ----------
        attr : str or tuple or list, default None
            Attribute name(s) to Leave. If None specified, all attributes will leave.
            If this argment specified as tuple or list, each element type must be str.
            
        scrape : bool, default False
            This argment evaluated only if `attr` is specified.
            If `True` was specified, specified attribute name(s) will be scraped.

        dump_only_1stL : bool, default False
            If `True` specified, memory dump image (which is represented as `dump` attribute)
            in the second and subsequent layers of scanning result will be deleted.

        do_sort: bool, default False
            If `True` specified, each attribute of dictionary will sort ascending order.

        Returns
        -------
        scanning_result : dict or None
            dict will returned when scanning has been done completely.
            So None will returned when scanning was failured.

        """

        if (self._obj_scanned is None): # self._obj_scanned が None の場合
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] No valid scanning result." + "\n"
            )
            return
        
        scanning_result = collections.OrderedDict()
        
        # 引数チェック
        attr = self._func_convert_to_list(attr, "attr")
        
        lst_scanned_keys = []
        for str_scanned_key, obj_scanned_val in self._obj_scanned.items():
            lst_scanned_keys.append(str_scanned_key)

        if do_sort:
            lst_scanned_keys.sort()

        for str_scanned_key in lst_scanned_keys:
            scanning_result[str_scanned_key] = self._func_scrape_copy(self._obj_scanned[str_scanned_key], 0, attr, scrape, dump_only_1stL, do_sort)
        
        return scanning_result
        
    def traverse(self, callback):
        """
        Visit each node of scanning result dictionary object and call callback function.

        Parameters
        ----------
        callback : function
            Callback function. This function must have following two argments.
            1st argment as dict  - Node that Traverser visited.
            2nd argment as tuple - Map that represents where is visited node is
                                   set in scanning result dictionary object.
        """

        if (self._obj_scanned is None): # self._obj_scanned が None の場合
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] No valid scanning result." + "\n"
            )
            return

        # wish callback が callable かどうかチェック
        # -> callable か、 inspect.isfunction
        # 
        # callback の引数定義をしらべる
        # -> getargspec か、 inspect.signature()
        #    getargspec は python3.X では非推奨
        #    inspect.signature() は Python 3.3 より前のバージョンでは組み込みではない
        #    https://blog.amedama.jp/entry/2016/10/31/225219

        try:
            for obj_scanned_val in self._obj_scanned.values():
                self._func_traverser((obj_scanned_val, ), callback)

        except Exception as e:
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] " + str(e) + "\n"
            )
            return

    def save_as(self, file_path, attr = None, scrape = False, dump_only_1stL = False, do_sort = False):
        """
        Save the scanning result as specified file path(name).

        Parameters
        ----------
        file_path : str
            File path (name)

        attr : str or tuple or list, default None
            Attribute name(s) to Leave. If None specified, all attributes will leave.
            If this argment specified as tuple or list, each element type must be str.
            
        scrape : bool, default False
            This argment evaluated only if `attr` is specified.
            If `True` was specified, specified attribute name(s) will be scraped.

        dump_only_1stL : bool, default False
            If `True` specified, memory dump image (which is represented as `dump` attribute)
            in the second and subsequent layers of scanning result will be deleted.

        do_sort: bool, default False
            If `True` specified, each attribute of dictionary will sort ascending order.

        """

        if (self._obj_scanned is None): # self._obj_scanned が None の場合
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] No valid scanning result." + "\n"
            )
            return

        # 引数チェック
        attr = self._func_convert_to_list(attr, "attr")
        
        try:
            obj_file = open(file_path, 'w')

        except Exception as e: #ファイルオープンに失敗した場合
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] " + str(e) + "\n"
            )
            return

        obj_scanned = self.info(attr = attr, scrape = scrape, dump_only_1stL = dump_only_1stL, do_sort = do_sort)
        str_scanned = json.dumps(obj_scanned, indent=4)

        obj_file.write(str_scanned)
        obj_file.close()

    # ----------------------------------------------------------------------------------------</ completely same as gdbnaut.py >

    def __init__(self, symbol):
        """
        Scan the object that pointed by specified symbol(s)

        Parameters
        ----------
        symbol : str or tuple or list
            Symbol name(s) that represent object to scanning.
            If this argment specified as tuple or list, each element type must be str.

        """

        # 引数チェック
        symbol = self._func_convert_to_list(symbol, "symbol")
        if(symbol is None):
            
            insobj_curframe_b_back = inspect.currentframe().f_back
            sys.stderr.write(
                "[error] No valid symbol specified." + "\n"
            )

            self._obj_scanned = None
            return
        
        self._gdbtyp_address_length_uint = self._func_get_address_length_uint()
        self._address_hex_format = self._get_address_hex_format()
        self._gdbifr_specified = gdb.selected_inferior()
        self._gdbval_ptr_queue_arr = [] # scan 中に pointer 型の gdb.Value が見つかった場合は、
                                        # この list に queue される
        self._obj_scanned = self._func_scan(symbol)
