import unittest

from code.src.crash_hunter.android import attributed_incidents


class AndroidEvidenceTests(unittest.TestCase):
    def test_unrelated_crash_is_not_target_bug(self):
        log = "10-15 12:00:00.000 101 102 E AndroidRuntime: FATAL EXCEPTION: main\n10-15 12:00:00.001 101 102 E AndroidRuntime: Process: unrelated.app, PID: 101\n10-15 12:00:00.002 101 102 E AndroidRuntime: java.lang.IllegalStateException: failure"
        self.assertEqual(attributed_incidents(log, "", "target.app"), [])

    def test_target_child_process_crash_is_captured(self):
        log = "10-15 12:00:00.000 101 102 E AndroidRuntime: FATAL EXCEPTION: main\n10-15 12:00:00.001 101 102 E AndroidRuntime: Process: target.app:worker, PID: 101\n10-15 12:00:00.002 101 102 E AndroidRuntime: java.lang.IllegalStateException: failure"
        bugs = attributed_incidents(log, "// CRASH: target.app:worker (pid 101)", "target.app")
        self.assertEqual(len(bugs), 1)
        self.assertEqual(bugs[0]["kind"], "JAVA_CRASH")

    def test_anr_boundary_and_tool_error(self):
        self.assertEqual(attributed_incidents("", "// NOT RESPONDING: target.application\n", "target.app"), [])
        self.assertEqual(attributed_incidents("", "adb.exe: device offline", "target.app"), [])
        self.assertEqual(attributed_incidents("", "// NOT RESPONDING: target.app (pid 9)\n", "target.app")[0]["kind"], "ANR")

    def test_native_target_crash(self):
        log = "10-15 12:00:00.000 101 102 F DEBUG   : *** *** ***\n10-15 12:00:00.001 101 102 F DEBUG   : Cmdline: target.app\n10-15 12:00:00.002 101 102 F DEBUG   : signal 11 (SIGSEGV)"
        self.assertEqual(attributed_incidents(log, "", "target.app")[0]["kind"], "NATIVE_CRASH")


if __name__ == "__main__":
    unittest.main()
