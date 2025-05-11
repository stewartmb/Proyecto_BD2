from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from ParserSQL.parser import parse
import Utils.Format_Meta as meta 

app = FastAPI()


class TextoInput(BaseModel):
    texto: str

class QueryInput(BaseModel):
    query: str

@app.post("/test")
def guardar_texto_a_archivo(input: TextoInput):
    with open('test.dat', 'w') as f:
        f.write(input.texto)
    return JSONResponse(content={"mensaje": "Texto guardado correctamente."})

@app.post("/query")
def execute_query(input: QueryInput):
    parsed_query = parse(input.query)
    return JSONResponse(execute(parsed_query[0]))

def execute(query):
    if query["action"] == "create_table":
        print(query)
        create_table(query)
        return f"created table {query["name"]}"
    elif query["action"] == "copy":
        print(query)
        return copy_stmt(query)
    elif query["action"] == "select":
        print(query)
        return select_stmt(query)
    elif query["action"] == "delete":
        print(query)
        return delete_stmt(query)
    elif query["action"] == "index":
        print(query)
        return index_stmt(query)
    else:
        raise HTTPException(status_code=400, detail="Instruction not recognized")

    
def create_table(input): # TODO
    print("create")

    # call sequential create

    # add table to metadata
    meta.create(input["data"], input["name"])

    # create indexes
    for name, info in input["data"]["columns"].items():
        if (info["index"] is not None):
            filename = f"{name}_{input["name"]}_{info["index"]}.bin"
            # if (info["index"] == "seq"):
            #     create_index_sequential(key=name, filename=filename)
            # elif (info["index" == "hash"]):
            #     create_index_hash(key=name, filename=filename)
            # elif (info["index" == "isam"]):
            #     create_index_isam(key=name, filename=filename)
            # elif (info["index"] == "btree"):
            #     create_index_btree(key=name, filename=filename)
            # elif (info["index"] == "rtree"):
            #     create_index_rtree(key=name, filename=filename)
            # else:
            #     raise HTTPException(status_code=400, detail="Index not recognized")

    return input

def copy_stmt(input):
    # TODO
    return "loaded"

def select_stmt(input):
    # TODO
    return "result"

def delete_stmt(input):
    # TODO
    return "deleted"

def index_stmt(input):
    # TODO
    return "index"