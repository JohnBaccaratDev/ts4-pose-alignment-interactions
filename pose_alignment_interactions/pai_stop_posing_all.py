import services
from pose_alignment_interactions.pai_base_interaction import PaiBaseInteraction
from pose_alignment_interactions.pose_players_compat import *

if posePlayer_installed:
    import poseplayer

if ww_installed:
    import wickedwhims.sex.features.poseplayer.pose_handler as ww_pose_handler
    from turbolib2.wrappers.sim.sim import TurboSim

class PaiStopPosingAll(PaiBaseInteraction):

    @classmethod
    def moves_sim(cls):
        return cls.sim_to_move.TARGET

    def _trigger_interaction_start_event(cls):
        for obj in services.current_zone().object_manager._objects.values():
            if obj.is_sim:
                if is_in_ww_pose(obj):
                    asi = TurboSim(obj).get_temp_value("active_sex_instance")

                    # WonderfulWhims calls it pose instance instead
                    if asi is None:
                        asi = TurboSim(obj).get_temp_value("active_pose_instance")
                    if asi.is_playing:
                        asi.cancel()

                elif is_in_posePlayer_pose(obj):

                    atleast_one = False
                    for interaction in obj.get_all_running_and_queued_interactions():
                        if isinstance(interaction, poseplayer.PoseInteraction):
                            interaction.cancel_user("Stopping all posing.")
                            atleast_one = True

                        else:
                            if atleast_one and interaction.visible:
                                break

