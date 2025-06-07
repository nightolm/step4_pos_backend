from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import mysql.connector

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ##allow_origins=["https://app-step4-1.azurewebsites.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データ構造
class TransactionItem(BaseModel):
    code: str
    name: str
    price: int

class Transaction(BaseModel):
    emp_cd: str
    store_cd: str
    pos_no: str
    items: List[TransactionItem]

# DB接続用ヘルパー

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

# 商品情報を取得
@app.get("/products/{code}")
def get_product(code: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT code, name, price FROM product_master WHERE code = %s", (code,))
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 取引を登録
@app.post("/transactions")
def create_transaction(trn: Transaction):
    total = sum(item.price for item in trn.items)
    # TODO: DBに取引を登録する実装
    return {"success": True, "total": total}
