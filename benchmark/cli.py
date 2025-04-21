import click

from benchmark.core.runner import generate_cases as generate_test_cases, run_benchmark
from benchmark.report.report_builder import build_report

@click.group()
def cli():
    """Benchmark CLI."""
    pass

@cli.command("generate-cases")
def generate_cases():
    """Generate test cases."""
    generate_test_cases()
    click.echo("Test cases generated.")

@cli.command("run")
@click.option('--case-ids', '-c', multiple=True, help="Test case IDs to run. If omitted, run all.")
@click.option('--tool-ids', '-t', multiple=True, help="Tool IDs to run. If omitted, run all.")
def run(case_ids, tool_ids):
    """Run benchmark for given case and tool IDs."""
    run_id = run_benchmark(case_ids=case_ids, tool_ids=tool_ids)
    click.echo(f"Run started with ID: {run_id}")

@cli.command("report")
@click.argument("run_id")
def report(run_id):
    """Generate report for a run."""
    report_file = build_report(run_id)
    click.echo(f"Report generated: {report_file}")

if __name__ == '__main__':
    cli()