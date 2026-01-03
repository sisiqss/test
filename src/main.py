import argparse
import asyncio
import json
import traceback
import logging
from typing import Any, Dict, Iterable, AsyncIterable, AsyncGenerator, Optional
import threading
import contextvars
import cozeloop
import uvicorn
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from coze_coding_utils.runtime_ctx.context import new_context, Context
from utils.helper import graph_helper
from utils.log.node_log import LOG_FILE
from utils.log.write_log import setup_logging, request_context
from utils.log.config import LOG_LEVEL
from utils.messages.server import (
    create_message_end_dict,
    create_message_error_dict,
    MESSAGE_END_CODE_CANCELED,
)

setup_logging(
    log_file=LOG_FILE,
    max_bytes=100 * 1024 * 1024, # 100MB
    backup_count=5,
    log_level=LOG_LEVEL,
    use_json_format=True,
    console_output=True
)

logger = logging.getLogger(__name__)
from utils.helper.agent_helper import (
    to_stream_input,
    to_client_message,
    agent_iter_server_messages,
)
from utils.log.parser import LangGraphParser
from utils.log.err_trace import extract_core_stack
from utils.log.loop_trace import init_run_config, init_agent_config


# 超时配置常量
TIMEOUT_SECONDS = 900  # 15分钟

