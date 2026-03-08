import services
import sims4.math as smath
from pose_alignment_interactions.pai_config import PaiConfig
from sims4.testing.unit import TestResult
from pose_alignment_interactions.pai_base_interaction import PaiBaseInteraction
from pose_alignment_interactions.pose_players_compat import set_pose_player_position


class PaiSnapToDirection(PaiBaseInteraction):

    @classmethod
    def moves_sim(cls):
        return cls.sim_to_move.TARGET


    @classmethod
    def _test(cls, target, context, **kwargs):

        if services.active_lot() is None:
            return TestResult(False, "Active Lot required.")

        return super()._test(target, context)


    @classmethod
    def get_target_for_affect_other_posed(cls, sim_to_push_affordance_to, active_sim, target):
        return sim_to_push_affordance_to

    @classmethod
    def orientation_to_snapped(cls, orientation):
        lot = services.active_lot()

        angle = smath.yaw_quaternion_to_angle(orientation)
        # subtract, so we get the actual rotation
        angle -= lot.rotation
        # mod, so we just work with positive radians
        angle = angle % smath.deg_to_rad(360)
        # normalize
        angle /= smath.deg_to_rad(360)
        # snap to exactly 8 points
        angle *= 8
        angle = round(angle)
        # reversal of the whole operation chain
        angle /= 8
        angle *= smath.deg_to_rad(360)
        angle += lot.rotation
        return smath.angle_to_yaw_quaternion(angle)

    def _trigger_interaction_start_event(self):
        self.spread_interaction_to_other_posed()

        if PaiConfig.affect_all_posed:
            sim = self.context.sim
        else:
            sim = self.target

        new_orientation = self.orientation_to_snapped(sim.location.world_transform.orientation)

        new_pos = smath.Location(smath.Transform(sim.location.transform.translation, new_orientation), sim.routing_surface)

        set_pose_player_position(sim, new_pos, sim.location)