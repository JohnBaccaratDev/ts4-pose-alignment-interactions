
import sims
from interactions import PipelineProgress
from pose_alignment_interactions.pai_globals import PaiGlobals
from sims4 import math

ww_installed = False
try:
    import wickedwhims.sex.features.poseplayer.pose_handler as ww_pose_handler
    from turbolib2.wrappers.sim.sim import TurboSim
    import turbolib2.utils.math as tmath
    ww_installed = True
except:
    pass

posePlayer_installed = False
try:
    from poseplayer import PoseInteraction as APP_PoseInteraction
    posePlayer_installed = True
except:
    pass

def is_in_pose_interaction(sim):
    return is_in_posePlayer_pose(sim) or is_in_ww_pose(sim)

def is_in_posePlayer_pose(sim):
    if not posePlayer_installed:
        return False

    for interaction in sim.get_all_running_and_queued_interactions():
        if interaction.pipeline_progress in [PipelineProgress.RUNNING, PipelineProgress.STAGED] and isinstance(interaction, APP_PoseInteraction):
            return True
    return False

def has_posePlayer_interactions_running_or_queued_up_next(sim):
    if not posePlayer_installed:
        return False

    for interaction in sim.get_all_running_and_queued_interactions():
        if isinstance(interaction, APP_PoseInteraction):
            if (interaction.queued or interaction.running) and not (interaction.has_been_canceled or interaction.has_been_killed):
                return True
        else:
            break
    return False

def is_in_ww_pose(sim):
    if not ww_installed:
        return False

    return ww_pose_handler.is_sim_in_pose_interaction(TurboSim(sim))

def reset_active_npc_callback(interaction):
    sim = interaction.sim
    if PaiGlobals.is_already_active_npc_sim(sim):
        if has_posePlayer_interactions_running_or_queued_up_next(sim) or is_in_ww_pose(sim):
            return
        PaiGlobals.reset_active_npc_sim()

def reset_position_for_andrews_pose_player(interaction):
    sim = interaction.sim
    if isinstance(sim, sims.sim.Sim):
        location_to_set = None
        queued_or_running = 0

        for queued in sim.queue:
            if not hasattr(queued, "pose_name"):
                break

            if not location_to_set and hasattr(queued, "pose_initial_position"):
                location_to_set = getattr(queued, "pose_initial_position")

            if (queued.queued or queued.running) and not (queued.has_been_canceled or queued.has_been_killed):
                queued_or_running += 1

            if location_to_set and not hasattr(queued, "pose_initial_position"):
                setattr(queued, "pose_initial_position", location_to_set)
                queued.register_on_cancelled_callback(reset_position_for_andrews_pose_player)

        if location_to_set and queued_or_running == 0:
            sim.location = location_to_set
            reset_active_npc_callback(interaction)

def set_pose_player_position(sim, should_location, old_location):

    # Instead of directly setting the location, set position through WW's offset positioning system ("Enable positioning"), so that manual adjustments with that system work
    if is_in_ww_pose(sim):
        asi = TurboSim(sim).get_temp_value("active_sex_instance")

        # WonderfulWhims calls it pose instance instead
        if asi is None:
            asi = TurboSim(sim).get_temp_value("active_pose_instance")

        if asi is not None:
            initial_pos = asi.get_location()

            should_x = should_location.world_transform.translation.x
            should_y = should_location.world_transform.translation.y
            should_z = should_location.world_transform.translation.z

            initial_x = initial_pos.world_transform.translation.x
            initial_y = initial_pos.world_transform.translation.y
            initial_z = initial_pos.world_transform.translation.z

            try: # Remove this branch after July 2026
                should_euler = tmath.convert_quaternion_to_euler(should_location.world_transform.orientation.x,
                                                              should_location.world_transform.orientation.y,
                                                              should_location.world_transform.orientation.z,
                                                              should_location.world_transform.orientation.w)
                initial_euler = tmath.convert_quaternion_to_euler(initial_pos.world_transform.orientation.x,
                                                              initial_pos.world_transform.orientation.y,
                                                              initial_pos.world_transform.orientation.z,
                                                              initial_pos.world_transform.orientation.w)
            except:
                should_quaternion = tmath.Quaternion(x=should_location.world_transform.orientation.x,
                                                     y=should_location.world_transform.orientation.y,
                                                     z=should_location.world_transform.orientation.z,
                                                     w=should_location.world_transform.orientation.w)
                initial_quaternion = tmath.Quaternion(x=initial_pos.world_transform.orientation.x,
                                                     y=initial_pos.world_transform.orientation.y,
                                                     z=initial_pos.world_transform.orientation.z,
                                                     w=initial_pos.world_transform.orientation.w)
                should_euler = tmath.Quaternion.to_euler(should_quaternion)
                initial_euler = tmath.Quaternion.to_euler(initial_quaternion)

            should_pitch = math.rad_to_deg(should_euler[0])
            should_yaw = math.rad_to_deg(should_euler[1])
            should_roll = math.rad_to_deg(should_euler[2])

            initial_pitch = math.rad_to_deg(initial_euler[0])
            initial_yaw = math.rad_to_deg(initial_euler[1])
            initial_roll = math.rad_to_deg(initial_euler[2])

            for active_node in asi._positioning_selected_nodes:
                ox, oy, oz, opitch, oyaw, oroll = asi._positioning_offsets.get(active_node, (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))

                new_x = ox + ((should_x - ox) - initial_x)
                new_y = oy + ((should_y - oy) - initial_y)
                new_z = oz + ((should_z - oz) - initial_z)

                new_pitch = opitch + ((should_pitch - opitch) - initial_pitch)
                new_yaw = oyaw + ((should_yaw - oyaw) - initial_yaw)
                new_roll = oroll + ((should_roll - oroll) - initial_roll)

                if new_pitch > 360.0:
                    new_pitch -= math.floor(new_pitch / 360.0) * 360.0
                if new_yaw > 360.0:
                    new_yaw -= math.floor(new_yaw / 360.0) * 360.0
                if new_roll > 360.0:
                    new_roll -= math.floor(new_roll / 360.0) * 360.0

                if new_pitch < -360.0:
                    new_pitch += math.floor(-new_pitch / 360.0) * 360.0
                if new_yaw < -360.0:
                    new_yaw += math.floor(-new_yaw / 360.0) * 360.0
                if new_roll < -360.0:
                    new_roll += math.floor(-new_roll / 360.0) * 360.0

                positioning_offset = (
                    new_x,
                    new_y,
                    new_z,
                    new_pitch,
                    new_yaw,
                    new_roll,
                )

                asi._positioning_offsets[active_node] = positioning_offset
                asi.update_node_positioning(active_node, positioning_offset=positioning_offset)

    elif is_in_posePlayer_pose(sim):
        # Set initial position, so that we can later reset to that position once the interaction is stopped

        for queued in sim.queue:
            if not hasattr(queued, "pose_name"):
                break

            if not hasattr(queued, "pose_initial_position"):
                setattr(queued, "pose_initial_position", old_location)
                queued.register_on_cancelled_callback(reset_position_for_andrews_pose_player)

        sim.location = should_location