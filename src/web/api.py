"""
REST API Router for Ca Mau Fertilizer Classification Dashboard.
Provides endpoints for video controls, real-time statistics,
order management, and Excel reporting.
"""

from datetime import datetime
import glob
import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
import pandas as pd
from pydantic import BaseModel

from src.config import BASE_DIR, EXPORTS_DIR
from src.core.database import DatabaseManager
from src.web.video_stream import VideoStreamManager

router = APIRouter(prefix="/api")

# Global singletons injected during app startup
stream_manager: Optional[VideoStreamManager] = None
db_manager: Optional[DatabaseManager] = None


def init_api_services(
    stream: VideoStreamManager, db: DatabaseManager
):
    global stream_manager, db_manager
    stream_manager = stream
    db_manager = db


# Pydantic Schemas
class VideoControlRequest(BaseModel):
    action: str  # 'play', 'pause', 'toggle_pause', 'reset', 'change_source', 'set_line'
    source: Optional[str] = None
    orientation: Optional[str] = "horizontal"
    coord: Optional[int] = 310


class CreateOrderRequest(BaseModel):
    customer_name: str
    items: Dict[str, int]


class SelectOrderRequest(BaseModel):
    order_id: int


@router.get("/status")
def get_system_status():
    """Return live metrics, counters, and streaming status."""
    if not stream_manager:
        raise HTTPException(status_code=503, detail="Stream service not ready")
    return stream_manager.get_status()


@router.get("/chart_data")
def get_chart_data():
    """Return real-time chart data for ApexCharts."""
    if not stream_manager:
        raise HTTPException(status_code=503, detail="Stream service not ready")
    return stream_manager.get_chart_data()


@router.get("/video_feed")
def video_feed():
    """MJPEG live video stream endpoint."""
    if not stream_manager:
        raise HTTPException(status_code=503, detail="Stream service not ready")
    return StreamingResponse(
        stream_manager.generate_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/video/control")
def control_video(req: VideoControlRequest):
    """Control video streaming: play, pause, reset, switch source."""
    if not stream_manager:
        raise HTTPException(status_code=503, detail="Stream service not ready")

    if req.action == "toggle_pause":
        is_paused = stream_manager.toggle_pause()
        return {"success": True, "is_paused": is_paused}
    elif req.action == "reset":
        stream_manager.reset_counts()
        return {"success": True, "message": "Counters reset"}
    elif req.action == "change_source" and req.source:
        stream_manager.change_source(req.source)
        return {"success": True, "source": req.source}
    elif req.action == "set_line" and req.orientation and req.coord:
        stream_manager.set_line_config(req.orientation, req.coord)
        return {"success": True, "orientation": req.orientation, "coord": req.coord}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")


@router.get("/orders")
def get_orders():
    """Fetch all orders from SQLite database."""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database service not ready")
    return db_manager.get_all_orders()


@router.post("/orders")
def create_order(req: CreateOrderRequest):
    """Create a new customer order with target quantities."""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database service not ready")

    ok, order_id = db_manager.create_order(req.customer_name, req.items)
    if not ok:
        raise HTTPException(status_code=400, detail="Could not create order")

    # If stream manager currently has no active order, automatically set this one
    if stream_manager and stream_manager.active_order is None:
        stream_manager.set_target_order({
            "order_id": order_id,
            "customer": req.customer_name,
            "targets": req.items,
        })

    return {"success": True, "order_id": order_id}


@router.post("/orders/select")
def select_active_order(req: SelectOrderRequest):
    """Select an existing order as the active tracking target."""
    if not db_manager or not stream_manager:
        raise HTTPException(status_code=503, detail="Services not ready")

    order = db_manager.get_order_by_id(req.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    targets = {item["product_name"]: item["quantity_ordered"] for item in order.get("items", [])}
    order_info = {
        "order_id": order["id"],
        "customer": order["customer_name"],
        "targets": targets,
    }
    stream_manager.set_target_order(order_info)
    return {"success": True, "active_order": order_info}


@router.delete("/orders/{order_id}")
def delete_order(order_id: int):
    """Delete an order from database."""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database service not ready")
    ok = db_manager.delete_order(order_id)
    return {"success": ok}


@router.get("/sample_videos")
def list_sample_videos():
    """List available sample videos in assets/videos/."""
    video_dir = BASE_DIR / "assets" / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    video_files = glob.glob(str(video_dir / "*.*"))
    results = []
    for f in video_files:
        p = Path(f)
        if p.suffix.lower() in [".mp4", ".avi", ".mov", ".mkv"]:
            results.append({
                "name": p.name,
                "path": str(p),
                "size_mb": round(p.stat().st_size / (1024 * 1024), 1),
            })
    return results


@router.get("/export_excel")
def export_excel():
    """Export current session counting stats into formatted Excel file."""
    if not stream_manager or not db_manager:
        raise HTTPException(status_code=503, detail="Services not ready")

    status = stream_manager.get_status()
    counts = status.get("counts", {})
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    export_data = {
        "Loại Sản Phẩm": ["Urea Bio xanh", "NPK 22-5-6", "Urea hạt đục"],
        "Số Lượng Đếm Được": [
            counts.get("Urea_Bio_xanh", 0),
            counts.get("NPK_22-5-6", 0),
            counts.get("Urea_hat_duc", 0),
        ],
        "Tốc Độ (Bao / Phút)": [status.get("speed_bags_per_min", 0.0)] * 3,
        "Thời Gian Xuất Báo Cáo": [now_str] * 3,
        "Nguồn Video / Camera": [status.get("video_source", "Camera")] * 3,
    }

    df = pd.DataFrame(export_data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"Bao_Cao_Dem_Phan_Bon_{timestamp}.xlsx"
    file_path = EXPORTS_DIR / file_name

    df.to_excel(file_path, index=False)

    # Audit in DB
    db_manager.record_counting_session(
        order_id=None,
        video_source=status.get("video_source", ""),
        counts=counts,
        start_time=stream_manager.session_start.strftime("%d/%m/%Y %H:%M:%S"),
        end_time=now_str,
        exported_file=str(file_path),
    )

    return FileResponse(
        path=str(file_path),
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
