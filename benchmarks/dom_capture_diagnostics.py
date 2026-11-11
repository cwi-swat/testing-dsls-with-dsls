"""Instrument the installed capture script only within benchmark runs."""


def instrument_capture(script, *, json_transport=False):
    def replace_once(text, before, after):
        if text.count(before) != 1:
            raise RuntimeError("Capture script changed; update the benchmark DOM instrumentation")
        return text.replace(before, after, 1)

    stages = (
        ("attributes", '        save("playwright.dom.tagName", element.tagName);',
         '        save("playwright.dom.textContent", element.textContent);'),
        ("text", '        save("playwright.dom.textContent", element.textContent);',
         '        for (const name of liveNames) {'),
        ("live_values", '        for (const name of liveNames) {',
         '        const bounds = element.getBoundingClientRect();'),
        ("bounds", '        const bounds = element.getBoundingClientRect();',
         '        if (options.computedStyles.length > 0) {'),
        ("computed_styles", '        if (options.computedStyles.length > 0) {',
         '        if (Object.keys(aliases).length > 0) {'),
    )
    # Insert each boundary once, ending the previous stage before starting the next.
    for index, (name, start, end) in enumerate(stages):
        prefix = "" if index == 0 else (
            f"        __times.{stages[index - 1][0]} += performance.now() - __start_{stages[index - 1][0]};\n")
        script = replace_once(script, start,
            prefix + f"        const __start_{name} = performance.now();\n" + start)
    name, start, end = stages[-1]
    script = replace_once(script, end,
        f"        __times.{name} += performance.now() - __start_{name};\n" + end)
    script = replace_once(script, 'properties: propertiesFor(current.element)',
        'properties: __propertiesFor(current.element)')
    instrumented = """(options) => {
    const __times = {attributes: 0, text: 0, live_values: 0, bounds: 0, computed_styles: 0};
    let __propertiesMillis = 0;
    function __propertiesFor(element) {
        const started = performance.now();
        const properties = __readProperties(element);
        __propertiesMillis += performance.now() - started;
        return properties;
    }
    let __readProperties;
    const started = performance.now();
    const capture = (""" + replace_once(script, '    nodes.push({ path: "#document",',
        '    __readProperties = propertiesFor;\n    nodes.push({ path: "#document",') + """)(options);
    const browserMillis = performance.now() - started;
    const jsonTransport = __JSON_TRANSPORT__;
    const encodingStarted = performance.now();
    const captureJson = jsonTransport ? JSON.stringify(capture) : null;
    const jsonEncodingMillis = jsonTransport ? performance.now() - encodingStarted : 0;
    const sizeStarted = performance.now();
    const jsonBytes = new TextEncoder().encode(jsonTransport ? captureJson : JSON.stringify(capture)).byteLength;
    const sizeMeasurementMillis = performance.now() - sizeStarted;
    const propertyCount = Object.keys(capture.properties).length
        + capture.nodes.reduce((count, node) => count + Object.keys(node.properties).length, 0);
    return {capture: jsonTransport ? captureJson : capture, diagnostics: {
        transport: jsonTransport ? "json" : "object",
        json_encoding_millis: jsonEncodingMillis,
        browser_millis: browserMillis,
        property_read_millis: __propertiesMillis,
        traversal_and_result_millis: Math.max(0, browserMillis - __propertiesMillis),
        property_stages_millis: __times,
        size_measurement_millis: sizeMeasurementMillis,
        json_bytes: jsonBytes,
        widget_count: capture.nodes.length,
        property_count: propertyCount
    }};
}
"""
    return instrumented.replace("__JSON_TRANSPORT__", "true" if json_transport else "false")
