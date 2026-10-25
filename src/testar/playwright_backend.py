"""Browser operations for miniTESTAR using Playwright's synchronous API.

Backend starts the browser.
A session is for one test run and its cleanup.
Browser is the Chromium process.
Context keeps cookies/storage separate.
Page is one tab, stored in session.page. 
A Locator is a query used to find an element again, not a saved HTML node. 
"""
import json
from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError, Locator, sync_playwright
from input_data_generation import generate_random_text, generate_random_number, generate_naughty_string
from reporting import log_info, print_derivation_retry
from actions import ActionNotReachable, ActionResult
from playwright_dom import (
    _ELEMENT_INFO_JS,
    _CANDIDATE_SNAPSHOT_JS,
    _REACHABILITY_JS,
    _DESCRIPTION_DATA_JS,
    _DESCRIPTION_LIST_JS,
)

_OBSERVATION_ATTEMPTS = 3 # Maximum number of attempts, including the first, to derive actions.

_DEFAULT_TIMEOUT_MS = 10000  # Default timeout for waiting Playwright calls, in milliseconds.

# Use the same input choices when making and executing actions.
_INPUT_TYPES = ("text", "number", "email", "password")
_INPUT_MODES = ("append", "prepend", "replace")
_INPUT_STRATEGIES = ("random_text", "random_number", "naughty_string")
_TEXT_SUBMIT_KEY = 'Enter'  # Press after each text action; Enter can submit the form.

# This is a limited starting selection, not every interactive element.
# It omits textarea, contenteditable and other custom widget roles.
# [onclick] does not detect listeners registered with addEventListener.
_ACTIONABLE_SELECTORS = (
    'a',               # Links
    'button',          # Buttons
    'input',           # Text fields, numbers, checkboxes, radios, etc.
    'select',          # Dropdowns
    '[onclick]',       # Elements with an inline onclick attribute
    "[role='button']", # Custom elements declaring a button role
)


class PlaywrightBackend:
    def __init__(self, *, headless=False, timeout=_DEFAULT_TIMEOUT_MS):
        # False shows the browser window; True runs without a visible window.
        self.headless = headless
        # Use the default above, or a timeout supplied by the caller.
        self.timeout = timeout

    def start(self, url):
        """Open the SUT in Chromium and return a PlaywrightSession.

        Each run gets its own context, so cookies and stored data from a previous
        run do not affect it. If startup fails, close the browser and stop Playwright.
        """
        runtime = sync_playwright().start()
        browser = None
        try:
            browser = runtime.chromium.launch(headless=self.headless)
            # Separate cookies/storage for each run; use the browser window size.
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            page.set_default_timeout(self.timeout)
            page.goto(url)
            return PlaywrightSession(page, context, browser, runtime)
        except BaseException:
            # If startup fails or is interrupted, release resources and re-raise.
            try:
                if browser is not None:
                    browser.close()
            finally:
                runtime.stop()
            raise


