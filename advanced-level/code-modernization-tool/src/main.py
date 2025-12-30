"""
Main entry point for Code Modernization Tool
"""
import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

from .analyzer.code_analyzer import CodeAnalyzer
from .converter.code_converter import CodeConverter
from .test_generator.test_generator import TestGenerator
from .documentation.doc_generator import DocumentationGenerator

console = Console()


@click.command()
@click.option('--source', '-s', required=True, help='Path to source code directory')
@click.option('--target', '-t', default='python', help='Target language (python, typescript, etc.)')
@click.option('--framework', '-f', default='fastapi', help='Target framework (fastapi, flask, express, etc.)')
@click.option('--output', '-o', default='./output', help='Output directory for modernized code')
@click.option('--preserve-original', is_flag=True, default=True, help='Preserve original code in output')
@click.option('--coverage', '-c', default=80, help='Target test coverage percentage')
@click.option('--ai-model', default='gpt-4o', help='AI model for code analysis and conversion')
def main(source, target, framework, output, preserve_original, coverage, ai_model):
    """
    Code Modernization Tool - Modernize legacy codebases using AI
    
    Example:
        python -m src.main --source ./legacy-java-app --target python --framework fastapi
    """
    console.print("[bold blue]🔧 Code Modernization Tool[/bold blue]")
    console.print(f"Source: {source}")
    console.print(f"Target: {target} ({framework})")
    console.print(f"Output: {output}")
    console.print("")
    
    # Validate source path
    source_path = Path(source)
    if not source_path.exists():
        console.print(f"[red]Error: Source path '{source}' does not exist[/red]")
        sys.exit(1)
    
    # Create output directory
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if preserve_original:
        original_path = output_path / "original_code"
        original_path.mkdir(exist_ok=True)
        console.print(f"[green]✓[/green] Original code will be preserved in: {original_path}")
    
    try:
        with Progress() as progress:
            # Step 1: Analyze code
            task1 = progress.add_task("[cyan]Analyzing codebase...", total=100)
            analyzer = CodeAnalyzer(source_path, ai_model=ai_model)
            analysis_result = analyzer.analyze()
            progress.update(task1, completed=100)
            console.print("[green]✓[/green] Code analysis complete")
            
            # Step 2: Generate documentation
            task2 = progress.add_task("[cyan]Generating documentation...", total=100)
            doc_generator = DocumentationGenerator(analysis_result, output_path)
            doc_generator.generate()
            progress.update(task2, completed=100)
            console.print("[green]✓[/green] Documentation generated")
            
            # Step 3: Convert code
            task3 = progress.add_task("[cyan]Converting code...", total=100)
            converter = CodeConverter(analysis_result, target, framework, ai_model=ai_model)
            modernized_code = converter.convert()
            progress.update(task3, completed=100)
            console.print("[green]✓[/green] Code conversion complete")
            
            # Step 4: Generate tests
            task4 = progress.add_task("[cyan]Generating tests...", total=100)
            test_gen = TestGenerator(modernized_code, coverage_target=coverage, ai_model=ai_model)
            test_suite = test_gen.generate()
            progress.update(task4, completed=100)
            console.print("[green]✓[/green] Test suite generated")
            
            # Step 5: Save output
            task5 = progress.add_task("[cyan]Saving output...", total=100)
            _save_output(output_path, modernized_code, test_suite, preserve_original, source_path)
            progress.update(task5, completed=100)
            console.print("[green]✓[/green] Output saved")
        
        console.print("")
        console.print("[bold green]✅ Modernization complete![/bold green]")
        console.print(f"Modernized code: {output_path / 'modernized_code'}")
        console.print(f"Tests: {output_path / 'tests'}")
        console.print(f"Documentation: {output_path / 'docs'}")
        if preserve_original:
            console.print(f"Original code: {output_path / 'original_code'}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


def _save_output(output_path, modernized_code, test_suite, preserve_original, source_path):
    """Save all output files"""
    # Save modernized code
    modernized_dir = output_path / "modernized_code"
    modernized_dir.mkdir(exist_ok=True)
    
    for file_path, content in modernized_code.items():
        full_path = modernized_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    # Save tests
    tests_dir = output_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    for file_path, content in test_suite.items():
        full_path = tests_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    # Preserve original if requested
    if preserve_original:
        original_dir = output_path / "original_code"
        import shutil
        if source_path.is_dir():
            shutil.copytree(source_path, original_dir, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, original_dir)


if __name__ == '__main__':
    main()

