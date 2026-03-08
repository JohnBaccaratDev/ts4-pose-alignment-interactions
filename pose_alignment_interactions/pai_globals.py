
class PaiGlobals:

    _active_npc_sim = None

    @classmethod
    def set_active_npc_sim(cls, sim):
        if hasattr(sim, "sim_id"):
            cls._active_npc_sim = sim
        else:
            raise Exception("Tried to set active sim, but got \"{0}\" of type \"{1}\"".format(str(sim), type(sim)))

    @classmethod
    def is_already_active_npc_sim(cls, sim):
        if cls._active_npc_sim is not None:
            if hasattr(sim, "sim_id"):
                return cls._active_npc_sim.sim_id == sim.sim_id
            if isinstance(sim, int):
                return cls._active_npc_sim.sim_id == sim
            raise Exception("Given object of type \"{0}\" does not attribute \"sim_id\"".format(type(sim)))
        return False

    @classmethod
    def get_active_npc_sim_object(cls):
        return cls._active_npc_sim

    @classmethod
    def reset_active_npc_sim(cls):
        cls._active_npc_sim = None