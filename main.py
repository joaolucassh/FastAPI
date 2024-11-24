from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

app = FastAPI()


class Cliente(BaseModel):
    id: int
    nome: str = Field(..., max_length=20)
    tipo_atendimento: str = Field(..., pattern="^[NP]$")  # Alterado para 'pattern' ao invés de 'regex'
    data_chegada: datetime
    atendido: bool = False


fila: List[Cliente] = []


def atualizar_posicoes():
    for index, cliente in enumerate(fila):
        cliente.id = index + 1


@app.get("/fila", response_model=List[Cliente])
async def get_fila():
    nao_atendidos = [cliente for cliente in fila if not cliente.atendido]
    return nao_atendidos


@app.get("/fila/{id}", response_model=Cliente)
async def get_cliente(id: int):
    for cliente in fila:
        if cliente.id == id:
            return cliente
    raise HTTPException(status_code=404, detail="Cliente não encontrado na fila")


@app.post("/fila", response_model=Cliente)
async def adicionar_cliente(nome: str, tipo_atendimento: str):
    if len(nome) > 20:
        raise HTTPException(status_code=400, detail="O nome deve ter no máximo 20 caracteres")
    if tipo_atendimento not in ["N", "P"]:
        raise HTTPException(status_code=400, detail="O tipo de atendimento deve ser 'N' ou 'P'")

    data_chegada = datetime.now()
    novo_cliente = Cliente(
        id=len(fila) + 1,
        nome=nome,
        tipo_atendimento=tipo_atendimento,
        data_chegada=data_chegada
    )
    if tipo_atendimento == "P":
        fila.insert(0, novo_cliente)  # Prioridade vai ao início
    else:
        fila.append(novo_cliente)  # Normal vai ao final
    atualizar_posicoes()
    return novo_cliente


@app.put("/fila", response_model=List[Cliente])
async def atualizar_fila():
    global fila
    fila = [cliente for cliente in fila if not cliente.atendido]  # Remove clientes atendidos
    atualizar_posicoes()  # Reorganiza os IDs
    return fila


@app.delete("/fila/{id}")
async def deletar_cliente(id: int):
    global fila
    cliente_encontrado = False
    for cliente in fila:
        if cliente.id == id:
            cliente_encontrado = True
            fila.remove(cliente)
            break
    if not cliente_encontrado:
        raise HTTPException(status_code=404, detail="Cliente não encontrado na fila")
    atualizar_posicoes()
    return {"message": "Cliente removido da fila com sucesso"}








