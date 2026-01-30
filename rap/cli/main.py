"""
Command-line interface for the RAP framework.

Usage:
    myrap run --input scenarios.csv --output results.csv --iterations 10000
    myrap info
    myrap taxonomy
    myrap template --output template.csv
"""

import sys
from pathlib import Path
from typing import Optional

import click

from rap import __version__
from rap.core.taxonomy import (
    get_all_dimensions,
    get_all_metrics,
    get_metrics_by_dimension,
    get_dimension_summary,
)
from rap.data.io import (
    read_scenarios_csv,
    write_results_csv,
    create_scenario_template,
    create_assessment_template,
)
from rap.engine.monte_carlo import (
    simulate_scenarios,
    SimulationConfig,
    aggregate_results,
)
from rap.engine.analytics import (
    calculate_risk_metrics,
    rank_scenarios,
    format_currency,
)


@click.group()
@click.version_option(version=__version__, prog_name="RAP Framework")
def cli() -> None:
    """
    RAP - Resilience Acceleration Program

    A risk quantification framework for cybersecurity resilience,
    inspired by FAIR/Open FAIR methodology.

    RAP connects three work fronts:
    - Business Strategy (Security Advisory)
    - Strategy & Risk Governance (GRC)
    - Offensive Security (Red Team)

    Using 7 digital risk dimensions and 25+ resilience metrics.
    """
    pass


@cli.command()
@click.option(
    "--input", "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Input CSV file with scenario definitions.",
)
@click.option(
    "--output", "-o",
    "output_file",
    required=True,
    type=click.Path(path_type=Path),
    help="Output CSV file for simulation results.",
)
@click.option(
    "--iterations", "-n",
    default=10000,
    type=int,
    help="Number of Monte Carlo iterations (default: 10000).",
)
@click.option(
    "--seed", "-s",
    default=None,
    type=int,
    help="Random seed for reproducibility.",
)
@click.option(
    "--aggregate/--no-aggregate",
    default=False,
    help="Include aggregated portfolio view.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed output.",
)
def run(
    input_file: Path,
    output_file: Path,
    iterations: int,
    seed: Optional[int],
    aggregate: bool,
    verbose: bool,
) -> None:
    """
    Run Monte Carlo simulation on risk scenarios.

    Reads scenarios from INPUT CSV, runs simulation, and writes
    results to OUTPUT CSV.

    Example:
        myrap run --input scenarios.csv --output results.csv --iterations 20000
    """
    click.echo(f"RAP Framework v{__version__}")
    click.echo(f"Reading scenarios from: {input_file}")

    try:
        scenarios = read_scenarios_csv(input_file)
    except Exception as e:
        click.echo(f"Error reading input file: {e}", err=True)
        sys.exit(1)

    click.echo(f"Loaded {len(scenarios)} scenarios")

    if verbose:
        click.echo("\nScenarios:")
        for s in scenarios:
            click.echo(f"  - {s.scenario_id}: {s.name}")

    # Configure simulation
    config = SimulationConfig(
        n_iterations=iterations,
        random_seed=seed,
    )

    click.echo(f"\nRunning Monte Carlo simulation ({iterations:,} iterations)...")

    try:
        results = simulate_scenarios(scenarios, config)
    except Exception as e:
        click.echo(f"Error during simulation: {e}", err=True)
        sys.exit(1)

    # Add aggregated result if requested
    if aggregate and len(results) > 1:
        try:
            agg_result = aggregate_results(results)
            results.append(agg_result)
            click.echo("Added aggregated portfolio view")
        except Exception as e:
            click.echo(f"Warning: Could not aggregate results: {e}", err=True)

    # Write results
    try:
        write_results_csv(results, output_file)
    except Exception as e:
        click.echo(f"Error writing output file: {e}", err=True)
        sys.exit(1)

    click.echo(f"\nResults written to: {output_file}")

    # Show summary
    click.echo("\n" + "=" * 60)
    click.echo("SIMULATION RESULTS SUMMARY")
    click.echo("=" * 60)

    for result in results:
        metrics = calculate_risk_metrics(result)
        click.echo(f"\n{metrics.scenario_name}")
        click.echo("-" * 40)
        click.echo(f"  Expected Annual Loss: {format_currency(metrics.mean_loss, metrics.currency)}")
        click.echo(f"  VaR 95%:              {format_currency(metrics.var_95, metrics.currency)}")
        click.echo(f"  VaR 99%:              {format_currency(metrics.var_99, metrics.currency)}")

    # Show ranking
    if len(results) > 1 and not aggregate:
        click.echo("\n" + "-" * 60)
        click.echo("RISK RANKING (by Expected Annual Loss)")
        click.echo("-" * 60)
        rankings = rank_scenarios(results, "mean_loss")
        for i, (sid, name, value) in enumerate(rankings, 1):
            click.echo(f"  {i}. {name}: {format_currency(value, results[0].currency)}")


@cli.command()
def info() -> None:
    """
    Display information about the RAP framework.
    """
    click.echo(f"""
RAP - Resilience Acceleration Program
Version: {__version__}

A risk quantification framework for cybersecurity resilience,
inspired by FAIR/Open FAIR methodology.

The RAP framework organizes risk assessment into:
- 7 Digital Risk Dimensions
- 25+ Resilience Metrics
- 3 Assessment Layers:
  1. Business Strategy (objectives, RTO/RPO, risk appetite)
  2. Strategy & Risk Governance (controls, processes, compliance)
  3. Offensive Security (real-world testing, Red Team results)

Risk Calculation:
- Uses PERT distributions for frequency and impact
- Monte Carlo simulation for loss distribution
- Outputs: Mean, Median, VaR 90/95/99

For more information:
  myrap taxonomy     - View dimensions and metrics
  myrap template     - Generate CSV templates
  myrap run --help   - Simulation options
""")


