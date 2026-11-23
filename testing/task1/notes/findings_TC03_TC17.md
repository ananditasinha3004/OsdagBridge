# Task 1 findings: TC-03 through TC-17

Observed at commit `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`. These are local findings, not published GitHub issues. Duplicate checking and issue URLs remain open.

## F01 - Additional inputs reset during saving

Reproduced in TC-09, TC-11, TC-12 and TC-13. Each edit was accepted and present in input_before_save.json. input.osi, input_after_save.json and output_dictionary.json contain defaults. The UI reported successful saving without warning about these replacements.

Source: desktop/ui/template_page.py:793 saveOSI_inputs calls solve_extend_basic_input_dict unconditionally. core/bridge_types/plate_girder/defaults.py:870 calls the tab-default functions; their _update helpers overwrite present values (e.g. lines 181-185, 263, 340, 362). A second isolated call using already-initialized inputs reproduced all four resets; see results/default_reset_reproduction.json.

Suggested fix: initialize only missing user-controlled values. Separate derived geometry recomputation from default assignment. Add save/reload and design regression checks for these four fields. Do not silently overwrite accepted values.

## F02 - Steel export repeats girder properties for other components

TC-14 exports custom girder fy/fu 360/510 MPa for bracing and diaphragm that retain 350/490. TC-15 exports 350/490 for custom bracing 300/450 and diaphragm 320/470. Grade names are component-specific but numeric values are not.

Source: desktop/ui/dialogs/generate_results_values_builder.py:155 resolve_material_properties_steel obtains one steel_prop from bridge._build_material_props(). Its _row function reuses those numeric properties for all three rows.

Suggested fix: resolve each row from the corresponding material prefix and grade, with explicit unit conversion. Test three different material definitions in one export. The finding proves an export mismatch; its effect on all internal design calculations remains unverified.

## F03 - Concrete export ignores custom density and mixes modulus units

TC-17 input and output dictionaries retain density 24 kN/m3 and Ecm 35 GPa. Material Properties - Concrete exports density 25 and Ecm 35 labeled MPa. It computes 200000/35 = 5714.29 as the modular ratio; consistent MPa units give 200000/35000 = 5.71429.

Source: desktop/ui/dialogs/generate_results_values_builder.py:204 resolve_material_properties_concrete reads cp.Ecm without GPa-to-MPa conversion and uses it as the denominator of steel_e_mpa/ecm. It hardcodes density = 25.0.

Suggested fix: convert both moduli to the same unit for the ratio and display, and export density from the selected deck material. Add a custom-density and modulus-unit regression test. This is an export finding, not an independently verified solver error.

