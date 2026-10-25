"""Steps of the TESTAR approach; miniTESTAR controls their order and repetition."""
import random

from browser_backend import BrowserBackend
from performance import PerformanceMeasurements
from reporting import print_oracle_finding, print_oracle_error

class TESTARSteps:
    """Use a browser session for browser work and provide selection and oracle steps.

    A wrapper can offer the same methods and add work before or after each step.
    This implementation has no dependency on a recorder or evidence format.
    """

    def __init__(self, *, backend: BrowserBackend, filters=(), preparations=(), oracles=()):
        self.backend = backend
        self.filters = filters
        self.preparations = preparations
        self.oracles = oracles
        self.session = None
        self.performance = PerformanceMeasurements()
        self.actionable_element_count = None

    def begin_sequence(self, url):
        """Open a fresh session and prepare the application, such as logging in.

        Preparations receive the native browser object and must match the backend.
        Close the new session if a preparation fails or is interrupted.
        """
        self.session = self.backend.start(url)
        try:
            self._prepare_performance_measurements()

            # Prepare the application, for example by logging in.
            for prepare in self.preparations:
                prepare(self.session.page)
        except BaseException:
            self.end_sequence()
            raise

    def _prepare_performance_measurements(self):
        """Reset the element count and use the session's measurements if available.

        Sharing the recorder includes the browser's detailed timings. A session
        without its own recorder still gets the timings measured by the loop.
        """
        self.actionable_element_count = None
        performance = getattr(self.session, 'performance', None)
        if performance is None:
            performance = PerformanceMeasurements()
        self.performance = performance

    def derive_actions(self):
        """Ask the session for actions, applying the configured element filters.

        Some backends also report an element count for timing output. An absent
        count means unknown, not zero; it is not needed to choose an action.
        """
        actions = self.session.derive_actions(self.filters)
        self.actionable_element_count = getattr(self.session, 'actionable_element_count', None)
        return actions

    def select_action(self, possible_actions):
        """Choose randomly from the nonempty list supplied by the loop."""
        selected_action_id = int(random.randint(0, len(possible_actions) - 1))
        return possible_actions[selected_action_id]

    def execute_action(self, action, value=None):
        """Execute once through the session; do not replay a failed action."""
        return self.session.execute_action(action, value=value)

    def check_oracles(self, findings, sequence, attempt):
        """Run each oracle and count its call, including findings and errors.

        Preserve the existing policy: assertion failures become findings;
        unexpected exceptions print a message and pause for terminal input.
        """
        checked = 0
        for oracle in self.oracles:
            checked += 1
            try:
                oracle(self.session.page)
            except AssertionError as error:
                findings.append(print_oracle_finding(oracle.__name__, error, sequence, attempt))
            except Exception as error:
                print_oracle_error(oracle.__name__, error)
                input('')
        return checked

    def end_sequence(self):
        """Release the session, including when an earlier step failed."""
        if self.session is not None:
            try:
                self.session.close()
            finally:
                self.session = None
