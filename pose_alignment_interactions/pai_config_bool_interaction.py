import services
import sims4
from event_testing.results import TestResult
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from interactions.utils.tunable_icon import TunableIconVariant
from sims4.tuning.tunable import Tunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from singletons import DEFAULT
from pose_alignment_interactions.pai_config import PaiConfig


class PaiConfigBoolInteraction(ImmediateSuperInteraction):
    INSTANCE_TUNABLES = {
        'config_property_name': Tunable(description="Name of property in PaiConfig", tunable_type=str, default="", needs_tuning=True),
        'pie_menu_icon_enabled':TunableIconVariant(description='Icon when enabled', tuning_group=GroupNames.UI),
        'pie_menu_icon_disabled':TunableIconVariant(description='Icon when disabled', tuning_group=GroupNames.UI)
    }

    @classmethod
    def _test(cls, target, context, **kwargs):
        if not hasattr(PaiConfig, cls.config_property_name):
            raise Exception("Property " + cls.config_property_name + " does not exist in PaiConfig.")

        return TestResult.TRUE


    @flexmethod
    def get_pie_menu_icon_info(cls, inst, target=DEFAULT, context=DEFAULT, **interaction_parameters):
        inst_or_cls = inst if inst is not None else cls
        resolver = inst_or_cls.get_resolver(target=target, context=context)
        if getattr(PaiConfig, inst_or_cls.config_property_name):
            icon_info_data = inst_or_cls.pie_menu_icon_enabled(resolver)
        else:
            icon_info_data = inst_or_cls.pie_menu_icon_disabled(resolver)
        return icon_info_data

    @classmethod
    def get_pai_config_property_value(cls):
        if not hasattr(PaiConfig, cls.config_property_name):
            raise Exception("Property " + cls.config_property_name + " does not exist in PaiConfig.")

        return getattr(PaiConfig, cls.config_property_name)


    @flexmethod
    def get_pie_menu_color(cls, inst, target=DEFAULT, context=DEFAULT):
        mood_manager = services.get_instance_manager(sims4.resources.Types.MOOD)
        if cls.get_pai_config_property_value():
            return (mood_manager.get(14636), 1) # Energized, light green. Happy wasn't used because of Meaningful Stories
        else:
            return (mood_manager.get(14632), 1) # Angry, red

    def _trigger_interaction_start_event(self):
        setattr(PaiConfig, self.config_property_name, not getattr(PaiConfig, self.config_property_name))
        PaiConfig.write_config()