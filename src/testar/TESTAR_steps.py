"""Steps of the TESTAR approach; miniTESTAR controls their order and repetition."""
import random

from browser_backend import BrowserBackend
from reporting import print_oracle_finding, print_oracle_error, print_test_summary

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

    def begin_test(self):
        """Start the whole test; the ordinary steps need no test-wide setup."""
        pass

    def begin_sequence(self, url):
        """Open a fresh session and prepare the application, such as logging in.

        Preparations receive session.page and must match the selected backend.
        Close the new session if a preparation fails or is interrupted.
        """
        self.session = self.backend.start(url)
        try:
            # Prepare the application, for example by logging in.
            for prepare in self.preparations:
                prepare(self.session.page)
        except BaseException:
            self.end_sequence()
            raise

    def derive_actions(self):
        """Ask the session for actions, applying the configured element filters."""
        return self.session.derive_actions(self.filters)

    def select_action(self, possible_actions):
        """Choose randomly from the nonempty list supplied by the loop."""
        selected_action_id = int(random.randint(0, len(possible_actions) - 1))
        return possible_actions[selected_action_id]

    def execute_action(self, action, value=None):
        """Execute once through the session; do not replay a failed action."""
        return self.session.execute_action(action, value=value)

    def check_oracles(self, findings, sequence, attempt):
        """Run each oracle and return the number of function calls, including failures.

        The count is per oracle function, not per assertion inside it.
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

    def end_test(self):
        """Finish the whole test; end_sequence has already closed each session."""
        pass

    def report_test(self, url, num_runs, length_sequence, oracle_findings,
                    execution_failures=None, sequence_stops=None, *,
                    sequence_results=None, total_seconds=None):
        """Print the test results, including any details supplied by a wrapper."""
        print_test_summary(url, num_runs, length_sequence, oracle_findings,
                           execution_failures, sequence_stops,
                           sequence_results=sequence_results, total_seconds=total_seconds)
