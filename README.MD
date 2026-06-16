# 写字楼租赁管理系统

FastAPI + Vue 3 实现的写字楼租赁管理系统，覆盖工位管理、租赁合同签订、费用收缴、到期提醒和运营看板。

## 功能

- 工位管理：新增工位、按状态筛选、查看区域/楼层/座位/月租金/配套。
- 合同签订：选择可租工位签订合同，自动将工位置为已租。
- 费用收缴：创建租金账单，确认收款，自动识别逾期账单。
- 到期提醒：查看 30 天内到期合同和逾期未收账单。
- 运营看板：统计总工位、可租工位、履行合同、待收金额、逾期金额、即将到期合同。

## 项目结构

```text
.
├── backend
│   ├── app
│   │   ├── api/routes      # API 路由模块
│   │   ├── core            # 配置
│   │   ├── db              # 数据库会话和初始化
│   │   ├── models          # SQLAlchemy 模型
│   │   ├── schemas         # Pydantic 入参/出参
│   │   └── services        # 业务逻辑
│   ├── Dockerfile
│   └── requirements.txt
├── frontend
│   ├── src
│   │   ├── api             # 前端 API 客户端
│   │   ├── components      # 通用组件
│   │   ├── styles          # 全局样式
│   │   ├── utils           # 格式化工具
│   │   └── views           # 业务页面
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Docker 启动

```bash
docker compose up --build
```

访问地址：

- 前端：http://127.0.0.1:5173
- 后端健康检查：http://127.0.0.1:8000/health
- API 文档：http://127.0.0.1:8000/docs

SQLite 数据库通过 Docker volume `backend-data` 持久化。

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

如果后端地址不是 `http://127.0.0.1:8000/api`，可设置：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api npm run dev
```

## 主要接口

- `GET /api/dashboard/stats`
- `GET /api/workstations`
- `POST /api/workstations`
- `GET /api/contracts`
- `POST /api/contracts`
- `GET /api/payments`
- `POST /api/payments`
- `POST /api/payments/{payment_id}/mark-paid`
- `GET /api/reminders/expiring-contracts`
- `GET /api/reminders/overdue-payments`