@cli.command()
@click.option(
    "--dimension", "-d",
    type=int,
    default=None,
    help="Show metrics for a specific dimension (1-7).",
)
@click.option(
    "--metric", "-m",
    type=str,
    default=None,
    help="Show details for a specific metric ID.",
)
def taxonomy(dimension: Optional[int], metric: Optional[str]) -> None:
    """
    Display RAP taxonomy (dimensions and metrics).

    Examples:
        myrap taxonomy                  # Show all dimensions
        myrap taxonomy -d 1             # Show metrics for dimension 1
        myrap taxonomy -m 01            # Show details for metric 01
    """
    from rap.core.taxonomy import get_metric, get_dimension

    if metric:
        # Show specific metric
        m = get_metric(metric)
        if not m:
            click.echo(f"Metric not found: {metric}", err=True)
            sys.exit(1)

        dim = get_dimension(m.dimension_id)
        dim_name = dim.name if dim else "Unknown"

        click.echo(f"""
Metric: {m.id} - {m.name}
{'=' * 60}
Description: {m.description}

Dimension:        {m.dimension_id} - {dim_name}
Measurement Type: {m.measurement_type}
Target Unit:      {m.target_unit}
Higher is Better: {'Yes' if m.higher_is_better else 'No'}

Related Frameworks: {', '.join(m.frameworks) if m.frameworks else 'N/A'}
""")
        return

    if dimension:
        # Show metrics for specific dimension
        dim = get_dimension(dimension)
        if not dim:
            click.echo(f"Dimension not found: {dimension}", err=True)
            sys.exit(1)

        click.echo(f"""
Dimension {dim.id}: {dim.name}
{'=' * 60}
English: {dim.name_en}

Description:
{dim.description}

Frameworks: {', '.join(dim.frameworks)}

Metrics:
""")
        metrics = get_metrics_by_dimension(dimension)
        for m in metrics:
            click.echo(f"  {m.id}: {m.name}")
            click.echo(f"      {m.description[:80]}...")
            click.echo()

        return

    # Show all dimensions summary
    click.echo("""
RAP TAXONOMY - 7 Digital Risk Dimensions
========================================
""")
    summary = get_dimension_summary()
    for dim_id, info in summary.items():
        click.echo(f"{dim_id}. {info['name']}")
        click.echo(f"   ({info['name_en']})")
        click.echo(f"   Metrics: {info['metric_count']} - IDs: {', '.join(info['metric_ids'])}")
        click.echo()

    click.echo("Use 'myrap taxonomy -d <number>' for dimension details")
    click.echo("Use 'myrap taxonomy -m <id>' for metric details")


@cli.command()
@click.option(
    "--output", "-o",
    "output_file",
    required=True,
    type=click.Path(path_type=Path),
    help="Output CSV file for template.",
)
@click.option(
    "--type", "-t",
    "template_type",
    type=click.Choice(["scenario", "assessment"]),
    default="scenario",
    help="Template type: scenario or assessment.",
)
def template(output_file: Path, template_type: str) -> None:
    """
    Generate CSV template files.

    Creates template files with example data that can be used
    as starting points for your own scenarios or assessments.

    Examples:
        myrap template -o scenarios.csv -t scenario
        myrap template -o assessments.csv -t assessment
    """
    try:
        if template_type == "scenario":
            create_scenario_template(output_file)
            click.echo(f"Scenario template created: {output_file}")
            click.echo("\nTemplate includes example scenarios for:")
            click.echo("  - Ransomware Attack on ERP")
            click.echo("  - Data Breach via Phishing")
            click.echo("  - Supply Chain Compromise")
        else:
            create_assessment_template(output_file)
            click.echo(f"Assessment template created: {output_file}")
            click.echo("\nTemplate includes example assessments from:")
            click.echo("  - Business Strategy layer")
            click.echo("  - Strategy & Risk Governance layer")
            click.echo("  - Offensive Security layer")

        click.echo("\nEdit the template and run:")
        if template_type == "scenario":
            click.echo(f"  myrap run -i {output_file} -o results.csv")
        else:
            click.echo("  (Assessment templates are used for PLA analysis)")

    except Exception as e:
        click.echo(f"Error creating template: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--input", "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Input CSV file with scenarios to validate.",
)
def validate(input_file: Path) -> None:
    """
    Validate a scenario CSV file.

    Checks for required columns, valid value ranges, and
    consistency of frequency/impact parameters.
    """
    import pandas as pd
    from rap.data.mapping import validate_scenario_data

    click.echo(f"Validating: {input_file}")

    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        sys.exit(1)

    click.echo(f"Found {len(df)} rows\n")

    has_errors = False
    for idx, row in df.iterrows():
        errors = validate_scenario_data(row)
        if errors:
            has_errors = True
            scenario_name = row.get("scenario_name", f"Row {idx}")
            click.echo(f"Errors in '{scenario_name}':")
            for error in errors:
                click.echo(f"  - {error}")
            click.echo()

    if has_errors:
        click.echo("Validation failed. Please fix the errors above.", err=True)
        sys.exit(1)
    else:
        click.echo("Validation passed. File is ready for simulation.")


if __name__ == "__main__":
    cli()
