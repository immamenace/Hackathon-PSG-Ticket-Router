#!/usr/bin/env python3
"""
Setup verification script for Smart Support Ticket Router
Checks if all dependencies are installed and components are working
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        return True, "✅ Installed"
    except ImportError:
        pkg = package_name or module_name
        return False, f"❌ Missing (install: pip install {pkg})"

def main():
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Smart Support Ticket Router[/bold cyan]\n"
        "Setup Verification",
        border_style="cyan"
    ))
    
    # Check dependencies
    console.print("\n[bold yellow]Checking Dependencies...[/bold yellow]\n")
    
    dependencies = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn[standard]"),
        ("sklearn", "scikit-learn"),
        ("transformers", "transformers"),
        ("torch", "torch"),
        ("redis", "redis"),
        ("celery", "celery"),
        ("httpx", "httpx"),
        ("sentence_transformers", "sentence-transformers"),
        ("scipy", "scipy"),
        ("jinja2", "jinja2"),
        ("rich", "rich"),
    ]
    
    table = Table(title="Dependency Status")
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="green")
    
    all_installed = True
    for module, package in dependencies:
        success, status = check_import(module, package)
        table.add_row(package, status)
        if not success:
            all_installed = False
    
    console.print(table)
    
    # Check project structure
    console.print("\n[bold yellow]Checking Project Structure...[/bold yellow]\n")
    
    import os
    
    required_files = [
        "main.py",
        "requirements.txt",
        "templates/index.html",
        "m1_mvr/__init__.py",
        "m1_mvr/ml_baseline.py",
        "m1_mvr/router.py",
        "m2_advanced/__init__.py",
        "m2_advanced/ml_transformers.py",
        "m2_advanced/router.py",
        "m3_orchestrator/__init__.py",
        "m3_orchestrator/semantic_dedup.py",
        "m3_orchestrator/circuit_breaker.py",
        "m3_orchestrator/skill_router.py",
        "m3_orchestrator/router.py",
    ]
    
    structure_table = Table(title="Project Files")
    structure_table.add_column("File", style="cyan")
    structure_table.add_column("Status", style="green")
    
    all_files_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅ Found" if exists else "❌ Missing"
        structure_table.add_row(file_path, status)
        if not exists:
            all_files_exist = False
    
    console.print(structure_table)
    
    # Check if components can be imported
    console.print("\n[bold yellow]Checking Components...[/bold yellow]\n")
    
    components_table = Table(title="Component Status")
    components_table.add_column("Component", style="cyan")
    components_table.add_column("Status", style="green")
    
    components = [
        ("Baseline Classifier", "m1_mvr.ml_baseline", "BaselineClassifier"),
        ("Advanced Classifier", "m2_advanced.ml_transformers", "AdvancedClassifier"),
        ("Semantic Deduplicator", "m3_orchestrator.semantic_dedup", "SemanticDeduplicator"),
        ("Circuit Breaker", "m3_orchestrator.circuit_breaker", "CircuitBreaker"),
        ("Skill Router", "m3_orchestrator.skill_router", "SkillBasedRouter"),
    ]
    
    all_components_ok = True
    for name, module, class_name in components:
        try:
            mod = __import__(module, fromlist=[class_name])
            getattr(mod, class_name)
            components_table.add_row(name, "✅ OK")
        except Exception as e:
            components_table.add_row(name, f"❌ Error: {str(e)[:30]}")
            all_components_ok = False
    
    console.print(components_table)
    
    # Final summary
    console.print("\n")
    if all_installed and all_files_exist and all_components_ok:
        console.print(Panel.fit(
            "[bold green]✅ All checks passed![/bold green]\n\n"
            "Your setup is complete and ready to use.\n\n"
            "Next steps:\n"
            "1. Start the server: [cyan]python main.py[/cyan]\n"
            "2. Open browser: [cyan]http://localhost:8000[/cyan]\n"
            "3. Run tests: [cyan]python test_milestone3.py[/cyan]",
            title="🎉 Success",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel.fit(
            "[bold red]❌ Some checks failed[/bold red]\n\n"
            "Please fix the issues above.\n\n"
            "To install missing dependencies:\n"
            "[cyan]pip install -r requirements.txt[/cyan]",
            title="⚠️  Issues Found",
            border_style="red"
        ))
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Verification interrupted[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        sys.exit(1)
