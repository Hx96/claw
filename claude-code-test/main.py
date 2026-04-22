"""FastAPI 主入口"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
from database import get_db, init_db

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Items API",
    description="一个简单的项目管理系统 REST API",
    version="1.0.0",
)


# 应用启动时初始化数据库
@app.on_event("startup")
def startup():
    init_db()


# ---------- 路由 ----------

@app.get("/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}


@app.get("/items", tags=["项目"], response_model=list[models.ItemResponse])
def get_items(db: Session = Depends(get_db)):
    """获取所有项目"""
    items = db.query(models.Item).order_by(models.Item.created_at.desc()).all()
    return items


@app.post(
    "/items",
    tags=["项目"],
    response_model=models.ItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": models.ErrorResponse, "description": "请求参数校验失败"},
    },
)
def create_item(item: models.ItemCreate, db: Session = Depends(get_db)):
    """创建新项目"""
    db_item = models.Item(
        name=item.name,
        description=item.description,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get(
    "/items/{item_id}",
    tags=["项目"],
    response_model=models.ItemResponse,
    responses={
        404: {"model": models.ErrorResponse, "description": "项目不存在"},
    },
)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """获取单个项目"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 ID {item_id} 不存在",
        )
    return db_item


# ---------- 运行入口 ----------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
