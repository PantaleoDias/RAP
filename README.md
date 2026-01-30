# RAP - Resilience Acceleration Program

A Python framework for cybersecurity risk quantification oriented towards **Cyber Resilience**, inspired by FAIR (Factor Analysis of Information Risk) and Open FAIR methodologies.

## Overview

RAP connects three work fronts to provide comprehensive risk assessment:

1. **Business Strategy** (Security Advisory) - Defines objectives: RTO, RPO, BIA, risk appetite
2. **Strategy & Risk Governance** (GRC) - Assesses controls, processes, and compliance maturity
3. **Offensive Security** (Red Team) - Tests real-world performance through simulations

Using **7 Digital Risk Dimensions** and **25+ Resilience Metrics**, RAP correlates results from these three fronts to:

- Estimate annual frequency (via PERT distribution)
- Estimate financial impact
- Calculate simulated annual risk using a FAIR-like model
- Present risk in a **3-Level PLA View**

## Installation

```bash
# Clone the repository
git clone https://github.com/example/rap.git
cd rap

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### 1. Create a scenario file

Create a CSV file with your risk scenarios (or use the template generator):

```bash
# Generate a template
myrap template -o scenarios.csv -t scenario
```

Example CSV format:
```csv
scenario_id,scenario_name,metric_id,dimension_id,asset,threat,freq_min,freq_most,freq_max,impact_min,impact_most,impact_max,currency
R001,Ransomware Attack on ERP,01,1,ERP System,Ransomware,0.1,0.3,0.7,100000,500000,3000000,BRL
```

### 2. Run simulation

```bash
myrap run --input scenarios.csv --output results.csv --iterations 10000
```

### 3. View results

The output CSV contains:
- `mean_loss` - Expected annual loss
- `var_90`, `var_95`, `var_99` - Value at Risk at different confidence levels
- `probability_of_loss` - Probability of any loss occurring

## CLI Commands

```bash
# Run Monte Carlo simulation
myrap run -i scenarios.csv -o results.csv -n 20000

# Show framework information
myrap info

# View taxonomy (dimensions and metrics)
myrap taxonomy              # All dimensions
myrap taxonomy -d 1         # Dimension 1 details
myrap taxonomy -m 01        # Metric 01 details

# Generate templates
myrap template -o scenario_template.csv -t scenario
myrap template -o assessment_template.csv -t assessment

# Validate scenario file
myrap validate -i scenarios.csv
```

## The 7 Digital Risk Dimensions

RAP organizes 25+ metrics into 7 risk dimensions aligned with industry standards:

| ID | Dimension | Description |
|----|-----------|-------------|
| 1 | Resiliência e Recuperação | Capacity to survive and recover from incidents |
| 2 | Proteção de Identidade e Acesso | Identity, credential, and access control |
| 3 | Segurança de Aplicações e Infra | Application and infrastructure hardening |
| 4 | Proteção de Dados e Compliance | Data privacy, LGPD/GDPR compliance |
| 5 | Segurança OT/IoT/Industrial | OT/IoT/ICS security |
| 6 | IA e Ameaças Emergentes | AI risks, deepfakes, emerging threats |
| 7 | Gestão de Riscos e Superfície | Attack surface, third-party, supply chain |

## Three-Layer Assessment (PLA View)

RAP provides a **3-Level PLA View** for each metric:

```
Level 1: Business Strategy Objective
├── What resilience/compliance objective does the business define?
├── Example: RTO < 2 hours for critical ERP

Level 2: Strategy & Risk Governance (GRC)
├── What is the current maturity of controls and processes?
├── Example: DR plan tested quarterly, 85% PAM coverage

