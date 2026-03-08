
from event_testing.results import TestResult
from pose_alignment_interactions.pai_active_npc_base import PaiActiveNpcBase
from pose_alignment_interactions.pai_globals import PaiGlobals
from pose_alignment_interactions.pose_players_compat import reset_active_npc_callback

class PaiActiveNpcSet(PaiActiveNpcBase):

    @classmethod
    def _test(cls, target, context, **kwargs):

        if PaiGlobals.is_already_active_npc_sim(target):
            return TestResult(False, "Sim is already active NPC sim.")

        if target.is_pet and not target.is_npc and context.client.selectable_sims.can_select_pets:
            return TestResult(False, "You are already allowed to select your pet.")

        return super()._test(target, context)

    def _trigger_interaction_start_event(cls):
        PaiGlobals.set_active_npc_sim(cls.target)
        for queued in cls.target.queue:
            queued.register_on_cancelled_callback(reset_active_npc_callback)