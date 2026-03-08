import sims4.math
import traceback
from pose_alignment_interactions import PaiConfig
from pose_alignment_interactions.pai_base_interaction import PaiBaseInteraction
from pose_alignment_interactions.pai_snap_to_direction import PaiSnapToDirection
from pose_alignment_interactions.pai_snap_to_grid import PaiSnapToGrid
from pose_alignment_interactions.pose_players_compat import set_pose_player_position

class PaiMove(PaiBaseInteraction):

    def _trigger_interaction_start_event(self):
        self.spread_interaction_to_other_posed()

        sim = self.get_active_sim()

        if PaiConfig.auto_snapping_move_rotate:
            new_pos_vector = PaiSnapToGrid.position_to_snapped_vector(self.target.position, self.target.routing_surface)
            new_orientation = PaiSnapToDirection.orientation_to_snapped(sim.location.world_transform.orientation)
        else:
            new_pos_vector = self.target.position
            new_orientation = sim.transform.orientation

        new_pos = sims4.math.Location(sims4.math.Transform(new_pos_vector, new_orientation), self.target.routing_surface)

        set_pose_player_position(sim, new_pos, sim.location)