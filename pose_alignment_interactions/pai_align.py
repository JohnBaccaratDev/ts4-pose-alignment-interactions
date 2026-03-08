from event_testing.results import TestResult
from objects.terrain import TerrainPoint
from pose_alignment_interactions.pai_base_interaction import PaiBaseInteraction
from pose_alignment_interactions.pose_players_compat import set_pose_player_position


class PaiAlign(PaiBaseInteraction):

    @classmethod
    def _test(cls, target, context, **kwargs):

        if isinstance(target, TerrainPoint):
            return TestResult(False, "PAI Align is not allowed with clicked location.")

        return super()._test(target, context)

    def _trigger_interaction_start_event(self):
        self.spread_interaction_to_other_posed()

        sim = self.get_active_sim()
        set_pose_player_position(sim, self.target.location, sim.location)