from rich import box
from rich.console import Console
from rich.table import Table

console = Console()


def print_model_results(
    model_name: str,
    val_metrics: dict,
    test_metrics: dict,
    cv_rmse: float,
) -> None:
    """Print model evaluation results as a rich table."""
    table = Table(
        title=f"[bold cyan]{model_name}[/bold cyan]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold green",
    )

    table.add_column("Split", style="bold", width=8)
    table.add_column("RMSE", justify="right")
    table.add_column("MAE", justify="right")
    table.add_column("R²", justify="right")
    table.add_column("RMSLE", justify="right")

    table.add_row(
        "Val",
        f"{val_metrics['rmse']:.4f}",
        f"{val_metrics['mae']:.4f}",
        f"{val_metrics['r2']:.4f}",
        f"{val_metrics['rmsle']:.4f}",
    )
    table.add_row(
        "Test",
        f"{test_metrics['rmse']:.4f}",
        f"{test_metrics['mae']:.4f}",
        f"{test_metrics['r2']:.4f}",
        f"{test_metrics['rmsle']:.4f}",
    )
    table.add_row(
        "CV",
        f"{cv_rmse:.4f}",
        "—",
        "—",
        "—",
    )

    console.print(table)


def print_summary_table(results: dict, best_model_name: str) -> None:
    """Print final comparison table across all models."""
    table = Table(
        title="[bold]Model Comparison Summary[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold green",
    )

    table.add_column("Model", style="bold", width=20)
    table.add_column("Val RMSE", justify="right")
    table.add_column("Val R²", justify="right")
    table.add_column("Test RMSE", justify="right")
    table.add_column("CV RMSE", justify="right")
    table.add_column("Best", justify="center")

    for model_name, metrics in results.items():
        is_best = model_name == best_model_name
        table.add_row(
            f"[bold yellow]{model_name}[/bold yellow]" if is_best else model_name,
            f"{metrics['val']['rmse']:.4f}",
            f"{metrics['val']['r2']:.4f}",
            f"{metrics['test']['rmse']:.4f}",
            f"{metrics['cv_rmse']:.4f}",
            "[bold yellow]★[/bold yellow]" if is_best else "",
        )

    console.print(table)