Level 3: Offensive Security Reality
├── What do real-world tests show?
├── Example: Actual recovery took 4 hours (vs 2h target)
```

The **gap** between these levels directly affects risk parameters:
- Larger gap → Higher frequency and impact estimates
- Smaller gap → Lower risk estimates

## Risk Model (FAIR-inspired)

RAP uses a FAIR-inspired model:

```
Annual Loss = Σ (Event Frequency × Event Impact)
```

For each scenario:
1. **Frequency** is sampled from a PERT distribution (min, most_likely, max)
2. **Impact** is sampled from a PERT distribution (min, most_likely, max)
3. **Monte Carlo simulation** generates thousands of possible annual losses
4. **Statistics** are calculated: mean, median, VaR 90/95/99

### Example

```python
from rap import RiskScenario, FrequencyParams, ImpactParams
from rap.engine.monte_carlo import simulate_scenario
from rap.engine.analytics import calculate_risk_metrics

# Define a scenario
scenario = RiskScenario(
    name="Ransomware Attack on ERP",
    description="Ransomware encrypts critical ERP database",
    metric_id="01",
    dimension_id=1,
    asset="ERP System",
    threat="Ransomware",
    frequency=FrequencyParams(0.1, 0.3, 0.7),  # Events per year
    impact=ImpactParams(100_000, 500_000, 3_000_000, "BRL"),
)

# Run simulation
result = simulate_scenario(scenario)
metrics = calculate_risk_metrics(result)

print(f"Expected Annual Loss: R$ {metrics.mean_loss:,.2f}")
print(f"VaR 95%: R$ {metrics.var_95:,.2f}")
```

## Project Structure

```
rap/
├── rap/
│   ├── __init__.py
│   ├── core/
│   │   ├── model.py          # RiskScenario, FrequencyParams, ImpactParams
│   │   ├── taxonomy.py       # 7 dimensions, 25 metrics
│   │   └── mapping_layers.py # Three-layer assessment mapping
│   ├── engine/
│   │   ├── distributions.py  # PERT, triangular sampling
│   │   ├── monte_carlo.py    # Simulation engine
│   │   └── analytics.py      # Risk metrics calculation
│   ├── data/
│   │   ├── io.py             # CSV read/write
│   │   └── mapping.py        # Data conversion utilities
│   └── cli/
│       └── main.py           # CLI commands
├── examples/
│   ├── simple_ransomware.csv
│   ├── comprehensive_scenarios.csv
│   └── sample_assessments.csv
├── tests/
├── README.md
└── pyproject.toml
```

## Understanding the Output

### Mean Loss (Expected Annual Loss)

The average loss you should expect per year across all simulations. Use this for budgeting and baseline risk comparisons.

### VaR (Value at Risk)

- **VaR 90**: 90% of simulated years had losses below this value
- **VaR 95**: 95% of simulated years had losses below this value
- **VaR 99**: 99% of simulated years had losses below this value

Higher VaR percentiles represent more extreme (but less likely) scenarios.

### Interpretation Example

```
Scenario: Ransomware Attack on ERP
Mean Loss:  R$ 283,000
VaR 95%:    R$ 1,200,000
VaR 99%:    R$ 2,800,000
```

This means:
- On average, expect ~R$ 283k in losses per year
- In 95% of years, losses will be under R$ 1.2M
- In the worst 1% of years, losses could exceed R$ 2.8M

## Methodology

RAP is inspired by:

- **[pyfair](https://github.com/Hive-Systems/pyfair)** - Open Source FAIR Toolkit
- **[riskquant](https://github.com/Netflix-Skunkworks/riskquant)** - Netflix's risk quantification library
- **[evaluator](https://github.com/davidski/evaluator)** - Quantified Risk Assessment Toolkit

### Key Concepts from FAIR

1. **Loss Event Frequency (LEF)** - How often loss events occur annually
2. **Loss Magnitude (LM)** - Financial impact per event
3. **Annual Loss Expectancy (ALE)** - LEF × LM
4. **PERT Distribution** - Three-point estimates (min, most likely, max)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=rap

# Format code
black rap tests
ruff check rap tests

# Type checking
mypy rap
```

## License

MIT License

## References

- [Open FAIR](https://www.opengroup.org/forum/open-fair-forum) - Open Group FAIR Standard
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)
- [Gartner Digital Risk Management](https://www.gartner.com)
