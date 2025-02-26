from ..pokemon import Pokemon
from ...abilities import get_ability

def try_trigger_func(target: Pokemon, a_trigger: str, *args):
    """
    Attempts to use the given ability trigger function with the given args
    """
    if not target.has_ability():
        return None
    
    ability = get_ability(target.id)
    if ability.has_trigger(a_trigger):
        result = ability.func(a_trigger)(*args)
        return True if result is None else result
    
    return None