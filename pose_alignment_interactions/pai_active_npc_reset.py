from event_testing.results import TestResult
from pose_alignment_interactions.pai_active_npc_base import PaiActiveNpcBase
from pose_alignment_interactions.pai_globals import PaiGlobals


class PaiActiveNpcReset(PaiActiveNpcBase):

    @classmethod
    def _test(cls, target, context, **kwargs):
        if PaiGlobals.get_active_npc_sim_object() is None:
            return TestResult(False, "There is no active npc sim set currently.")

        return super()._test(target, context)

    def _trigger_interaction_start_event(cls):
        PaiGlobals.reset_active_npc_sim()