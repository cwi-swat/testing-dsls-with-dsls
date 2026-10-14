"""JavaScript readers used by the synchronous Playwright backend.

These expressions run inside the page, not in Python. Readers return plain data;
only the reachability expression scrolls. A snapshot describes one moment and
cannot guarantee that the page will remain unchanged until execution.
"""

# JavaScript runs in the browser, while this Python code runs the test.
# These strings read data or check reachability; only _REACHABILITY_JS scrolls.
_TARGET_SELECTOR_JS = '''el => {
            for (const attribute of ['id', 'name']) {
                const value = el.getAttribute(attribute);
                if (value) {
                    const selector = el.tagName.toLowerCase() +
                        '[' + attribute + '="' + CSS.escape(value) + '"]';
                    if (document.querySelectorAll(selector).length === 1)
                        return selector;
                }
            }
            // Walk up the HTML tree, locating each child by its tag position.
            const parts = [];
            for (let node = el; node; node = node.parentElement) {
                const tag = node.tagName.toLowerCase();
                let position = 1;
                for (let sibling = node.previousElementSibling; sibling;
                     sibling = sibling.previousElementSibling) {
                    if (sibling.tagName === node.tagName) position++;
                }
                parts.unshift(tag + ':nth-of-type(' + position + ')');
            }
            const selector = parts.join(' > ');
            if (document.querySelector(selector) !== el)
                throw new Error('Cannot describe this target with a main-DOM CSS selector');
            return selector;
        }'''

_ELEMENT_INFO_JS = '''el => {
            // Rectangle coordinates are relative to the visible viewport.
            const box = el.getBoundingClientRect();
            // Collect useful properties/attributes for the action log.
            const attributes = {};
            for (const name of ['href', 'src', 'alt', 'title', 'placeholder', 'value', 'name', 'aria-label', 'role']) {
                // Prefer a DOM property (e.g. current input value or full href).
                const value = el[name] ?? el.getAttribute(name);
                // Keep an empty current value: the field may have been cleared.
                if (value != null && (name === 'value' || value !== ''))
                    attributes[name] = String(value);
            }
            // Return plain data; Playwright converts this object to a Python dict.
            // Add scroll offsets to report location relative to the document.
            return {tag_name: el.tagName.toLowerCase(), id: el.id,
                class: el.getAttribute('class') || '', type: el.type || '',
                text: el.innerText || '',
                location: {x: box.x + scrollX, y: box.y + scrollY},
                size: {height: box.height, width: box.width}, attributes};
        }'''



# Read enabled status and ID uniqueness for all visible candidates.
_CANDIDATE_SNAPSHOT_JS = '''elements => {
            const counts = new Map();
            // One pass instead of a separate DOM search for each candidate ID.
            for (const el of document.querySelectorAll('[id]')) {
                counts.set(el.id, (counts.get(el.id) || 0) + 1);
            }
            return elements.map(el => {
                // Check ancestors, including crossing an open shadow root.
                let ariaCheck = false;
                for (let node = el; node;
                     node = node.parentElement || node.getRootNode().host) {
                    if (node.hasAttribute('aria-disabled')) ariaCheck = true;
                }
                return {
                    id: el.id || '',
                    unique_id: el.getRootNode() === document && !!el.id && counts.get(el.id) === 1,
                    enabled: !!el.closest('fieldset[disabled]') || !el.matches(':disabled'),
                    enabled_check: ariaCheck || !!el.closest('fieldset[disabled]')
                };
            });
        }'''


# Scroll one element and check whether its center receives pointer events.
_REACHABILITY_JS = '''el => {
            // Scroll immediately, rather than starting a smooth animation.
            // This can reveal an ordinary off-screen button, but cannot
            // open a sidebar that has been moved away with CSS.
            el.scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});

            // Get the rectangle relative to the viewport, not the full page.
            const box = el.getBoundingClientRect();
            const x = box.left + box.width / 2;
            const y = box.top + box.height / 2;

            // A point outside the viewport cannot receive a pointer click.
            if (box.width <= 0 || box.height <= 0 ||
                x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) {
                return false;
            }

            // Hit testing returns the topmost element that receives pointer
            // events here. An overlay will be returned instead of our button.
            const topElement = document.elementFromPoint(x, y);

            // A child is also fine: clicking a span inside a button counts
            // as clicking that button. null or an unrelated element is not.
            return topElement !== null &&
                (topElement === el || el.contains(topElement));
        }'''


# Ordinary inputs can be checked during the same browser call as their data.
# For ARIA, fieldsets and shadow DOM, retain Playwright's own rules rather
# than trying to reproduce those more complicated rules here.
_EDITABILITY_JS = """el => {
    let needsPlaywright = el.getRootNode() !== document || !!el.closest('fieldset');
    for (let node = el; node;
         node = node.parentElement || node.getRootNode().host) {
        if (node.hasAttribute('aria-disabled') || node.hasAttribute('aria-readonly'))
            needsPlaywright = true;
    }
    return {
        editable: !el.disabled && !el.readOnly,
        editable_check: needsPlaywright
    };
}"""


# Read one description in one call. These strings contain JavaScript code.
_DESCRIPTION_DATA_JS = (
    "el => { const readInfo = (" + _ELEMENT_INFO_JS + "); "
    "const readSelector = (" + _TARGET_SELECTOR_JS + "); "
    "const readEditability = (" + _EDITABILITY_JS + "); "
    "return {target: readInfo(el), selector: readSelector(el), ...readEditability(el), "
    "option_labels: el.tagName.toLowerCase() === 'select' ? "
    "Array.from(el.querySelectorAll('option')).map(option => option.label) : []}; }"
)


# Read targets with known unique IDs in one browser call, preserving order.
# Missing or ambiguous targets are errors; do not silently describe another one.
_DESCRIPTION_LIST_JS = (
    "ids => { const readInfo = (" + _ELEMENT_INFO_JS + "); "
    "const readEditability = (" + _EDITABILITY_JS + "); "
    "const targets = new Map(); "
    "for (const el of document.querySelectorAll('[id]')) { "
    "if (!targets.has(el.id)) targets.set(el.id, []); targets.get(el.id).push(el); } "
    "return ids.map(id => { const matches = targets.get(id) || []; "
    "if (matches.length !== 1) throw new Error('Description target missing or ambiguous: ' + id); "
    "const el = matches[0]; "
    "const selector = el.tagName.toLowerCase() + '[id=\"' + CSS.escape(id) + '\"]'; "
    "return {target: readInfo(el), selector: selector, ...readEditability(el), "
    "option_labels: el.tagName.toLowerCase() === 'select' ? "
    "Array.from(el.querySelectorAll('option')).map(option => option.label) : []}; }); }"
)



