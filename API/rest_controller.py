from fastapi import FastAPI
import os
import sys
from lark import Lark
from pydantic import BaseModel
from fastapi.responses import JSONResponse
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from ParserSQL.parser import *
import services

app = FastAPI()
parser = Lark(sql_grammar, start='start', parser='lalr', transformer=SQLTransformer())

class QueryInput(BaseModel):
    query: str

#@app.post("/query")
def parse_sql_query(input: QueryInput):
    sql_code = input.query
    try:
        result = parser.parse(sql_code)
    except Exception as e:
        print("ERROR:", e)
        return JSONResponse(
            content={"error": "Error parsing input", "details": str(e)},
            status_code=400
        )
    for line in result:
        if isinstance(line, list):
            services.convert(line[0])
        else:
            services.convert(line)

print("comenzar")

consultas = ["", "", "", ""]
consultas[0]= "API/consultas/crear_tabla.txt"
consultas[1]= "API/consultas/crear_indice.txt"
consultas[2]= "API/consultas/insertar_datos.txt"
# consultas[3]= "API/consultas/select_datos.txt"


for c in consultas:
    if c != "":
        with open(c, "r") as f:
            sql_code = f.read()

        test_query = QueryInput(
            query=sql_code
        )
        parse_sql_query(test_query)

print("terminar")