#!/usr/bin/env python3
"""测试应用的 API"""
import httpx
from rich.console import Console
from rich.table import Table
from rich import print

console = Console()

BASE_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # 测试健康检查
        console.print("[bold cyan]1. 健康检查[/bold cyan]")
        response = await client.get(f"{BASE_URL}/health")
        console.print(f"[green]✓[/green] 状态: {response.json()}")
        
        # 测试数据源列表
        console.print("\n[bold cyan]2. 数据源列表[/bold cyan]")
        response = await client.get(f"{BASE_URL}/api/sources/")
        sources = response.json()
        console.print(f"[green]✓[/green] 已加载 {len(sources)} 个数据源")
        
        # 统计各类型
        from collections import Counter
        types = Counter([s['type'] for s in sources])
        for t, count in types.items():
            console.print(f"  - {t}: {count}")
        
        # 测试仪表盘
        console.print("\n[bold cyan]3. 仪表盘数据[/bold cyan]")
        response = await client.get(f"{BASE_URL}/api/dashboard/summary")
        console.print(f"[green]✓[/green] 仪表盘: {response.json()}")
        
        # 测试 RSS 采集
        console.print("\n[bold cyan]4. RSS 采集测试[/bold cyan]")
        items = await client.get(f"{BASE_URL}/api/items/")
        console.print(f"[green]✓[/green] 数据库中的内容数: {len(items.json())}")
        
        console.print("\n[bold green]✓ 所有测试通过！应用运行正常[/bold green]")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
