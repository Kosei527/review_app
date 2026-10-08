from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Knowledge(BaseModel):
    domain: str
    recap: str
    why: str
    generalization: str

def init_db():
    conn = sqlite3.connect("review.db") #dbに接続
    cur = conn.cursor() #カーソルを作る
    cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            recap TEXT,
            why TEXT,
            generalization TEXT,
            date TEXT
        )
    """)
    conn.commit() #変更を確定する
    conn.close() #接続を閉じる

init_db() #()このかっこがつくことが実行の合図

@app.get("/")
def top():
    return {"message": "hello"}

@app.post("/save")
def save(domain: str = Form(), recap: str = Form(), why: str = Form(), generalization: str = Form()): #引数を一つだけでなく、四つに分けることでフォームエンコード形式に対応させる
    conn = sqlite3.connect("review.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO knowledge (domain, recap, why, generalization, date) VALUES (?,?,?,?,?)",
        (domain,recap,why,generalization,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    return {"result": "saved"}
#HTMLフォームはフォームエンコード形式で送るので、JSON前提のPydanticモデルではなく、Form()で受け取る

@app.get("/list")
def listup():
    conn = sqlite3.connect("review.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM knowledge")
    rows = cur.fetchall()
    conn.close()
    row_result = []
    for r in rows:
        row_result.append(dict(r))
    return row_result #生JSON、{"キー":"値"} の形式のデータ

@app.get("/search")
def search(keyword: str):
    conn = sqlite3.connect("review.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM knowledge WHERE domain = ?",(keyword,)) #値を取り出す
    rows = cur.fetchall() #結果を持ってくる
    conn.close()
    s_result = []
    for r in rows:
        s_result.append(dict(r)) #dictで辞書に変換　FastAPIはRowという型をJSONにできないから 
    return s_result

@app.get("/save-form")
def save_form():
    return FileResponse("static/save.html")

@app.get("/list-page")
def listpage(request: Request, keyword: str =""): #TemplateResponseを使うときに必要、決まり事
    conn = sqlite3.connect("review.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if keyword == "":
        cur.execute("SELECT * FROM knowledge")
    else:
        cur.execute("SELECT * FROM knowledge WHERE  domain = ?",(keyword,))
    rows = cur.fetchall()
    conn.close()
    return templates.TemplateResponse(request, "list.html", {"rows": rows}) #list.htmlにrowsを渡し、Jinja2に処理させてる dict変換は不必要