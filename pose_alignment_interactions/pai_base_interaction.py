import services
import sims.sim
import sims4
import traceback
from event_testing.results import TestResult
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from interactions.context import InteractionSource, InteractionContext
from interactions.go_here_test import go_here_test
from interactions.priority import Priority
from interactions.utils.tunable_icon import TunableIconVariant
from objects.terrain import TerrainPoint
from pose_alignment_interactions.pai_config import PaiConfig
from singletons import DEFAULT

from pose_alignment_interactions.pose_players_compat import *
from sims4.tuning.tunable import Tunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod

import pose_alignment_interactions.pai_interaction_ids as pai_interaction_ids


class PaiBaseInteraction(ImmediateSuperInteraction):
    INSTANCE_TUNABLES = {
        'config_property_name': Tunable(description="Name of property in PaiConfig", tunable_type=str, default=""),
        'pie_menu_icon_enabled':TunableIconVariant(description='Icon when enabled', tuning_group=GroupNames.UI),
        'pie_menu_icon_disabled':TunableIconVariant(description='Icon when disabled', tuning_group=GroupNames.UI)
    }

    class sim_to_move:
        NONE = 0
        TARGET = 1
        CONTEXT = 2


    @classmethod
    def moves_sim(cls):
        return cls.sim_to_move.CONTEXT


    @classmethod
    def allowed_for_affect_other_posed(cls, sim_to_push_affordance_to, active_sim, target):
        return True


    @classmethod
    def get_target_for_affect_other_posed(cls, sim_to_push_affordance_to, active_sim, target):
        return target


    @classmethod
    def affects_other_posed(cls):
        return cls.config_property_name is not None and cls.config_property_name != ""


    def spread_interaction_to_other_posed(self):
        if not self.affects_other_posed() or not getattr(PaiConfig, self.config_property_name):
            return

        if self.context.source == InteractionSource.SCRIPT:
            return

        active_sim = self.get_active_sim()
        target = self.target
        obj_manager = services.current_zone().object_manager
        for obj in obj_manager._objects.values():
            if hasattr(obj, "is_sim") and obj.is_sim:

                if hasattr(active_sim, "sim_id") and active_sim.sim_id == obj.sim_id:
                    continue

                if not self.allowed_for_affect_other_posed(obj, active_sim, target):
                    continue

                if not is_in_pose_interaction(obj):
                    continue

                context = InteractionContext(obj, InteractionSource.SCRIPT, Priority.Low)
                obj.push_super_affordance(self.affordance, self.get_target_for_affect_other_posed(obj, active_sim, target), context)


    @flexmethod
    def get_pie_menu_icon_info(cls, inst, *args, **kwargs):
        inst_or_cls = inst if inst is not None else cls

        if inst_or_cls.affects_other_posed():
            target = kwargs.get("target", DEFAULT)
            context = kwargs.get("context", DEFAULT)
            resolver = inst_or_cls.get_resolver(target=target, context=context)
            if getattr(PaiConfig, inst_or_cls.config_property_name):
                icon_info_data = inst_or_cls.pie_menu_icon_enabled(resolver)
            else:
                icon_info_data = inst_or_cls.pie_menu_icon_disabled(resolver)
            return icon_info_data

        return super().get_pie_menu_icon_info(inst, *args, **kwargs)


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

            if cls.moves_sim() == cls.sim_to_move.TARGET:
                sim = target
                if not isinstance(target, sims.sim.Sim):
                    return TestResult(False, "Target must be a sim for this interaction.")
            else:
                sim = PaiGlobals.get_active_npc_sim_object()
                if sim is None:
                    sim = context.sim
        else:
            # Same as above, though in this case just exclude the ones with no category
            if cls.category is None and getattr(target, "is_sim", False):
                return TestResult(False, "Interaction is only for active sim or objects")

            sim = None
            if getattr(target, "is_sim", False) and is_in_pose_interaction(target):
                sim = target

            if sim is None:
                sim = PaiGlobals.get_active_npc_sim_object()

            if sim is None:
                sim = context.sim

        if sim is None:
            return TestResult(False, "Sim required for pose alignment.")

        if not PaiConfig.affect_all_posed and cls.moves_sim() == cls.sim_to_move.CONTEXT and getattr(target, "is_sim", False) and sim.sim_id == target.sim_id:
                return TestResult(False, "Sim is already in alignment with self.")

        if isinstance(target, TerrainPoint):
            test = go_here_test(target, context, **kwargs)
            # Ignore routing
            if(not test.result and test.reason != "Cannot GoHere! Unroutable area." ):
                return test

        if posePlayer_installed and is_in_posePlayer_pose(sim):
            return TestResult.TRUE

        if ww_installed and is_in_ww_pose(sim):
            return TestResult.TRUE

        return TestResult(False, "Sim is in neither WW or PosePlayer pose interaction.")

    def get_active_sim(cls):
        if PaiGlobals.get_active_npc_sim_object() is not None and not PaiConfig.affect_all_posed:
            return PaiGlobals.get_active_npc_sim_object()
        else:
            return cls.sim