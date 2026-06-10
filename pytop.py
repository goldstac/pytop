import os
import sys
import time
import psutil
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table

def create_vertical_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="top_banner", size=5),
        Layout(name="process_pane", ratio=1)
    )
    return layout

def get_top_banner_content() -> Table:
    banner_table = Table.grid(expand=True)
    banner_table.add_column(justify="left", ratio=1)
    banner_table.add_column(justify="right", ratio=3)

    branding_str = "[bold magenta]pytop[/]"

    stats_table = Table.grid(expand=True)
    stats_table.add_column(justify="center", ratio=1)
    stats_table.add_column(justify="center", ratio=1)
    stats_table.add_column(justify="center", ratio=1)

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    mem_used = mem.used / (1024**3)
    mem_total = mem.total / (1024**3)
    
    cpu_str = f"[bold cyan]CPU Load:[/] {cpu}%"
    mem_str = f"[bold magenta]RAM Usage:[/] {mem.percent}% ({mem_used:.1f}GB/{mem_total:.1f}GB)"
    disk_str = f"[bold yellow]Disk Space:[/] {disk.percent}% free"
    
    stats_table.add_row(cpu_str, mem_str, disk_str)
    banner_table.add_row(branding_str, stats_table)
    return banner_table

def get_massive_process_table(available_height: int) -> Table:
    table = Table(box=None, expand=True, show_header=True, header_style="bold reverse magenta")
    table.add_column("PID", justify="right", width=7, style="dim")
    table.add_column("Application Name", justify="left", style="bold white")
    table.add_column("CPU %", justify="right", width=10, style="cyan")
    table.add_column("Memory %", justify="right", width=10, style="yellow")

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['cpu_percent'] is not None:
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
    max_rows = max(5, available_height - 4)
    
    for proc in processes[:max_rows]:
        table.add_row(
            str(proc['pid']),
            proc['name'][:45],
            f"{proc['cpu_percent']:.1f}%",
            f"{proc['memory_percent']:.1f}%"
        )
    return table

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    layout = create_vertical_layout()
    
    try:
        with Live(layout, refresh_per_second=2, screen=True) as live:
            while True:
                term_width, term_height = os.get_terminal_size()
                process_pane_height = term_height - 5
                
                layout["top_banner"].update(Panel(get_top_banner_content(), border_style="dim cyan"))
                layout["process_pane"].update(Panel(get_massive_process_table(process_pane_height), title="🔥 Active System Workloads", border_style="magenta"))
                
                time.sleep(0.5)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()