class GraphService:
    def __init__(self):
        if not graph_helper.is_agent_proj():
            self.graph = graph_helper.get_graph_instance("graphs.graph")

        # 用于跟踪正在运行的任务（使用asyncio.Task）
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    
    def _get_graph(self, ctx=Context):
        if graph_helper.is_agent_proj():
            return graph_helper.get_agent_instance("agents.agent", ctx)
        else:
            return self.graph
    
    
    @staticmethod
    def _sse_event(data: Any) -> str:
        return f"event: message\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"

    # 流式运行（原始迭代器）：本地调用使用
    def stream(self, payload: Dict[str, Any], run_config: RunnableConfig, ctx=Context) -> Iterable[Any]:
        client_msg, session_id = to_client_message(payload)
        run_config["recursion_limit"] = 100
        run_config["configurable"] = {"thread_id": session_id}
        stream_input = to_stream_input(client_msg)
        t0 = time.time()
        try:
            items = self._get_graph(ctx).stream(stream_input, stream_mode="messages", config=run_config, context=ctx)
            server_msgs_iter = agent_iter_server_messages(
                items,
                session_id=client_msg.session_id,
                query_msg_id=client_msg.local_msg_id,
                local_msg_id=client_msg.local_msg_id,
                run_id=ctx.run_id,
                log_id=ctx.logid,
            )
            for sm in server_msgs_iter:
                yield sm.dict()
        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for run_id: {ctx.run_id}")
            end_msg = create_message_end_dict(
                code=MESSAGE_END_CODE_CANCELED,
                message="Stream execution cancelled",
                session_id=client_msg.session_id,
                query_msg_id=client_msg.local_msg_id,
                log_id=ctx.logid,
                time_cost_ms=int((time.time() - t0) * 1000),
                reply_id="",
                sequence_id=1,
            )
            yield end_msg
            raise
        except Exception as ex:
            error_msg = create_message_error_dict(
                code="exception",
                message=str(ex),
                session_id=client_msg.session_id,
                query_msg_id=client_msg.local_msg_id,
                log_id=ctx.logid,
                reply_id="",
                sequence_id=1,
                local_msg_id=client_msg.local_msg_id,
            )
            yield error_msg

    # 同步运行：本地/HTTP 通用
    async def run(self, payload: Dict[str, Any], ctx=None) -> Dict[str, Any]:
        if ctx is None:
            ctx = new_context("run")

        run_id = ctx.run_id
        logger.info(f"Starting run with run_id: {run_id}")

        try:
            graph = self._get_graph(ctx)
            # custom tracer
            run_config = init_run_config(graph, ctx)
            run_config["configurable"] = {"thread_id": ctx.run_id}

            # 直接调用，LangGraph会在当前任务上下文中执行
            # 如果当前任务被取消，LangGraph的执行也会被取消
            return await graph.ainvoke(payload, config=run_config, context=ctx)

        except asyncio.CancelledError:
            logger.info(f"Run {run_id} was cancelled")
            return {"status": "cancelled", "run_id": run_id, "message": "Execution was cancelled"}
        except Exception as e:
            # 记录详细的错误信息和堆栈跟踪
            logger.error(f"Error in GraphService.run: {str(e)}\nTraceback:\n{extract_core_stack()}")
            # 重新抛出异常，让上层捕获并处理
            raise
        finally:
            # 清理任务记录
            self.running_tasks.pop(run_id, None)

    # 流式运行（SSE 格式化）：HTTP 路由使用
    async def stream_sse(self, payload: Dict[str, Any], ctx=None) -> AsyncGenerator[str, None]:
        if ctx is None:
            ctx = new_context(method="stream_sse")

        run_id = ctx.run_id
        logger.info(f"Starting stream with run_id: {run_id}")
        graph = self._get_graph(ctx)
        if graph_helper.is_agent_proj():
            run_config = init_agent_config(graph, ctx)
        else:
            run_config = init_run_config(graph, ctx)  # vibeflow

        try:
            async for chunk in self.astream(payload, graph, run_config=run_config, ctx=ctx):
                yield self._sse_event(chunk)
        finally:
            # 清理任务记录
            self.running_tasks.pop(run_id, None)
            cozeloop.flush()

    # 取消执行 - 使用asyncio的标准方式
    def cancel_run(self, run_id: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        取消指定run_id的执行

        使用asyncio.Task.cancel()来取消任务,这是标准的Python异步取消机制。
        LangGraph会在节点之间检查CancelledError,实现优雅的取消。
        """
        logger.info(f"Attempting to cancel run_id: {run_id}")

        # 查找对应的任务
        if run_id in self.running_tasks:
            task = self.running_tasks[run_id]
            if not task.done():
                # 使用asyncio的标准取消机制
                # 这会在下一个await点抛出CancelledError
                task.cancel()
                logger.info(f"Cancellation requested for run_id: {run_id}")
                return {
                    "status": "success",
                    "run_id": run_id,
                    "message": "Cancellation signal sent, task will be cancelled at next await point"
                }
            else:
                logger.info(f"Task already completed for run_id: {run_id}")
                return {
                    "status": "already_completed",
                    "run_id": run_id,
                    "message": "Task has already completed"
                }
        else:
            logger.warning(f"No active task found for run_id: {run_id}")
            return {
                "status": "not_found",
                "run_id": run_id,
                "message": "No active task found with this run_id. Task may have already completed or run_id is invalid."
            }

    # 运行指定节点：本地/HTTP 通用
    async def run_node(self, node_id: str, payload: Dict[str, Any], ctx=None) -> Any:
        if ctx is None or Context.run_id == "":
            ctx = new_context(method="node_run")

        node_func, input_cls, output_cls = graph_helper.get_graph_node_func_with_inout(self.graph.get_graph(), node_id)
        if node_func is None or input_cls is None:
            raise KeyError(f"node_id '{node_id}' not found")
        assert self.graph is not None, "Graph is not initialized"
        parser = LangGraphParser(self.graph)
        metadata = parser.get_node_metadata(node_id) or {}

        _g = StateGraph(input_cls, input_schema=input_cls, output_schema=output_cls)
        _g.add_node("sn", node_func, metadata=metadata)
        _g.set_entry_point("sn")
        _g.add_edge("sn", END)
        _graph = _g.compile()

        run_config = init_run_config(_graph, ctx)
        return await _graph.ainvoke(payload, config=run_config)

    # 获取工作流的出入参Schema
    def graph_inout_schema(self) -> Any:
        if graph_helper.is_agent_proj():
            return {"input_schema": {}, "output_schema": {}}
        _graph_input = self.graph.get_input_schema()
        _graph_output = self.graph.get_output_schema()

        return {"input_schema": _graph_input.model_json_schema(), "output_schema": _graph_output.model_json_schema()}

    async def astream(self, payload: Dict[str, Any], graph: CompiledStateGraph, run_config: RunnableConfig, ctx=Context) -> AsyncIterable[Any]:
        client_msg, session_id = to_client_message(payload)
        run_config["recursion_limit"] = 100
        run_config["configurable"] = {"thread_id": session_id}
        stream_input = to_stream_input(client_msg)

        # 使用后台线程拉取同步流，并通过事件循环安全地推送到异步队列
        loop = asyncio.get_running_loop()
        q: asyncio.Queue = asyncio.Queue()
        context = contextvars.copy_context()
        start_time = time.time()
        def producer():
            try:
                items = graph.stream(stream_input, stream_mode="messages", config=run_config, context=ctx)
                server_msgs_iter = agent_iter_server_messages(
                    items,
                    session_id=client_msg.session_id,
                    query_msg_id=client_msg.local_msg_id,
                    local_msg_id=client_msg.local_msg_id,
                    run_id=ctx.run_id,
                    log_id=ctx.logid,
                )
                last_seq = 0
                for sm in server_msgs_iter:
                    # 主动检查执行时间，及时中断
                    if time.time() - start_time > TIMEOUT_SECONDS:
                        logger.error(f"Agent execution timeout after {TIMEOUT_SECONDS}s for run_id: {ctx.run_id}")
                        timeout_msg = create_message_end_dict(
                            code="TIMEOUT",
                            message=f"Execution timeout: exceeded {TIMEOUT_SECONDS} seconds",
                            session_id=client_msg.session_id,
                            query_msg_id=client_msg.local_msg_id,
                            log_id=ctx.logid,
                            time_cost_ms=int((time.time() - start_time) * 1000),
                            reply_id=getattr(sm, 'reply_id', ''),
                            sequence_id=last_seq + 1,
                        )
                        loop.call_soon_threadsafe(q.put_nowait, timeout_msg)
                        return
                    loop.call_soon_threadsafe(q.put_nowait, sm.dict())
                    last_seq = sm.sequence_id
            except Exception as ex:
                end_msg = create_message_end_dict(
                    code="exception",
                    message=str(ex),
                    session_id=client_msg.session_id,
                    query_msg_id=client_msg.local_msg_id,
                    log_id=ctx.logid,
                    time_cost_ms=int((time.time() - start_time) * 1000),
                    reply_id="",
                    sequence_id=last_seq + 1,
                )
                loop.call_soon_threadsafe(q.put_nowait, end_msg)
            finally:
                loop.call_soon_threadsafe(q.put_nowait, None)

        threading.Thread(target=lambda: context.run(producer), daemon=True).start()

        try:
            while True:
                item = await q.get()
                if item is None:
                    break
                yield item
        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for run_id: {ctx.run_id}")
            raise


service = GraphService()
app = FastAPI()

# 挂载静态文件服务
import os
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 根路径重定向到首页
@app.get("/", response_class=HTMLResponse)
async def get_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>职场情绪充电站</title></head>
        <body>
            <h1>欢迎来到职场情绪充电站</h1>
            <p>静态文件未找到，请检查static目录。</p>
        </body>
    </html>
    """

# API端点：将/stream_run映射到/api/stream，方便前端调用
@app.post("/api/stream")
async def api_stream(request: Request):
    return await http_stream_run(request)


@app.post("/run")
async def http_run(request: Request) -> Dict[str, Any]:
    global result
    raw_body = await request.body()
    try:
        body_text = raw_body.decode("utf-8")
    except Exception as e:
        body_text = str(raw_body)
        raise HTTPException(status_code=400,
                            detail=f"Invalid JSON format: {body_text}, traceback: {traceback.format_exc()}, error: {e}")

    ctx = new_context(method="run", headers=request.headers)
    run_id = ctx.run_id
    request_context.set(ctx)

    logger.info(
        f"Received request for /run: "
        f"run_id={run_id}, "
        f"query={dict(request.query_params)}, "
        f"body={body_text}"
    )

    try:
        payload = await request.json()

        # 创建任务并记录 - 这是关键，让我们可以通过run_id取消任务
        task = asyncio.create_task(service.run(payload, ctx))
        service.running_tasks[run_id] = task

        try:
            result = await asyncio.wait_for(task, timeout=float(TIMEOUT_SECONDS))
        except asyncio.TimeoutError:
            logger.error(f"Run execution timeout after {TIMEOUT_SECONDS}s for run_id: {run_id}")
            task.cancel()
            try:
                result = await task
            except asyncio.CancelledError:
                return {
                    "status": "timeout", 
                    "run_id": run_id, 
                    "message": f"Execution timeout: exceeded {TIMEOUT_SECONDS} seconds"
                }

        if not result:
            result = {}
        if isinstance(result, dict):
            result["run_id"] = run_id
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in http_run: {e}, traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format, {extract_core_stack()}")

    except asyncio.CancelledError:
        logger.info(f"Request cancelled for run_id: {run_id}")
        result = {"status": "cancelled", "run_id": run_id, "message": "Execution was cancelled"}
        return result

    except Exception as e:
        logger.error(f"Unexpected error in http_run: {e}, traceback: {traceback.format_exc()}", exc_info=True)
        raise HTTPException(status_code=500, detail=extract_core_stack())
    finally:
        cozeloop.flush()


@app.post("/stream_run")
async def http_stream_run(request: Request):
    ctx = new_context(method="stream_run", headers=request.headers)
    request_context.set(ctx)
    raw_body = await request.body()
    try:
        body_text = raw_body.decode("utf-8")
    except Exception as e:
        body_text = str(raw_body)
        raise HTTPException(status_code=400,
                            detail=f"Invalid JSON format: {body_text}, traceback: {extract_core_stack()}, error: {e}")

    run_id = ctx.run_id
    logger.info(
        f"Received request for /stream_run: "
        f"run_id={run_id}, "
        f"query={dict(request.query_params)}, "
        f"body={body_text}"
    )

    try:
        payload = await request.json()
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in http_stream_run: {e}, traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format:{extract_core_stack()}")

    # 包装stream_sse为可取消的任务
    async def cancellable_stream():
        # 将真正的流式任务登记到 running_tasks，确保 /cancel 能定位到它
        task = asyncio.current_task()
        if task:
            service.running_tasks[run_id] = task
            logger.info(f"Registered streaming task for run_id: {run_id}")

        client_msg, _ = to_client_message(payload)
        t0 = time.time()

        try:
            async for chunk in service.stream_sse(payload, ctx):
                yield chunk
        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for run_id: {run_id}")
            end_msg = create_message_end_dict(
                code=MESSAGE_END_CODE_CANCELED,
                message="Stream cancelled by user",
                session_id=client_msg.session_id,
                query_msg_id=client_msg.local_msg_id,
                log_id=ctx.logid,
                time_cost_ms=int((time.time() - t0) * 1000),
                reply_id="",
                sequence_id=1,
            )
            yield service._sse_event(end_msg)
            raise
        except Exception as ex:
            logger.error(f"Unexpected error in http_stream_run: {ex}, traceback: {traceback.format_exc()}")
            error_msg = create_message_error_dict(
                code="exception",
                message=str(ex),
                session_id=client_msg.session_id,
                query_msg_id=client_msg.local_msg_id,
                log_id=ctx.logid,
                reply_id="",
                sequence_id=1,
                local_msg_id=client_msg.local_msg_id,
            )
            yield service._sse_event(error_msg)

    # 注意：StreamingResponse会在后台运行generator
    response = StreamingResponse(cancellable_stream(), media_type="text/event-stream")
    return response

@app.post("/cancel/{run_id}")
async def http_cancel(run_id: str, request: Request):
    """
    取消指定run_id的执行

    使用asyncio.Task.cancel()实现取消,这是Python标准的异步任务取消机制。
    LangGraph会在节点之间的await点检查CancelledError,实现优雅取消。
    """
    ctx = new_context(method="cancel", headers=request.headers)
    request_context.set(ctx)
    logger.info(f"Received cancel request for run_id: {run_id}")
    result = service.cancel_run(run_id, ctx)
    return result


@app.post(path="/node_run/{node_id}")
async def http_node_run(node_id: str, request: Request):
    raw_body = await request.body()
    try:
        body_text = raw_body.decode("utf-8")
    except UnicodeDecodeError:
        body_text = str(raw_body)
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {body_text}")
    ctx = new_context(method="node_run", headers=request.headers)
    request_context.set(ctx)
    logger.info(
        f"Received request for /node_run/{node_id}: "
        f"query={dict(request.query_params)}, "
        f"body={body_text}",
    )

    try:
        payload = await request.json()
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in http_node_run: {e}, traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format:{extract_core_stack()}")
    try:
        return await service.run_node(node_id, payload, ctx)
    except KeyError:
        raise HTTPException(status_code=404,
                            detail=f"node_id '{node_id}' not found or input miss required fields, traceback: {extract_core_stack()}")
    except Exception as e:
        logger.error(f"Unexpected error in http_node_run: {e}, traceback: {traceback.format_exc()}", exc_info=True)
        raise HTTPException(status_code=500, detail=extract_core_stack())
    finally:
        cozeloop.flush()


@app.get("/health")
async def health_check():
    try:
        # 这里可以添加更多的健康检查逻辑
        return {
            "status": "ok",
            "message": "Service is running",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get(path="/graph_parameter")
async def http_graph_inout_parameter(request: Request):
    return service.graph_inout_schema()


# 花名册管理API接口

from pydantic import BaseModel
from typing import Optional


class RosterEntryCreate(BaseModel):
    user_id: str
    name: str
    gender: str
    relationship_type: str
    current_location: str
    birth_date: Optional[str] = ""
    mbti: Optional[str] = ""
    birth_place: Optional[str] = ""
    relationship_level: Optional[str] = ""
    notes: Optional[str] = ""


class RosterEntryUpdate(BaseModel):
    name: Optional[str] = ""
    gender: Optional[str] = ""
    current_location: Optional[str] = ""
    birth_date: Optional[str] = ""
    mbti: Optional[str] = ""
    birth_place: Optional[str] = ""
    relationship_type: Optional[str] = ""
    relationship_level: Optional[str] = ""
    notes: Optional[str] = ""


@app.post("/api/roster")
async def add_roster(entry: RosterEntryCreate):
    """添加花名册条目"""
    from tools.roster_tool import add_roster_entry
    try:
        result = add_roster_entry(
            user_id=entry.user_id,
            name=entry.name,
            gender=entry.gender,
            relationship_type=entry.relationship_type,
            current_location=entry.current_location,
            birth_date=entry.birth_date or "",
            mbti=entry.mbti or "",
            birth_place=entry.birth_place or "",
            relationship_level=entry.relationship_level or "",
            notes=entry.notes or ""
        )
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error adding roster entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/roster")
async def get_roster(user_id: str, relationship_type: str = ""):
    """获取花名册列表"""
    from tools.roster_tool import get_roster_entries
    try:
        result = get_roster_entries(user_id=user_id, relationship_type=relationship_type)
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error getting roster: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/roster/{entry_id}")
async def get_roster_detail(entry_id: int):
    """获取花名册条目详情"""
    from tools.roster_tool import get_roster_entry_by_id
    try:
        result = get_roster_entry_by_id(entry_id=entry_id)
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error getting roster entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/roster/{entry_id}")
async def update_roster(entry_id: int, entry: RosterEntryUpdate):
    """更新花名册条目"""
    from tools.roster_tool import update_roster_entry
    try:
        result = update_roster_entry(
            entry_id=entry_id,
            name=entry.name or "",
            gender=entry.gender or "",
            current_location=entry.current_location or "",
            birth_date=entry.birth_date or "",
            mbti=entry.mbti or "",
            birth_place=entry.birth_place or "",
            relationship_type=entry.relationship_type or "",
            relationship_level=entry.relationship_level or "",
            notes=entry.notes or ""
        )
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error updating roster entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/roster/{entry_id}")
async def delete_roster(entry_id: int):
    """删除花名册条目"""
    from tools.roster_tool import delete_roster_entry
    try:
        result = delete_roster_entry(entry_id=entry_id)
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error deleting roster entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/roster/search")
async def search_roster(user_id: str, keyword: str):
    """搜索花名册条目"""
    from tools.roster_tool import search_roster_entries
    try:
        result = search_roster_entries(user_id=user_id, keyword=keyword)
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error searching roster: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/roster/bazi")
async def update_bazi(user_id: str, bazi: str):
    """为用户添加八字信息"""
    from tools.roster_tool import add_user_bazi
    try:
        result = add_user_bazi(user_id=user_id, bazi=bazi)
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error updating bazi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def parse_args():
    parser = argparse.ArgumentParser(description="Start FastAPI server")
    parser.add_argument("-m", type=str, default="http", help="Run mode, support http,flow,node")
    parser.add_argument("-n", type=str, default="", help="Node ID for single node run")
    parser.add_argument("-p", type=int, default=5000, help="HTTP server port")
    parser.add_argument("-i", type=str, default="", help="Input JSON string for flow/node mode")
    return parser.parse_args()


def parse_input(input_str: str) -> Dict[str, Any]:
    """Parse input string, support both JSON string and plain text"""
    if not input_str:
        return {"text": "你好"}

    # Try to parse as JSON first
    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        # If not valid JSON, treat as plain text
        return {"text": input_str}

def start_http_server(port):
    workers = 1
    reload = False
    if graph_helper.is_dev_env():
        reload = True

    logger.info(f"Start HTTP Server, Port: {port}, Workers: {workers}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload, workers=workers)

if __name__ == "__main__":
    args = parse_args()
    if args.m == "http":
        start_http_server(args.p)
    elif args.m == "flow":
        payload = parse_input(args.i)
        result = asyncio.run(service.run(payload))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.m == "node" and args.n:
        payload = parse_input(args.i)
        result = asyncio.run(service.run_node(args.n, payload))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.m == "agent":
        for chunk in service.stream(
                {
                    "type": "query",
                    "session_id": "1",
                    "message": "你好",
                    "content": {
                        "query": {
                            "prompt": [
                                {
                                    "type": "text",
                                    "content": {"text": "现在几点了？请调用工具获取当前时间"},
                                }
                            ]
                        }
                    },
                },
                run_config={"configurable": {"session_id": "1"}}
        ):
            print(chunk)
