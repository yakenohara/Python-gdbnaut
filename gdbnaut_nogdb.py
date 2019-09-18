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

import json

class gdb:
    TYPE_CODE_PTR                  =  1
    TYPE_CODE_ARRAY                =  2
    TYPE_CODE_STRUCT               =  3
    TYPE_CODE_UNION                =  4
    TYPE_CODE_ENUM                 =  5
    TYPE_CODE_FLAGS                =  6
    TYPE_CODE_FUNC                 =  7
    TYPE_CODE_INT                  =  8
    TYPE_CODE_FLT                  =  9
    TYPE_CODE_VOID                 = 10
    TYPE_CODE_SET                  = 11
    TYPE_CODE_RANGE                = 12
    TYPE_CODE_STRING               = 13
    TYPE_CODE_BITSTRING            =-1
    TYPE_CODE_ERROR                = 14
    TYPE_CODE_METHOD               = 15
    TYPE_CODE_METHODPTR            = 16
    TYPE_CODE_MEMBERPTR            = 17
    TYPE_CODE_REF                  = 18
    TYPE_CODE_RVALUE_REF           = 19
    TYPE_CODE_CHAR                 = 20
    TYPE_CODE_BOOL                 = 21
    TYPE_CODE_COMPLEX              = 22
    TYPE_CODE_TYPEDEF              = 23
    TYPE_CODE_NAMESPACE            = 24
    TYPE_CODE_DECFLOAT             = 25
    TYPE_CODE_INTERNAL_FUNCTION    = 27

class SymbolInfo:

    # < completely same as gdbnaut.py >-----------------------------------------------------------------------------------------
    
    def _func_convert_to_list(self, target):
        str_target_arr = []
        if (isinstance(target, tuple)) :
            target = list(target) # list に変更

        if (isinstance(target, list)) :
            for elem in target:
                if isinstance(elem, str):
                    if (elem in str_target_arr): # シンボル名の重複指定の場合
                        #todo warn
                        pass

                    else: # シンボル名の重複指定でない場合
                        str_target_arr.append(elem)

                else: # string でない場合
                    #todo warn
                    pass

        elif (isinstance(target, str)) :
            str_target_arr.append(target)

        else: # Unknown type な場合
            #todo warn
            return None

        return str_target_arr

    def _func_sort_copy(self, node, bool_sort):
        obj_to_return = None

        if isinstance(node, list):
            for obj_one_elem in node:
                obj_to_return = self._func_sort_copy(obj_one_elem, bool_sort)

        if isinstance(node, dict):
            lst_keys = []
            obj_to_return = {}
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

        obj_scraping = {}

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

                obj_scraped = {}
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

        scanning_result = {}
        
        # 引数チェック
        attr = self._func_convert_to_list(attr)
        if(attr is None):
            #todo warn
            pass
        
        elif(len(attr) == 0): # シンボル名の指定が 1つもない場合
            attr = None

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

        #todo callback が callable かどうかチェック(callable? inspect.isfunction?)
        
        #todo self._obj_scanned が None の場合

        for obj_scanned_val in self._obj_scanned.values():
            self._func_traverser((obj_scanned_val, ), callback)

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

        # 引数チェック
        attr = self._func_convert_to_list(attr)
        if(attr is None):
            #todo warn
            pass
        
        elif(len(attr) == 0): # シンボル名の指定が 1つもない場合
            attr = None

        #todo ファイルアクセスチェック
        obj_file = open(file_path, 'w')

        obj_scanned = self.info(attr = attr, scrape = scrape, dump_only_1stL = dump_only_1stL, do_sort = do_sort)
        str_scanned = json.dumps(obj_scanned, indent=4)

        obj_file.write(str_scanned)
        obj_file.close()

    # ----------------------------------------------------------------------------------------</ completely same as gdbnaut.py >

    def __init__(self, scanned_result):
        """
        Import Scanned result object which have been exported by gdbnaut.SymbolInfo.

        Parameters
        ----------
        scanned_result : str or dict
            If you have a exported file which have been generated by
            `.save_as(file_path)` method of `gdbnaut.SymbolInfo` class,
            you can specify generated file path as str.
            Or if you have a dictionary object which have been generated by
            `.info()` method of `gdbnaut.SymbolInfo` class,
            you can specify that dictionary object directly as this argment.
            Otherwise, this method will be end in failure.

        """
        
        if isinstance(scanned_result, str):
            
            #todo 開けなかった時
            obj_file = open(scanned_result, 'r')

            #todo dictionary に出来なかった時
            obj_scanned = json.load(obj_file)
            obj_file.close()
            self._obj_scanned = obj_scanned

        elif isinstance(scanned_result, dict):
            self._obj_scanned = scanned_result

        else:
            #todo warn
            self._obj_scanned = None
