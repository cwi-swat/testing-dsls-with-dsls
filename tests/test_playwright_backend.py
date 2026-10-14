"""Local Chromium integration checks (requires Playwright's browser install)."""
import sys
import json
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'testar'))
from playwright_backend import PlaywrightBackend, PlaywrightSession
from browser_test_support import open_session


class PlaywrightTests(unittest.TestCase):
    def test_new_session_does_not_inherit_cookies_or_storage(self):
        backend = PlaywrightBackend(headless=True)
        def open_local_page(session):
            # Fulfil locally so both sessions use the same origin without network access.
            session.page.route('http://minitestar.test/**',
                               lambda route: route.fulfill(body='<p>Local test</p>', content_type='text/html'))
            session.page.goto('http://minitestar.test/')
        first = backend.start('about:blank')
        try:
            open_local_page(first)
            first.page.evaluate("localStorage.setItem('previous_run', 'yes'); document.cookie = 'previous_run=yes'")
            self.assertEqual(first.page.evaluate("localStorage.getItem('previous_run')"), 'yes')
            self.assertIn('previous_run=yes', first.page.evaluate('document.cookie'))
        finally:
            first.close()
        second = backend.start('about:blank')
        self.addCleanup(second.close)
        open_local_page(second)
        self.assertIsNone(second.page.evaluate("localStorage.getItem('previous_run')"))
        self.assertEqual(second.page.evaluate('document.cookie'), '')

    def test_no_candidates_returns_no_actions(self):
        session = open_session(self)
        session.page.set_content('<p>No controls</p><input hidden><button disabled>Disabled</button>')
        self.assertEqual(session.derive_actions([]), [])
        self.assertEqual(session.actionable_element_count, 0)

    def test_nested_filters_can_exclude_every_candidate(self):
        session = open_session(self)
        session.page.set_content('<button>A</button><input><select></select>')
        filters = [lambda page: [[], [page.locator('button'), [page.locator('input, select')]]]]
        self.assertEqual(session.derive_actions(filters), [])

    def test_empty_dropdown_offers_click_and_arrows(self):
        session = open_session(self)
        session.page.set_content('<select id="empty"></select>')
        actions = session.derive_actions([])
        self.assertEqual([(a['kind'], a['parameters']) for a in actions], [
            ('click', {}), ('press_key', {'key': 'ArrowUp'}), ('press_key', {'key': 'ArrowDown'})])

    def test_click_reaches_application_handler(self):
        session = open_session(self)
        session.page.set_content('<button onclick="window.clicks = (window.clicks || 0) + 1">Save</button>')
        action = session.derive_actions([])[0]
        self.assertIsNone(session.page.evaluate('window.clicks'))
        result = session.execute_action_description(action)
        self.assertEqual(result.status, 'execution_succeeded', result.error)
        self.assertEqual(session.page.evaluate('window.clicks'), 1)

    def test_start_releases_resources_when_navigation_fails(self):
        # A failed goto must not leave a Chromium process or service behind.
        runtime = Mock()
        browser = runtime.chromium.launch.return_value
        page = browser.new_context.return_value.new_page.return_value
        error = RuntimeError('navigation failed')
        page.goto.side_effect = error
        with patch('playwright_backend.sync_playwright') as factory:
            factory.return_value.start.return_value = runtime
            with self.assertRaises(RuntimeError) as caught:
                PlaywrightBackend(headless=True, timeout=321).start('about:blank')
        self.assertIs(caught.exception, error)
        page.set_default_timeout.assert_called_once_with(321)
        browser.close.assert_called_once()
        runtime.stop.assert_called_once()

    def test_start_stops_service_when_launch_fails(self):
        runtime = Mock()
        runtime.chromium.launch.side_effect = RuntimeError('launch failed')
        with patch('playwright_backend.sync_playwright') as factory:
            factory.return_value.start.return_value = runtime
            with self.assertRaisesRegex(RuntimeError, 'launch failed'):
                PlaywrightBackend().start('about:blank')
        runtime.stop.assert_called_once()

    def test_close_attempts_every_resource_even_when_cleanup_fails(self):
        for failing_resource in ['context', 'browser']:
            with self.subTest(resource=failing_resource):
                page, context, browser, runtime = Mock(), Mock(), Mock(), Mock()
                resources = {'context': context, 'browser': browser}
                resources[failing_resource].close.side_effect = RuntimeError('cleanup failed')
                session = PlaywrightSession(page, context, browser, runtime)
                with self.assertRaisesRegex(RuntimeError, 'cleanup failed'):
                    session.close()
                context.close.assert_called_once()
                browser.close.assert_called_once()
                runtime.stop.assert_called_once()

    def test_plain_description_builder_offers_exact_input_combinations(self):
        # Test the action contract independently of DOM reads and timing.
        data = {'selector': '#field', 'target': {'tag_name': 'input'}, 'option_labels': []}
        descriptions = PlaywrightSession._build_action_descriptions(data, True)
        typing = [d['parameters'] for d in descriptions if d['kind'] == 'type_text']
        self.assertEqual(len(typing), 9)
        self.assertEqual({(p['input_strategy'], p['mode']) for p in typing}, {
            (strategy, mode)
            for strategy in ['random_text', 'random_number', 'naughty_string']
            for mode in ['append', 'prepend', 'replace']
        })
        self.assertTrue(all(p['submit_key'] == 'Enter' for p in typing))
        self.assertEqual(PlaywrightSession._build_action_descriptions(data, False),
                         [{'kind': 'click', 'selector': '#field',
                           'target': data['target'], 'parameters': {}}])

    def test_excluded_candidates_do_not_need_additional_enabled_checks(self):
        session = open_session(self)
        session.page.set_content('<button id="excluded" aria-disabled="true">Skip</button>'
                                 '<button id="keep">Keep</button>')
        session.performance.enabled = True
        elements = session.derive_actionable_elements([lambda page: page.locator('#excluded')])
        self.assertEqual([element.get_attribute('id') for element in elements], ['keep'])
        self.assertNotIn('special_enabled', session.performance.breakdown('discovery'))

    def test_cleared_input_keeps_empty_current_value_in_info_and_descriptions(self):
        session = open_session(self)
        page = session.page
        page.set_content('<input id="name" value="Jan">')
        element = page.locator('#name')
        element.fill('')
        self.assertEqual(element.get_attribute('value'), 'Jan')
        self.assertEqual(session.get_element_info(element)['attributes']['value'], '')
        # Check both the individual reader and the batch reader used after discovery.
        individual = session.derive_action_descriptions([element])
        batch = session.derive_actions([])
        self.assertTrue(all(a['target']['attributes']['value'] == '' for a in individual + batch))

    def test_description_read_failure_propagates_original_error(self):
        from playwright.sync_api import TimeoutError
        session = open_session(self)
        session.page.set_content('<button>Target</button>')
        elements = session.derive_actionable_elements([])
        original_error = TimeoutError('description read failed')
        with patch.object(session, '_read_description_data', side_effect=original_error):
            with self.assertRaises(TimeoutError) as caught:
                session.derive_action_descriptions(elements)
        self.assertIs(caught.exception, original_error)

    def test_execution_timeout_is_failed_but_configuration_error_propagates(self):
        from playwright.sync_api import TimeoutError
        session = open_session(self)
        with patch.object(session, '_execute_action_description', side_effect=TimeoutError('disabled')):
            result = session.execute_action_description({})
            self.assertEqual(result.status, 'execution_failed')
            self.assertEqual(result.error_type, 'TimeoutError')
        with patch.object(session, '_execute_action_description', side_effect=ValueError('bad mode')):
            with self.assertRaises(ValueError):
                session.execute_action_description({})
        session.page.close()
        with patch.object(session, '_execute_action_description', side_effect=TimeoutError('closed')):
            with self.assertRaises(TimeoutError):
                session.execute_action_description({})

    def test_description_timeout_rediscovers_instead_of_reusing_old_elements(self):
        from playwright.sync_api import TimeoutError
        session = open_session(self)
        page = session.page
        page.set_content('<button id="old">Old</button>')
        original_describe = session.derive_action_descriptions
        seen = []
        def describe(elements):
            seen.append(elements)
            if len(seen) == 1:
                page.set_content('<button id="new">New</button>')
                raise TimeoutError('old position no longer exists')
            return original_describe(elements)
        filters = Mock(return_value=[])
        with patch.object(session, 'derive_action_descriptions', side_effect=describe):
            with patch.object(session, 'execute_action_description') as execute:
                actions = session.derive_actions([filters])
                execute.assert_not_called()
        self.assertEqual(filters.call_count, 2)
        self.assertIsNot(seen[0], seen[1])
        self.assertEqual([a['target']['id'] for a in actions], ['new'])

    def test_description_retries_are_bounded_and_do_not_hide_other_errors(self):
        from playwright.sync_api import TimeoutError
        session = open_session(self)
        session.page.set_content('<button>Target</button>')
        error = TimeoutError('description read timeout')
        with patch.object(session, 'derive_action_descriptions', side_effect=error) as describe:
            with patch.object(session, 'derive_actionable_elements', wraps=session.derive_actionable_elements) as discover:
                with self.assertRaises(TimeoutError) as caught:
                    session.derive_actions([])
                self.assertIs(caught.exception, error)
                self.assertEqual(describe.call_count, 3)
                self.assertEqual(discover.call_count, 3)
        with patch.object(session, 'derive_action_descriptions', side_effect=ValueError('bad code')) as describe:
            with self.assertRaises(ValueError):
                session.derive_actions([])
            describe.assert_called_once()

    def test_navigation_retry_repeats_discovery_with_fresh_filters(self):
        from playwright.sync_api import Error
        session = open_session(self)
        page = session.page
        page.set_content('<button id="old">Old</button>')
        filters = Mock(return_value=[])
        original_snapshot = session._snapshot_candidates
        calls = []
        def read_snapshot(candidates):
            calls.append(True)
            if len(calls) == 1:
                page.set_content('<button id="new">New</button>')
                raise Error('Execution context was destroyed, most likely because of a navigation')
            return original_snapshot(candidates)
        with patch.object(session, '_snapshot_candidates', side_effect=read_snapshot):
            with patch.object(page, 'wait_for_load_state', wraps=page.wait_for_load_state) as wait:
                descriptions = session.derive_actions([filters])
                wait.assert_called_once_with('domcontentloaded')
        self.assertEqual(filters.call_count, 2)
        self.assertEqual([a['target']['id'] for a in descriptions], ['new'])

    def test_discovery_retry_is_bounded_and_specific(self):
        from playwright.sync_api import Error
        session = open_session(self)
        navigation = Error('Execution context was destroyed')
        with patch.object(session, 'derive_actionable_elements', side_effect=navigation) as discover:
            with patch.object(session.page, 'wait_for_load_state') as wait:
                with self.assertRaises(Error) as caught:
                    session.derive_actions([])
                self.assertIs(caught.exception, navigation)
                self.assertEqual(discover.call_count, 3)
                self.assertEqual(wait.call_count, 2)
        other = Error('Unexpected browser error')
        with patch.object(session, 'derive_actionable_elements', side_effect=other) as discover:
            with patch.object(session.page, 'wait_for_load_state') as wait:
                with self.assertRaises(Error) as caught:
                    session.derive_actions([])
                self.assertIs(caught.exception, other)
                discover.assert_called_once()
                wait.assert_not_called()

    def test_target_disabled_after_discovery_is_skipped_before_action(self):
        from browser_backend import ActionNotReachable
        session = open_session(self)
        page = session.page
        page.set_content('<input id="precision" type="number" value="2">')
        elements = session.derive_actionable_elements([])
        descriptions = session.derive_action_descriptions(elements)
        page.locator('#precision').evaluate('el => el.disabled = true')
        with patch.object(session, '_is_reachable') as reachability:
            with patch.object(session, '_log') as logging:
                for action in descriptions:
                    self.assertEqual(session.execute_action_description(action).status, 'execution_skipped')
                logging.assert_not_called()
            reachability.assert_not_called()
        self.assertEqual(page.locator('#precision').input_value(), '2')

    def test_target_disabled_during_reachability_is_skipped(self):
        from browser_backend import ActionNotReachable
        session = open_session(self)
        page = session.page
        page.set_content('<button id="target">Click</button>')
        action = session.derive_action_descriptions(
            session.derive_actionable_elements([]))[0]
        def disable_during_check(element):
            element.evaluate('el => el.disabled = true')
            return True
        with patch.object(session, '_is_reachable', side_effect=disable_during_check):
            with patch.object(session, '_log') as logging:
                self.assertEqual(session.execute_action_description(action).status, 'execution_skipped')
                logging.assert_not_called()

    def test_batch_descriptions_match_individual_route(self):
        session = open_session(self)
        page = session.page
        page.set_content('<input id="number" type="number" value="2">'
                         '<button id="excluded">Skip</button>'
                         '<select id="choices"><option>A</option><option>B</option></select>'
                         '<button>Fallback</button>')
        elements = session.derive_actionable_elements([lambda p: p.locator('#excluded')])
        session.performance.enabled = True
        batch = session.derive_action_descriptions(elements)
        self.assertEqual(session.performance.breakdown('descriptions')['batch_snapshot']['calls'], 1)
        self.assertEqual(session.performance.breakdown('descriptions')['element_snapshot']['calls'], 1)
        # Fresh equivalent Locator objects deliberately use the fallback route.
        individual = session.derive_action_descriptions([
            page.locator('#number'), page.locator('#choices'), page.get_by_text('Fallback', exact=True)
        ])
        self.assertEqual(batch, individual)
        self.assertFalse(any(d['target']['id'] == 'excluded' for d in batch))
        # Read values again instead of retaining state data from discovery.
        page.locator('#number').fill('37')
        updated = session.derive_action_descriptions(elements)
        self.assertEqual(updated[0]['target']['attributes']['value'], '37')

    def test_description_snapshot_preserves_readers_and_editability(self):
        session = open_session(self)
        page = session.page
        page.set_content('''<input id="normal" type="text" value="hello">
            <input name="quoted&quot;name" type="text" readonly>
            <input id="aria" type="text" aria-readonly="true">
            <button>Plain button</button>
            <select><option label="First">One</option><option disabled>Two</option></select>''')
        elements = page.locator('input, button, select').all()
        for element in elements:
            data = session._read_description_data(element)
            self.assertEqual(data['target'], session.get_element_info(element))
            self.assertTrue(element.evaluate(
                '(el, selector) => document.querySelectorAll(selector).length === 1 '
                '&& document.querySelector(selector) === el', data['selector']))
            self.assertEqual(data['option_labels'],
                             element.locator('option').evaluate_all('options => options.map(o => o.label)'))
        session.performance.enabled = True
        descriptions = session.derive_action_descriptions(elements)
        for index in range(3):
            element = elements[index]
            selector = session._read_description_data(element)['selector']
            offered = [d for d in descriptions if d['selector'] == selector]
            self.assertEqual(len(offered), 12 if element.is_editable() else 1)
        self.assertEqual(session.performance.breakdown('descriptions')['element_snapshot']['calls'], len(elements))
        self.assertNotIn('element_info', session.performance.breakdown('descriptions'))
        self.assertNotIn('selector', session.performance.breakdown('descriptions'))

    def test_editability_batch_matches_playwright_and_is_read_again(self):
        session = open_session(self)
        page = session.page
        page.set_content("""<input id="normal"><input id="readonly" readonly>
            <input id="disabled" disabled><input id="aria" aria-readonly="true">
            <div aria-disabled="true"><input id="nested"></div>
            <fieldset disabled><legend><input id="legend"></legend>
              <input id="field"></fieldset>
            <input id="false" aria-disabled="false" aria-readonly="false">""")
        elements = page.locator('input').all()
        session.performance.enabled = True
        for changed in [False, True]:
            if changed:
                page.locator('#normal').evaluate('el => el.readOnly = true')
                page.locator('#readonly').evaluate('el => el.readOnly = false')
            descriptions = session.derive_action_descriptions(elements)
            for element in elements:
                selector = session._read_description_data(element)['selector']
                actions = [d for d in descriptions if d['selector'] == selector]
                self.assertEqual(len(actions), 12 if element.is_editable() else 1)
            # Only the five complex inputs require individual browser checks.
            self.assertEqual(session.performance.breakdown('descriptions')['editable']['calls'], 5)

    def test_candidate_snapshot_matches_playwright_checks(self):
        session = open_session(self)
        page = session.page
        page.set_content('''
            <input id="normal"><input id="hidden" type="hidden">
            <input id="disabled" disabled><input style="display:none">
            <button style="visibility:hidden">Hidden</button>
            <button style="opacity:0">Transparent</button>
            <fieldset disabled><legend><input id="legend"></legend><input id="field"></fieldset>
            <div aria-disabled="true"><button id="aria">Disabled</button></div>
            <div disabled role="button">Not a native disabled control</div>
            <a id="duplicate" href="#">One</a><a id="duplicate" href="#">Two</a>
        ''')
        candidates = page.locator("a, button, input, select, [onclick], [role='button']")
        expected = [el for el in candidates.all() if el.is_visible() and el.is_enabled()]
        # Isolate discovery checks from scrolling and hit testing.
        with patch.object(session, '_is_reachable', return_value=True):
            actual = session.derive_actionable_elements([])
        self.assertEqual([el.evaluate('el => el.outerHTML') for el in actual],
                         [el.evaluate('el => el.outerHTML') for el in expected])

    def test_action_descriptions_are_data_without_execution(self):
        session = open_session(self)
        page = session.page
        page.set_content('''<button id="button" onclick="window.clicked=true">Go</button>
            <input id="text" type="text" value="original">
            <input id="readonly" type="text" readonly>
            <select id="select"><option>A</option><option>B</option></select>''')
        elements = session.derive_actionable_elements([])
        # Fail if describing actions accidentally generates random input.
        with patch('playwright_backend.generate_random_text', side_effect=AssertionError), \
             patch('playwright_backend.generate_random_number', side_effect=AssertionError), \
             patch('playwright_backend.generate_naughty_string', side_effect=AssertionError):
            descriptions = session.derive_action_descriptions(elements)
        self.assertEqual(len(descriptions), 19)  # click + 12 input + click + 5 select
        self.assertEqual(json.loads(json.dumps(descriptions)), descriptions)
        self.assertEqual(page.locator('#text').input_value(), 'original')
        self.assertIsNone(page.evaluate('window.clicked'))
        self.assertEqual(page.locator('#select').input_value(), 'A')
        text_actions = [d for d in descriptions if d['target']['id'] == 'text']
        self.assertEqual([d['kind'] for d in text_actions],
                         ['click', 'press_key', 'press_key'] + ['type_text'] * 9)
        self.assertEqual(text_actions[3]['parameters']['input_strategy'], 'random_text')
        for description in descriptions:
            target = page.locator(description['selector'])
            self.assertEqual(target.get_attribute('id'), description['target']['id'])
        # Descriptions survive JSON storage and replacement of the DOM node.
        page.locator('#text').evaluate("el => el.outerHTML = '<input id=\"text\" type=\"text\">'")
        session.execute_action_description(json.loads(json.dumps(text_actions[3])), value='42')
        self.assertEqual(page.locator('#text').input_value(), '42')
        self.assertEqual(session.derive_action_descriptions([]), [])

    def test_selectors_and_missing_or_ambiguous_targets(self):
        """Cover the current ID/name/path queries, not the removed semantic API."""
        session = open_session(self)
        page = session.page
        page.set_content('<input id="amount" type="text">'
                         '<input name="customer" type="text">'
                         '<button onclick="window.clicked=true">Save</button>')
        descriptions = session.derive_action_descriptions(session.derive_actionable_elements([]))
        amount = next(d for d in descriptions if d['target']['id'] == 'amount'
                      and d['kind'] == 'type_text')
        customer = next(d for d in descriptions if d['target']['attributes'].get('name') == 'customer')
        save = next(d for d in descriptions if d['target']['tag_name'] == 'button')
        self.assertIn('[id=', amount['selector'])
        self.assertIn('[name=', customer['selector'])
        self.assertIn('nth-of-type', save['selector'])
        # A stable ID still resolves after an unrelated input is inserted.
        page.locator('body').evaluate("el => el.insertAdjacentHTML('afterbegin', '<input>')")
        session.execute_action_description(amount, value='42')
        self.assertEqual(page.locator('#amount').input_value(), '42')
        session.execute_action_description(save)
        self.assertTrue(page.evaluate('window.clicked'))
        page.locator('#amount').evaluate("el => el.insertAdjacentHTML('afterend', '<input id=\"amount\">')")
        self.assertEqual(session.execute_action_description(amount, value='1').status, 'execution_failed')
        page.locator('#amount').evaluate_all('elements => elements.forEach(el => el.remove())')
        self.assertEqual(session.execute_action_description(amount, value='1').status, 'execution_failed')

    def test_reachability_with_sidebar_overlay_and_scrolling(self):
        session = open_session(self)
        page = session.page
        page.set_content('''
            <style>
                #sidebar {position:fixed; left:0; top:0; width:200px;
                          transform:translateX(-250px)}
                #covered {position:absolute; top:100px; left:100px}
                #overlay {position:absolute; top:90px; left:90px;
                          width:200px; height:100px; z-index:10}
                #close {position:absolute; top:10px; left:10px}
                #below {position:absolute; top:2000px; left:100px}
            </style>
            <div id="sidebar"><a id="menu" href="#">All Items</a></div>
            <button id="covered">Covered</button>
            <div id="overlay"><button id="close"><span>Close</span></button></div>
            <button id="below">Below the fold</button>
        ''')
        elements = session.derive_actionable_elements([])
        self.assertEqual([el.get_attribute('id') for el in elements],
                         ['menu', 'covered', 'close', 'below'])
        self.assertEqual(page.evaluate('window.scrollY'), 0)
        descriptions = session.derive_action_descriptions(elements)
        for target in ['menu', 'covered']:
            action = next(a for a in descriptions
                          if a['kind'] == 'click' and a['target']['id'] == target)
            self.assertEqual(session.execute_action_description(action).status, 'execution_skipped')
        below = next(a for a in descriptions
                     if a['kind'] == 'click' and a['target']['id'] == 'below')
        session.execute_action_description(below)
        self.assertGreater(page.evaluate('window.scrollY'), 0)
        # Reachability was only an observation; clicking still occurs later.
        close = next(a for a in descriptions
                     if a['kind'] == 'click' and a['target']['id'] == 'close')
        self.assertEqual(session.execute_action_description(close).status, 'execution_succeeded')
        page.locator('#overlay').evaluate('el => el.remove()')
        self.assertTrue(session._is_reachable(page.locator('#covered')))

    def test_discovery_actions_and_replaced_element(self):
        session = open_session(self)
        page = session.page
        page.set_content('<input id="text" type="text"><a id="cart" href="#">Cart</a>'
                         '<button id="skip">skip</button><input disabled>'
                         '<input style="display:none"><select id="choices">'
                         '<option>A</option><option>B</option></select>')
        elements = session.derive_actionable_elements([
            lambda page: [page.locator('#skip'), page.locator('#absent')]
        ])
        self.assertEqual([el.get_attribute('id') for el in elements],
                         ['text', 'cart', 'choices'])
        descriptions = session.derive_action_descriptions(elements)
        cart_actions = [a for a in descriptions if a['target']['id'] == 'cart']
        self.assertEqual(len(cart_actions), 1)
        text_actions = [a for a in descriptions if a['target']['id'] == 'text']
        self.assertEqual(len(text_actions), 12)
        number = next(a for a in text_actions if a['kind'] == 'type_text'
                      and a['parameters']['input_strategy'] == 'random_number'
                      and a['parameters']['mode'] == 'replace')
        self.assertEqual(session.execute_action_description(number).status, 'execution_succeeded')
        self.assertTrue(page.locator('#text').input_value().isdigit())
        choice_actions = [a for a in descriptions if a['target']['id'] == 'choices']
        self.assertEqual(len(choice_actions), 5)
        choice = next(a for a in choice_actions if a['kind'] == 'select_option'
                      and a['parameters']['label'] == 'B')
        self.assertEqual(session.execute_action_description(choice).status, 'execution_succeeded')
        self.assertEqual(page.locator('#choices').input_value(), 'B')
        page.evaluate('document.querySelector("#text").outerHTML = "<input id=text type=text>"')
        updated = session.derive_action_descriptions(elements)
        text = next(a for a in updated if a['target']['id'] == 'text'
                    and a['kind'] == 'type_text'
                    and a['parameters']['input_strategy'] == 'random_text'
                    and a['parameters']['mode'] == 'replace')
        self.assertEqual(session.execute_action_description(text).status, 'execution_succeeded')
        self.assertEqual(len(page.locator('#text').input_value()), 10)


if __name__ == '__main__':
    unittest.main()
