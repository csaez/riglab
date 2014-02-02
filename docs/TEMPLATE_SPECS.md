TEMPLATE SPECS
==============

`riglab` templates are JSON files with the following structure:

    {
        "filetype": "riglab:group_template",
         "version": "1.0",
         "mapping": {
                        "solvers": {ref_solver_id: {"name": solver_name, "class": class_name}, ...},
                        "skeleton": {ref_joint: new_joint, ...},
                        "states": {state_name: {ref_solver_id: state_value, ...},
                                   ...},
                        "active_state": state_name,
                    },
         "data": {
                    ref_solver_id: {"skeleton": (ref_joint, ...),
                                    "icons": (curve_data*, ...)
                                    "dependencies": ({"internal": {ref_solver_id: {"index": anim_index,
                                                                                   "name": space_name,
                                                                                   "type": space_type},
                                                                    ...},
                                                      "external": ({"obj": anim_index,
                                                                    "name": space_name,
                                                                    "type": space_type},
                                                                   ...),
                                                      "active": space_name}, ...),
                    ...,
                },
    }

(*) `curve_data` is a 1-dimensional array (per manipulator) containing the curve
geometry in a Softimage friendly format
([docs](http://download.autodesk.com/global/docs/softimage2012/en_us/sdkguide/si_om/NurbsCurveList.Get2.html)).
