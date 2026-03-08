import math as pmath

import terrain
import services
import sims4.math as smath
from pose_alignment_interactions.pai_config import PaiConfig
from sims4.testing.unit import TestResult

from pose_alignment_interactions.pai_base_interaction import PaiBaseInteraction
from pose_alignment_interactions.pose_players_compat import set_pose_player_position


class PaiSnapToGrid(PaiBaseInteraction):

    @classmethod
    def moves_sim(cls):
        return cls.sim_to_move.TARGET


    @classmethod
    def _test(cls, target, context, **kwargs):

        if services.active_lot() is None:
            return TestResult(False, "Active Lot required.")

        return super()._test(target, context)

    @classmethod
    def position_to_snapped_vector(cls, position, routing_surface):
        lot = services.active_lot()

        start_corner = lot.corners[0]
        cx = start_corner.x
        cz = start_corner.z

        sx = position.x
        sz = position.z

        # subtract so we are at an origin
        sx -= cx
        sz -= cz

        tempx = sx
        tempz = sz

        r = lot.rotation

        # rotate around origin
        sx = (tempx * pmath.cos(r)) - (tempz * pmath.sin(r))
        sz = (tempx * pmath.sin(r)) + (tempz * pmath.cos(r))

        # snap to every 0.5th point on the grid
        sx = round(sx * 2) / 2
        sz = round(sz * 2) / 2

        # rest is reversal of the whole operation chain
        tempx = sx
        tempz = sz

        sx = (tempx * pmath.cos(-r)) - (tempz * pmath.sin(-r))
        sz = (tempx * pmath.sin(-r)) + (tempz * pmath.cos(-r))

        sx += cx
        sz += cz

        # recalculate height, if we were already close to the ground
        if smath.almost_equal(terrain.get_terrain_height(position.x, position.z, routing_surface), position.y, epsilon=0.1):
            sy = terrain.get_terrain_height(sx, sz, routing_surface)
        else:
            sy = position.y

        return smath.Vector3(sx, sy, sz)

    def _trigger_interaction_start_event(self):
        self.spread_interaction_to_other_posed()

        if PaiConfig.affect_all_posed:
            sim = self.sim
        else:
            sim = self.target

        new_pos = smath.Location(smath.Transform(self.position_to_snapped_vector(sim.position, sim.routing_surface), sim.orientation), sim.routing_surface)

        set_pose_player_position(sim, new_pos, sim.location)