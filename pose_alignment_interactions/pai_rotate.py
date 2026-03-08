import traceback

import sims4.math
from pose_alignment_interactions.pai_config import PaiConfig
from pose_alignment_interactions.pai_base_interaction import PaiBaseInteraction
from pose_alignment_interactions.pai_snap_to_direction import PaiSnapToDirection
from pose_alignment_interactions.pose_players_compat import set_pose_player_position

class PaiRotate(PaiBaseInteraction):

    @classmethod
    def allowed_for_affect_other_posed(cls, sim_to_push_affordance_to, active_sim, target):
        if hasattr(target, "sim_id") and target.sim_id == sim_to_push_affordance_to.sim_id:
            return False
        return True

    def _trigger_interaction_start_event(self):
        self.spread_interaction_to_other_posed()

        sim = self.get_active_sim()

        # Do nothing in the case that the active sim is also the target and we are in Affect All Mode
        if PaiConfig.affect_all_posed and sim == self.target:
            return

        new_orientation = sims4.math.angle_to_yaw_quaternion(sims4.math.vector3_angle(self.target.position - sim.transform.translation))
        if PaiConfig.auto_snapping_move_rotate:
            new_orientation = PaiSnapToDirection.orientation_to_snapped(new_orientation)

        new_pos = sims4.math.Location(sims4.math.Transform(sim.transform.translation, new_orientation), sim.routing_surface)

        set_pose_player_position(sim, new_pos, sim.location)
