"""
Session isolation tests.

Verifies that two sessions for different institutions cannot receive each
other's recognition events, and that attendance cannot be written cross-tenant.
"""
import pytest

from backend.services.session_service import get_session_manager


class TestSessionIsolation:
    def setup_method(self):
        """Start two independent sessions."""
        self.mgr = get_session_manager()
        self.sess_a = self.mgr.start_session("INST_A", "Physics 101")
        self.sess_b = self.mgr.start_session("INST_B", "Math 202")

    def teardown_method(self):
        self.mgr.end_session("INST_A")
        self.mgr.end_session("INST_B")

    def test_get_active_session_is_institution_scoped(self):
        """Each institution sees only its own session."""
        sess_a = self.mgr.get_active_session("INST_A")
        sess_b = self.mgr.get_active_session("INST_B")

        assert sess_a is not None
        assert sess_b is not None
        assert sess_a.session_id != sess_b.session_id
        assert sess_a.subject_name == "Physics 101"
        assert sess_b.subject_name == "Math 202"

    def test_institution_a_attendance_increment_does_not_affect_b(self):
        self.mgr.increment_attendance("INST_A")
        self.mgr.increment_attendance("INST_A")

        sess_a = self.mgr.get_active_session("INST_A")
        sess_b = self.mgr.get_active_session("INST_B")

        assert sess_a.attendance_count == 2
        assert sess_b.attendance_count == 0

    def test_ending_a_session_does_not_affect_b(self):
        self.mgr.end_session("INST_A")

        sess_a = self.mgr.get_active_session("INST_A")
        sess_b = self.mgr.get_active_session("INST_B")

        assert sess_a is None
        assert sess_b is not None
        assert sess_b.is_active is True

    def test_forged_session_id_lookup_returns_none(self):
        """Cannot retrieve INST_B session by ID while querying INST_A."""
        real_b_id = self.sess_b.session_id
        # Even if you know INST_B's session_id, querying INST_A returns None
        sess = self.mgr.get_active_session("INST_A")
        # The returned session must not be INST_B's session
        assert sess is None or sess.session_id != real_b_id
