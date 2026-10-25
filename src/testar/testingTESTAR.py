from pathlib import Path
from uuid import uuid4
from miniTESTAR import testar

def test_cambio():
    """Run the cambio app, without login or filters."""
    from playwright_backend import PlaywrightBackend

    testar(
        url='https://cambio.softwaretesting.nl/',
        num_runs=4,
        length_sequence=20,
        filter_elements=[],
        preparations=[],
        oracles=[],
        backend=PlaywrightBackend(),
        measure_timings=True,
    )

def test_sudoku():
    """Run the sudoku game, without login or filters."""
    from playwright_backend import PlaywrightBackend

    testar(
        url='https://sudoku.softwaretesting.nl/',
        num_runs=2,
        length_sequence=40,
        filter_elements=[],
        preparations=[],
        oracles=[],
        backend=PlaywrightBackend(),
        measure_timings=True,
    )

def test_random_generator():
    """Run the random generator with Playwright, without login or filters."""
    from playwright_backend import PlaywrightBackend

    testar(
        url='https://random-generator.softwaretesting.nl/',
        num_runs=4,
        length_sequence=30,
        filter_elements=[],
        preparations=[],
        oracles=[],
        backend=PlaywrightBackend(),
        measure_timings=True,
    )

def test_saucer():
    """Log in to SauceDemo, then test with Playwright and a visible-error oracle."""
    from playwright_backend import PlaywrightBackend

    def login(page):
        page.locator('#user-name').fill('standard_user')
        page.locator('#password').fill('secret_sauce')
        page.locator('#login-button').click()
        page.locator('.inventory_list').wait_for(state='visible')

    def filter_burger(page):
        return page.locator('#react-burger-menu-btn')

    def filter_external_links(page):
        return page.locator(
            'a[href*="twitter.com"], a[href*="x.com"], '
            'a[href*="facebook.com"], a[href*="linkedin.com"]'
        )

    def no_visible_error(page):
        """Report visible SauceDemo error messages after each action.

        This treats validation messages as findings too: random input can
        legitimately produce an error, so a finding is not necessarily a bug.
        """
        # SauceDemo marks its error message with data-test="error".
        # :visible ignores messages that exist in HTML but are hidden.
        messages = page.locator('[data-test="error"]:visible').all_inner_texts()
        # TESTARSteps catches AssertionError and records this message as a finding.
        assert not messages, 'Visible error message: ' + ' | '.join(messages)

    testar(
        url='https://www.saucedemo.com/',
        num_runs=3,
        length_sequence=30,
        filter_elements=[filter_burger, filter_external_links],
        preparations=[login],
        oracles=[no_visible_error],
        backend=PlaywrightBackend(),
        measure_timings=True,
    )

def parabank_no_internal_error(page):
    """Report a visible ParaBank internal error with its URL and a screenshot.

    This detects the application's error message, not a browser crash.
    TESTARSteps adds sequence/attempt numbers to this oracle finding.
    """
    messages = page.get_by_text('An internal error has occurred', exact=False).and_(
        page.locator(':visible')
    ).all_inner_texts()
    if messages:
        # Save evidence only when a visible internal error is found.
        url = page.url
        folder = Path(__file__).resolve().parents[2] / 'test-output' / 'parabank'
        screenshot = folder / f'internal-error-{uuid4().hex}.png'
        try:
            folder.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot), full_page=True, timeout=2000)
            evidence = f'Screenshot: {screenshot}'
        except Exception as error:
            # A screenshot failure must not hide the original oracle finding.
            evidence = f'Screenshot could not be saved: {error}'
        raise AssertionError(f"ParaBank internal error at {url}: "
                             + ' | '.join(messages) + f". {evidence}")


def test_parabank():
    """Log in to ParaBank and explore with Playwright, excluding selected links."""
    from playwright_backend import PlaywrightBackend

    def filter_external_links(page):
        return page.locator(
            'a[href*="parasoft.com"], a[href*="?_wadl&_type=xml"], '
            'a[href*="?wsdl"]'
        )

    def login(page):
        page.locator('input[name="username"]').fill('john')
        page.locator('input[name="password"]').fill('demo')
        page.locator('input[type="submit"][value="Log In"]').click()
        page.locator('#leftPanel').get_by_role('link', name='Log Out', exact=True).wait_for(
            state='visible'
        )

    testar(
        url='https://para.testar.org/',
        num_runs=3,
        length_sequence=50,
        filter_elements=[filter_external_links],
        preparations=[login],
        oracles=[parabank_no_internal_error],
        backend=PlaywrightBackend(),
        measure_timings=True,
    )


if __name__ == "__main__":
    # Run the tests below in order. Comment out any calls you want to skip.
    #test_cambio()
    #test_sudoku()
    test_random_generator()
    #test_saucer()
    #test_parabank()
