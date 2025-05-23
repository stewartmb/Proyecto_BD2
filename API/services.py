import json
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Format_Meta import *
from Utils.file_format import *
from Heap_struct.Heap import *
from Hash_struct.Hash import Hash
from BPtree_struct.Indice_BPTree_file import BPTree as Btree
from Sequential_Struct.Indice_Sequential_file import Sequential
from RTree_struct.RTreeFile_Final import RTreeFile as Rtree

def to_struct(type):
    varchar_match = re.match(r"varchar\[(\d+)\]", type)

    if type == "int":
        return "i"
    if type == "double":
        return "d"
    elif varchar_match:
        size = varchar_match.group(1)  # Extraemos el tamaño entre los corchetes
        return f"{size}s"
    else:
        print("ERROR: tipo no soportado")
        return None


def convert(query):
    print(json.dumps(query, indent=2))
    if query["action"] == "create_table":
        create_table(query)
    elif query["action"] == "insert":
        insert(query)
    elif query["action"] == "select":
        print("Y")
    elif query["action"] == "delete":
        print("Z")
    elif query["action"] == "index":
        create_index(query)
    elif query["action"] == "copy":
        print("B")
    else:
        print("error")

def create_table(query):
    # crear tabla y añadir a metadata
    with open(table_filename(query["name"]), "w") as f:
        pass
    create(query["data"], query["name"])
    format = {}
    cols = query["data"]["columns"]
    for key in cols.keys():
        format[key] = to_struct(cols[key]["type"])

    # crear indices
    for key in cols.keys():
        index = cols[key]["index"]
        if index == None:
            pass
        elif index == "hash":
            hash = Hash(format,
                        key,
                        index_filename(query["name"], key, "buckets"),
                        index_filename(query["name"], key, "index"),
                        table_filename(query["name"]))
        elif index == "seq":
            seq = Sequential(format,
                        key,
                        index_filename(query["name"], key, "index"),
                        table_filename(query["name"]))

        elif index == "btree":
            btree = Btree(format,
                            key,
                            index_filename(query["name"], key, "index"),
                            table_filename(query["name"]),
                            4)

        else:
            print("INDICE NO IMPLEMENTADO AUN")

def insert(query):
    nombre_tabla = query["table"]
    data = select(nombre_tabla)
    format = {}
    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    # insertar en tabla
    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

    position = heap.insert(query["values"][1])

    # insertar en cada indice si existe
    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        if index == None:
            pass
        elif index == "hash":
            hash = Hash(format,
                        key,
                        index_filename(nombre_tabla, key, "buckets"),
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla))

            hash.insert(query["values"][1], position)
        elif index == "seq":
            seq = Sequential(format,
                        key,
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla))

            seq.add(query["values"][1], position)

    # indice compuesto en rtree, añadir en el indice
    rtree_keys = data.get("indexes", {}).get("rtree")
    if rtree_keys is not None:
        rtree = Rtree(format, 
                    data["key"],
                    rtree_keys, 
                    table_filename(nombre_tabla),  
                    index_filename(nombre_tabla, *rtree_keys, "index"))
        rtree.insert(query["values"][1], position)

def create_index(query):
    nombre_tabla = query["table"]
    data = select(nombre_tabla)
    format = {}

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    for key in query["attr"]:
        data["columns"][key]["index"] = query["index"]
    
    create(data, nombre_tabla)
    
    keys = query["attr"]

    hash = None
    seq = None
    rtree = None
    bptree = None
    isam = None

    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))
    
    index = query["index"]
    if index == "hash":
        hash = Hash(format,
                    keys[0],
                    index_filename(nombre_tabla, keys[0], "buckets"),
                    index_filename(nombre_tabla, keys[0], "index"),
                    table_filename(nombre_tabla))
    elif index == "seq":
        seq = Sequential(format,
                    key,
                    index_filename(nombre_tabla, keys[0], "index"),
                    table_filename(nombre_tabla))
    elif index == "rtree":
        rtree = Rtree(format, 
                        data["key"],
                        keys, 
                        table_filename(nombre_tabla),  
                        index_filename(nombre_tabla, *keys, "index"))
        if "indexes" not in data:
            data["indexes"] = {}
        data["indexes"]["rtree"] = keys
    else:
        print("INDICE NO IMPLEMENTADO AUN")

    create(data, nombre_tabla)

    records = heap._select_all()

    # añadir los registros ya en la tabla al indice creado
    for record in records:
        if hash is not None:
            hash.insert(record)
        elif seq is not None:
            seq.add(record)
        elif rtree is not None:
            rtree.insert(record)
    
    