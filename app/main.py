from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じてVercelのURLに絞ってもOK
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
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# 商品情報を取得
@app.get("/products/{code}")
def get_product(code: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT code, name, price FROM prd WHERE TRIM(code) = %s", (code,))
        ##cursor.execute("SELECT code, name, price FROM prd WHERE code = %s", (code,))
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
    # TODO: Supabase側に insert 処理を追加（必要に応じて）
    return {"success": True, "total": total}
