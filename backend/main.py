from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import require_auth, router as auth_router
from api.backtests.backtests import router as backtests_router
from api.bots.bots import router as bots_router
from api.strategies.strategies import router as strategies_router
from api.users.users import router as users_router
from db.seed import seed_defaults
from executor.MultithreadExecutor import MultithreadExecutor
from executor.runtime_registry import BotRuntimeRegistry
from strategies.implementation.MockStrategy import MockStrategy
import threading
from executor.Bot import Bot

def init_bot_runtime_registry() -> BotRuntimeRegistry:
    executor = MultithreadExecutor()
    mock_strategy = MockStrategy(required_symbols=2)
    bot = Bot(name="MockBot", strategy=mock_strategy, symbols=["AAPL", "GOOG"])
    executor.add_bot(bot)
    executor.start()
    threading.Thread(target=executor.run, daemon=True).start()
    return executor


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(strategies_router, dependencies=[Depends(require_auth)])
app.include_router(users_router, dependencies=[Depends(require_auth)])
app.include_router(bots_router, dependencies=[Depends(require_auth)])
app.include_router(backtests_router, dependencies=[Depends(require_auth)])

@app.get("/", dependencies=[Depends(require_auth)])
async def root():
    return {"message": "Hello World"}


@app.on_event("startup")
def on_startup() -> None:
    seed_defaults()
    app.state.bot_runtime_registry = init_bot_runtime_registry()
    