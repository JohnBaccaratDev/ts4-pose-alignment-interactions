from pose_alignment_interactions.pai_config import PaiConfig
from pose_alignment_interactions.pai_config_bool_interaction import PaiConfigBoolInteraction
from pose_alignment_interactions.pose_players_compat import *
from event_testing.results import TestResult

class PaiConfigBoolInteractionGeneral(PaiConfigBoolInteraction):

    @classmethod
    def _test(cls, target, context, **kwargs):
        # Addresses forums.ea.com/idea/the-sims-4-bug-reports-en/multiple-more-choices--options-on-non-active-sim/12195548
        # Has category -> Interactions when clicking non-active sim
        if cls.category is not None and (not getattr(target, "is_sim", False) or context.sim.sim_id == target.sim_id):
            return TestResult(False, "Interaction is only for non-active sim")
        # Has no category -> Interactions for active sim and objects
        elif cls.category is None and getattr(target, "is_sim", False) and context.sim.sim_id != target.sim_id:
            return TestResult(False, "Interaction is only for active sim or objects")

        sim = PaiGlobals.get_active_npc_sim_object()
        if sim is not None and is_in_pose_interaction(sim):
            return TestResult.TRUE

        sim = context.sim
        if sim is not None and is_in_pose_interaction(sim):
            return TestResult.TRUE

        if getattr(target, "is_sim", False):
            if is_in_pose_interaction(target):
                return TestResult.TRUE

        return TestResult(False, "Active sim is not posed")
