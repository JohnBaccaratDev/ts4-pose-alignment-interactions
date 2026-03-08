from event_testing.results import TestResult
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from pose_alignment_interactions.pose_players_compat import is_in_pose_interaction
from pose_alignment_interactions.pai_config import PaiConfig


class PaiActiveNpcBase(ImmediateSuperInteraction):

    @classmethod
    def _test(cls, target, context, **kwargs):
        if not PaiConfig.affect_all_posed:
            # Addresses forums.ea.com/idea/the-sims-4-bug-reports-en/multiple-more-choices--options-on-non-active-sim/12195548
            # Has category -> Interactions when clicking non-active sim
            if cls.category is not None and (not getattr(target, "is_sim", False) or context.sim.sim_id == target.sim_id):
                return TestResult(False, "Interaction is only for non-active sim")
            # Has no category -> Interactions for active sim and objects
            elif cls.category is None and getattr(target, "is_sim", False) and context.sim.sim_id != target.sim_id:
                return TestResult(False, "Interaction is only for active sim or objects")
        else:
            if cls.category is None:
                return TestResult(False, "Interaction is only for active sim or objects")

        if not is_in_pose_interaction(target):
            return TestResult(False, "Target sim is not in pose interaction.")

        return super()._test(target, context)