class PlaywrightSession:
    def __init__(self, page, context, browser, runtime):
        # Existing preparations, filters and oracles receive this native Page.
        self.page = page
        # Keep ownership of these resources so close() can release them.
        self._context = context
        self._browser = browser
        self._runtime = runtime
        self._description_targets = {}
        self.actionable_element_count = 0

    def close(self):
        """Close the context and browser, then stop Playwright.

        Use finally so we still try the remaining cleanup if closing one part fails.
        """
        try:
            self._context.close()
        finally:
            try:
                self._browser.close()
            finally:
                self._runtime.stop()

    def derive_actions(self, filters):
        """Get actionable elements, then make their action descriptions.

        The page can change between these steps. If this causes a temporary
        browser error, get fresh elements and make descriptions again.
        Try at most _OBSERVATION_ATTEMPTS times; then propagate the error.
        """
        for attempt in range(_OBSERVATION_ATTEMPTS):
            reading_descriptions = False
            try:
                elements = self.derive_actionable_elements(filters)
                self.actionable_element_count = len(elements)
                reading_descriptions = True
                descriptions = self.derive_action_descriptions(elements)
                return descriptions
            except PlaywrightError as error:
                message = str(error)
                temporary = any(text in message for text in (
                    'Execution context was destroyed', 'Element is not attached',
                    'Description target missing or ambiguous',
                )) or (reading_descriptions and isinstance(error, PlaywrightTimeoutError))
                if (not temporary or attempt == _OBSERVATION_ATTEMPTS - 1 or self.page.is_closed()
                        or not self._browser.is_connected()):
                    raise
                print_derivation_retry(attempt + 2, _OBSERVATION_ATTEMPTS)
                if 'Execution context was destroyed' in message:
                    self.page.wait_for_load_state('domcontentloaded')

    def derive_actionable_elements(self, filters):
        """Get the visible and enabled elements in the current Page.
        Remove elements matched by the filters.

        An element can be visible but covered by a dialog or become disabled after this step,
        we check that later when we are executing the selected action. 

        derive_actions() handles retries if the page changes while deriving actions.
        """
        
        self._description_targets = {}
        
        # Get the Locators excluded by the given filters.
        excluded = self._get_excluded_locators(filters)

        combined_selector = ", ".join(_ACTIONABLE_SELECTORS)

        # Make a query for visible candidates; _snapshot_candidates() reads them
        # in one browser call instead of checking visibility element by element.
        candidate_query = ':is(' + combined_selector + '):visible'
        visible_candidates = self.page.locator(candidate_query)
        snapshot = self._snapshot_candidates(visible_candidates)
        # snapshot contains data read for each candidate, not HTML elements.
        # Build Locators for the candidates we keep, so action descriptions can
        # find those elements again.
        elements = []
        for index, info in enumerate(snapshot):
            # Skip disabled elements.
            if not info['enabled']:
                continue
            # Prefer a unique ID; a position-based Locator can shift after DOM changes.
            if info['unique_id']:
                element = self.page.locator('[id=' + json.dumps(info['id']) + ']')
            else:
                element = visible_candidates.nth(index)
            # Remove excluded/filtered candidates.
            if self._is_excluded(element, excluded):
                continue
            if info['enabled_check']:
                # For complex cases/ARIA, check whether the element is enabled according to Playwright's own rules.
                if not element.is_enabled():
                    continue
            elements.append(element)
            if info['unique_id']:
                # Remember unique IDs to read descriptions together in one browser call.
                self._description_targets[element] = info['id']
        return elements

    def _get_excluded_locators(self, filters):
        """Call the filters with the page and collect which elements to exclude.
        """
        excluded = []
        for callback in filters:
            result = callback(self.page)
            self._collect_filter_results(result, excluded)
        return excluded

    def _collect_filter_results(self, value, excluded):
        """Put the Locators returned by a filter into one list.

        A filter may return a single Locator or nested iterables of Locators.
        Keep each Locator as one item, even if it matches several elements.
        """
        if isinstance(value, Locator):
            excluded.append(value)
        else:
            for item in value:
                self._collect_filter_results(item, excluded)

    def _is_excluded(self, element, excluded):
        """Check whether this element is matched by any of the filters.

        Compare what the Locators find in the page, rather than the Python objects.
        """
        for locator in excluded:
            if element.and_(locator).count() > 0:
                return True
        return False
    
    def _snapshot_candidates(self, candidates):
        """Read whether the candidates are enabled and whether their IDs are unique.

        Read all candidates in one browser call for speed. For more complicated
        enabled checks, the returned data tells us to use element.is_enabled().
        """
        return candidates.evaluate_all(_CANDIDATE_SNAPSHOT_JS)

    def _is_reachable(self, element):
        """Scroll to the element and check whether its center can be clicked.

        A dialog or another element may cover it. A child inside the element,
        such as text inside a button, is fine. We check the center only; an edge
        might still be clickable even when this check returns False.
        """
        return element.evaluate(_REACHABILITY_JS)

    def _type(self, element, name, value, mode='append'):
        """Type text using append, prepend or replace, then press _TEXT_SUBMIT_KEY.

        Move the cursor to the end for append and to the start for prepend.
        Clear the field first for replace. This gives each mode a fixed meaning,
        regardless of where the cursor was before the action.
        Type character by character so the browser can reject invalid characters
        in number fields. The logged text is what we try to type; the final field
        value can therefore differ. The submit key is configured in _TEXT_SUBMIT_KEY.
        """
        if mode not in _INPUT_MODES:
            raise ValueError('Unknown input mode: ' + str(mode))
        self._log(name + ' (' + mode + ')', element, value)
        if mode == 'replace':
            # Clear first; fill(value) would reject invalid text in number inputs.
            element.fill("")
        elif mode == 'prepend':
            element.press('Home')
        else:
            element.press('End')
        element.press_sequentially(value)
        element.press(_TEXT_SUBMIT_KEY)


    def derive_action_descriptions(self, elements):
        """Read the actionable elements and make their action descriptions.

        Read elements with known unique IDs together to save browser calls.
        Read the other elements individually. Check whether inputs are editable
        before offering typing actions, then use _build_action_descriptions().
        Store the input strategy here; generate the text only when executing.
        """
        descriptions = []

        # Read known unique-ID targets together; other Locators use individual calls.
        known = [el for el in elements if el in self._description_targets]
        data_by_element = {}
        if known:
            target_ids = [self._description_targets[el] for el in known]
            snapshots = self.page.evaluate(_DESCRIPTION_LIST_JS, target_ids)
            data_by_element = dict(zip(known, snapshots))

        for element in elements:
            data = data_by_element.get(element)
            if data is None:
                # Without a recorded unique ID, read this Locator individually.
                data = self._read_description_data(element)
            target = data['target']
            tag = target['tag_name']
            kind = target['type']

            # Ordinary input editability was read with the other element data:
            # disabled and readonly fields must not receive typing actions.
            editable = False
            if tag == 'input' and kind in _INPUT_TYPES:
                if data['editable_check']:
                    # Complex cases still use this Playwright version's exact rules.
                    editable = element.is_editable()
                else:
                    editable = data['editable']
            descriptions.extend(self._build_action_descriptions(data, editable))

        return descriptions

    @staticmethod
    def _build_action_descriptions(data, editable):
        """Make the action descriptions from the data already read for one element.

        Offer a click for every element, arrows for editable inputs and dropdowns,
        typing for editable inputs, and option selections for dropdowns.
        Keep descriptions as dictionaries so they can be stored as JSON.
        Each contains the action kind, selector, target information and parameters.
        """
        descriptions = []

        def add(kind, parameters):
            descriptions.append({
                'kind': kind,
                'selector': data['selector'],
                'target': data['target'],
                'parameters': parameters,
            })

        add('click', {})
        if editable or data['target']['tag_name'] == 'select':
            add('press_key', {'key': 'ArrowUp'})
            add('press_key', {'key': 'ArrowDown'})
        if editable:
            for strategy in _INPUT_STRATEGIES:
                for mode in _INPUT_MODES:
                    add('type_text', {
                        'input_strategy': strategy,
                        'mode': mode,
                        'submit_key': _TEXT_SUBMIT_KEY,
                    })
        elif data['target']['tag_name'] == 'select':
            for label in data['option_labels']:
                add('select_option', {'label': label})
        return descriptions

    def _read_description_data(self, element):
        """Read the element information needed to make its action descriptions.

        Read its selector, properties, editability and dropdown labels together
        to save browser calls. Some editability checks still need is_editable().
        """
        return element.evaluate(_DESCRIPTION_DATA_JS)

    def execute_action(self, description, value=None):
        """Execute the action once and return its ActionResult.

        execution_succeeded means the browser calls completed.
        execution_skipped means the element was disabled or covered.
        execution_failed means a timeout, changed page or missing/ambiguous target
        prevented completion.
        Do not repeat a failed action: it may already have partly happened.
        Invalid descriptions, unexpected errors and a closed browser propagate.
        """
        try:
            self._execute_action_description(description, value=value)
            return ActionResult('execution_succeeded')
        except ActionNotReachable as error:
            # The intended action did not begin; the core can try another target.
            return ActionResult('execution_skipped', str(error), type(error).__name__)
        except PlaywrightError as error:
            # Browser/tab gone: propagate the error and stop the run.
            if self.page.is_closed() or not self._browser.is_connected():
                raise
            message = str(error)
            temporary = isinstance(error, PlaywrightTimeoutError) or any(
                text in message for text in (
                    'Execution context was destroyed',
                    'Element is not attached to the DOM',
                    'Element is not attached',
                ))
            # Only recognised temporary browser problems become failed results.
            if not temporary:
                raise
            # The action may have partly happened; the next step must get new actions.
            return ActionResult('execution_failed', message, type(error).__name__)

    def _execute_action_description(self, description, value=None):
        """Find the element, check whether it is reachable, then execute the action.

        The selector must find exactly one element; otherwise report a failure.
        If the element is disabled or covered, skip it.
        For type_text, generate text using input_strategy unless the caller
        supplies a value. An empty string is also a supplied value.
        execute_action() converts reachability and recognised browser errors into results.
        Invalid descriptions and unexpected errors propagate.
        """
        element = self.page.locator(description['selector'])
        # execute_action() converts a missing or ambiguous match to execution_failed.
        if element.count() != 1:
            raise PlaywrightTimeoutError('The action selector must match exactly one element')
        # Scroll only toward the chosen target, not toward every candidate.
        # A blocked or disabled target is skipped before generating input.
        reachable = self._check_action_reachability(element)
        if not reachable:
            raise ActionNotReachable(description['selector'])
        kind = description['kind']
        parameters = description['parameters']
        if kind == 'click':
            self._log('click', element)
            element.click()
        elif kind == 'press_key':
            key = parameters['key']
            self._log('press key', element, key)
            element.press(key)
        elif kind == 'type_text':
            if parameters['mode'] not in _INPUT_MODES or parameters['submit_key'] != _TEXT_SUBMIT_KEY:
                raise ValueError(f'Only append, prepend or replace followed by {_TEXT_SUBMIT_KEY} is supported')
            # Generate now unless the caller supplied an actual input value.
            if value is None:
                generators = {
                    'random_text': generate_random_text,
                    'random_number': generate_random_number,
                    'naughty_string': generate_naughty_string,
                }
                strategy = parameters['input_strategy']
                if strategy not in generators:
                    raise ValueError('Unknown input strategy: ' + str(strategy))
                value = generators[strategy]()
            if not isinstance(value, str):
                raise ValueError('type_text requires a string value')
            self._type(element, 'type text keys', value, mode=parameters['mode'])
        elif kind == 'select_option':
            label = parameters['label']
            self._log('select dropdown option', element, label)
            element.select_option(label=label)
        else:
            raise ValueError('Unknown action kind: ' + str(kind))

    def _check_action_reachability(self, element):
        """Check that the element is enabled and that its center can be clicked.

        Check enabled again after scrolling, because scrolling may change the
        page. False tells the caller to skip this element.
        """
        return (element.is_enabled() and self._is_reachable(element)
                and element.is_enabled())

    @staticmethod
    def get_element_info(element):
        """Read the element properties used in action descriptions and the log.

        Include the current field value and its position in the document.
        Read again for logging, because the element may have changed since
        its action description was made.
        """
        return element.evaluate(_ELEMENT_INFO_JS)

    def _log(self, action, element, *args):
        """Log the action with the current element information before executing it.
        """
        log_info(action, self.get_element_info(element), *args)
