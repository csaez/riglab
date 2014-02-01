TEMPLATE SPECS
==============

`riglab` templates are JSON files with the following structure:

    {
        "filetype": "riglab_template",
         "version": "1.0",
         "mapping": {
                        "solvers": {ref_solver_id: class_name, ...},
                        "skeleton": {ref_joint: new_joint, ...},
                        "states": {state_name: {ref_solver_id: state_value, ...},
                                   ...},
                        "active_state": state_name,
                    },
         "data": {
                    ref_solver_id: {"skeleton": (ref_joint, ...),
                                    "icons": (curve_data*, ...)
                                    "dependencies": ({"internal": {ref_solver_id: index, ...},
                                                      "external": (obj_name**, ...),
                                                      "active": ref***}, ...),
                    ...,
                },
    }

(*)
`curve_data` is a 1-dimensional array (per manipulator) containing the curve
geometry in a Softimage friendly format
([softimage docs](http://download.autodesk.com/global/docs/softimage2012/en_us/sdkguide/si_om/NurbsCurveList.Get2.html)).

(**)
`obj_name` is the fullname of the object used as ref for the space switching.

(***)
`ref` is the name of the active space.
