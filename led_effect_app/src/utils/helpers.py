import flet as ft
from utils.logger import AppLogger


def safe_component_update(component: ft.Control, operation_name: str = "update"):
    try:
        if (hasattr(component, '_Control__uid') and 
            component._Control__uid is not None and 
            hasattr(component, 'update')):
            component.update()
            return True
        else:
            AppLogger.info(f"Skipping {operation_name} - component not yet added to page")
            return False
    except (AttributeError, AssertionError) as e:
        AppLogger.warning(f"Safe update failed for {operation_name}: {e}")
        return False
    except Exception as e:
        AppLogger.error(f"Unexpected error in safe update for {operation_name}: {e}")
        return False


def safe_batch_component_update(components: list, operation_name: str = "batch_update"):
    """Safely update multiple Flet components"""
    updated_count = 0
    for i, component in enumerate(components):
        if safe_component_update(component, f"{operation_name}[{i}]"):
            updated_count += 1
    
    AppLogger.info(f"Safe batch update: {updated_count}/{len(components)} components updated")
    return updated_count


def safe_dropdown_update(dropdown: ft.Dropdown, options_list: list, operation_name: str = "dropdown_update"):
    """Safely update dropdown options"""
    try:
        dropdown.options = [ft.dropdown.Option(str(x)) for x in options_list]
        
        if options_list and (dropdown.value not in [str(x) for x in options_list]):
            dropdown.value = str(options_list[0])
            
        return safe_component_update(dropdown, operation_name)
    except Exception as e:
        AppLogger.error(f"Error in safe dropdown update for {operation_name}: {e}")
        return False