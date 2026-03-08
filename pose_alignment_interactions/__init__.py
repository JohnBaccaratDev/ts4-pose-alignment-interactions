import sims4
import services
import traceback
from pose_alignment_interactions.pai_config import PaiConfig
from server.clientmanager import ClientManager
from sims4.resources import Types
from sims4.tuning.instance_manager import InstanceManager

from pose_alignment_interactions.pai_globals import PaiGlobals
from pose_alignment_interactions.inject import *
from pose_alignment_interactions.pose_players_compat import *
from pose_alignment_interactions.pai_interaction_ids import *

pai_interactions = (pai_move_id,
                    pai_rotate_id,
                    pai_align_id,
                    pai_config_interaction_affect_others_id,
                    pai_config_interaction_auto_snapping_id
                    )

pai_sim_only_interactions = (pai_snap_to_grid_id,
                             pai_snap_to_direction_id,
                             pai_align_other_sim_id,
                             pai_rotate_other_sim_id,
                             pai_move_other_sim_id,
                             pai_snap_to_grid_other_sim_id,
                             pai_snap_to_direction_other_sim_id,
                             pai_active_npc_set_other_sim_id,
                             pai_active_npc_reset_id,
                             pai_active_npc_reset_other_sim_id,
                             pai_cancel_all_posing_id,
                             pai_cancel_all_posing_other_sim_id,
                             pai_config_interaction_affect_others_other_sim_id,
                             pai_config_interaction_auto_snapping_other_sim_id
                             )

def get_sa_tuple_for_interactions(interactions):
    affordance_manager = services.affordance_manager()
    sa_list = []
    for sa_id in interactions:
        key = sims4.resources.get_resource_key(sa_id, Types.INTERACTION)
        sa_tuning = affordance_manager.get(key)
        if not sa_tuning is None:
            sa_list.append(sa_tuning)
    return tuple(sa_list)

@inject_to(InstanceManager, "load_data_into_class_instances")
def pai_inject_object_interactions(original, self, *args, **kwargs):
    original(self, *args, **kwargs)

    if self.TYPE == Types.OBJECT:
        sa_for_all_tuple = get_sa_tuple_for_interactions(pai_interactions)
        sa_for_sims_tuple = get_sa_tuple_for_interactions(pai_sim_only_interactions)

        # Interactions for all objects
        for (key, cls) in self._tuned_classes.items():
            if hasattr(cls, "_super_affordances"):
                if getattr(cls, "provides_terrain_interactions", False) and not cls.__qualname__ == "object_terrain":
                    continue

                cls._super_affordances += sa_for_all_tuple

                if cls.__qualname__ in ["object_sim", "object_Dog", "object_Cat", "object_Horse", "object_fox"]:
                    cls._super_affordances += sa_for_sims_tuple

def on_active_sim_change_callback(old_sim, new_sim):
    PaiGlobals.reset_active_npc_sim()


@inject_to(ClientManager, "create_client")
def pai_inject_create_client(original, self, *args, **kwargs):
    client = original(self, *args, **kwargs)
    client.register_active_sim_changed(on_active_sim_change_callback)
    return client


@inject_to(sims.sim.Sim, "on_remove")
def pai_inject_on_sim_remove(original, self, *args, **kwargs):
    if PaiGlobals.is_already_active_npc_sim(self, *args, **kwargs):
        PaiGlobals.reset_active_npc_sim()

    original(self)

# Wrap ww interaction blocking function so that PAI interactions can still be used while posing
if ww_installed:
    # Only needed to do it for WhickedWhims, WonderfulWhims doesn't have interaction blocking
    try:
        import wickedwhims.sex.integral.sex_handlers._ts4_interactions_blocking as _ts4_interactions_blocking

        @inject_to(_ts4_interactions_blocking, "is_wickedwhims_interaction")
        def wrapped_is_wickedwhims_interaction(original, interaction_id):
            return original(interaction_id) or interaction_id in pai_interactions or interaction_id in pai_sim_only_interactions
    except:
        pass

    from wickedwhims.sex.features.poseplayer.pose_interactions import StopPoseInteraction

    @inject_to(StopPoseInteraction, "on_interaction_start")
    def pai_inject_StopPose_Interaction(original, cls, interaction_instance, *args, **kwargs):
        ret = original(interaction_instance, *args, **kwargs)
        sim = cls.get_interaction_target(interaction_instance)
        if ret and PaiGlobals.is_already_active_npc_sim(sim):
            PaiGlobals.reset_active_npc_sim()

        return ret

PaiConfig.get_to_export()
PaiConfig.read_config()