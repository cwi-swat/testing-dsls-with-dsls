#! /usr/bin/env python3

from miniTESTAR import testar
from pathlib import Path
import importlib.util
from playwright_backend import PlaywrightBackend

def load_oracles(html):
    """Load oracle functions from the Python file beside the HTML file.

    If the file is missing, has no oracles or cannot be loaded, print why and
    return []. The QL run can then continue without oracle checks.
    """
    oracle_path = html.with_suffix('.py')
    if not oracle_path.is_file():
        print(f'No oracle file: {oracle_path.name}. Running without oracles.')
        return []
    try:
        spec = importlib.util.spec_from_file_location('ql_oracle_' + html.stem, oracle_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        oracles = [value for name, value in vars(module).items()
                   if name.endswith('_oracle') and callable(value)]
    except Exception as error:
        print(f'Could not load {oracle_path.name}: {type(error).__name__}: {error}. '
              'Running without oracles.')
        return []
    if not oracles:
        print(f'No oracle functions in {oracle_path.name}. Running without oracles.')
    return oracles


def testar_QL_webApp(full_path, *, measure_timings=False):
    html = Path(full_path).resolve()
    oracles = load_oracles(html)
    testar(
        url=html.as_uri(),
        num_runs=3,
        length_sequence=10,
        filter_elements=[],
        preparations=[],
        oracles=[],
        backend=PlaywrightBackend(),
        measure_timings=measure_timings,
    )


def test_name(name, *, measure_timings=False):
    """Find a generated HTML example relative to the project, not the terminal."""
    html = Path(__file__).resolve().parents[2] / 'examples' / (name + '.html')
    if not html.is_file():
        raise FileNotFoundError(f'Generate {name}.html from examples/{name}.myql first')
    testar_QL_webApp(str(html), measure_timings=measure_timings)


if __name__ == "__main__":
    #test_name("tax")
    #test_name("loan_approval")
    #test_name("shopping_cart")
    #test_name("travel_booking")
    #test_name("age_boundaries")
    #test_name("calculation_chain")
    #test_name("feature_switches")
    #test_name("language_constructs")
    #test_name("01_tax_office")
    #test_name("02_phq9_gad7")
    #test_name("03_huurtoeslag")
    #test_name("04_mortgage_urla")
    #test_name("05_us_form1040")
    #test_name("06_who_verbal_autopsy")
    #test_name("acs_household_1", measure_timings=True)
    #test_name("acs_household_5", measure_timings=True)
    test_name("acs_household_20", measure_timings=True)
    test_name("acs_household_100", measure_timings=True)
    #test_name("acs_household_500", measure_timings=True)
