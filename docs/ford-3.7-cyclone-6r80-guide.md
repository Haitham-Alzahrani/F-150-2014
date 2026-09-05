Ford 3.7L Cyclone V6 / 6R80 — Complete Verified Reference, Diagnostic & Calibration Guide

Applicability: 2011–2014 Mustang & F-150 (with notes for 2015+ Speed Density variants).
Purpose: Diagnostic reference, HP Tuners navigation, and tuning methodology.

---

Evidence Classification System

This guide uses four evidence levels to clearly distinguish the authority of each statement:

Level Label Definition
1 Ford-Verified Confirmed by Ford owner's manuals, service documentation, or technical publications.
2 Technical Reference Supported by reputable engineering, service, or aftermarket technical data, but not necessarily an OEM specification.
3 Calibration Heuristic / Observed Range Useful working range for diagnosis/tuning based on common datalog observations.
4 OSID-Specific Must be read from the actual vehicle calibration; values vary by OSID.

---

1. Specifications & Reference Data

1A. Engine Ratings (Level 1)

Vehicle Published Rating Evidence Level
2011–2014 Mustang 3.7L 305 hp @ 6,500 RPM / 280 lb-ft @ 4,250 RPM Level 1 — Ford Mustang Owner's Manuals
2011–2014 F-150 3.7L 302 hp @ 6,500 RPM / 278 lb-ft @ 4,000 RPM Level 1 — Ford F-150 Owner's Manuals

Note: These are common published ratings for the 2011–2014 applications. Verify the exact model-year owner's manual/specification sheet for the vehicle being calibrated, as ratings can vary by model year and application.

---

1B. Cylinder Layout & Firing Order (Level 1 / Level 2)

Firing Order (Level 1 — Ford-Verified):

· Firing Order: 1-4-2-5-3-6

Cylinder Layout Diagram (Level 2 — Technical Reference):

```
       [ FRONT ]
    Bank 2 (Driver)   Bank 1 (Passenger)
    [ Cyl 4 ]         [ Cyl 1 ]
    [ Cyl 5 ]         [ Cyl 2 ]
    [ Cyl 6 ]         [ Cyl 3 ]
       [ REAR ]
```

Important Note: The firing order 1-4-2-5-3-6 is directly verified by Ford documentation. The physical bank/cylinder numbering convention (Bank 1 = Passenger, Bank 2 = Driver with cylinders 1-2-3 and 4-5-6) is a technical reference and should be verified against the applicable Ford service-manual cylinder-identification diagram for the specific vehicle.

---

1C. Spark Plug Specifications (Level 1 / Level 2)

Vehicle Motorcraft Service Part Engineering Plug ID Verified Gap Evidence Level
2014 F-150 3.7L SP-520 CYFS-12F-5 0.049–0.053 in (1.25–1.35 mm) Level 1 — 2014 F-150 Owner's Manual
2011–2014 Mustang 3.7L SP-520 CYFS-12F-5* 0.049–0.053 in (1.25–1.35 mm) Level 1 — Mustang Owner's Manuals
2011 F-150 3.7L (Discrepancy) SP-520 — Verify specific owner's manual Level 1 — Some 2011 manuals list 0.052–0.056 in

Critical Notes:

· The 2011 F-150 owner's manual lists the 3.7L V6 spark plug gap as 0.052–0.056 in in some publications, while the 2012 service manual and 2014 owner's manual list 0.049–0.053 in. This may reflect a running change. Always verify against your specific vehicle's owner's manual.
· SP-526 / SP-526-X (CYFS-12-FP) is for the 6.2L V8, not the 3.7L.
· SP-548 / CYFS-12F-1X is for the 5.0L/5.2L V8 applications, not the 3.7L.
· Engineering ID CYFS-12F-5 is confirmed by Ford parts documentation for the 2014 F-150 3.7L application. For Mustang applications, verify exact engineering ID for your specific model year and application.

Installation Specifications (Level 1 / Level 2):

Parameter Value Evidence Level
Thread Torque 11 lb-ft (15 Nm) Level 1/2 — Ford Service Procedure (verify exact 3.7L application)
Coil-on-Plug Bolt Torque 53 lb-in (6 Nm) Level 1/2 — Ford Service Procedure (verify exact 3.7L application)
Anti-Seize Do not apply unless Ford procedure specifies it Level 2 — Motorcraft installation guidance

**OBD-II Mode $06 Misfire Monitoring (Level 4):**
Mode $06 provides manufacturer-specific monitor/test information. Ford's test identifiers and cylinder mapping are OSID-dependent. TID/CID assignments must be decoded using the applicable PCM/service documentation or scan-tool definition. Do not assume TID $53 or CID $01–$06 applies universally.

---

1D. 6R80 Transmission Specifications

Gear Ratios (Level 1 — Ford Service Reference):

Mustang 6R80 (2011 Mustang Workshop Manual):

Gear Ratio
1st 4.17:1
2nd 2.34:1
3rd 1.52:1
4th 1.14:1
5th 0.87:1
6th 0.69:1

F-150 6R80 (2014 F-150 Workshop Reference):

Gear Ratio
1st 4.17:1
2nd 2.34:1
3rd 1.52:1
4th 1.14:1
5th 0.87:1
6th 0.69:1

Important Note: Some secondary references list 1.57:1 for 3rd gear. Do not substitute that value without confirming the exact transmission/application. The 1.52:1 ratio is supported by Ford workshop documentation for both Mustang and F-150 3.7L 6R80 applications.

Fluid Specifications (Level 1):

Parameter Specification Evidence Level
Fluid Type Motorcraft MERCON LV / WSS-M2C938-A Level 1 — Ford Owner's Manuals
6R80 Dry-Fill Capacity (Current Ford Documentation) Approximately 12.12 qt (11.47 L) Level 1 — Current Ford 6R80 Documentation
6R80 Dry-Fill Capacity (2011–2013 F-150 3.7L) 12.1 qt (11.7 L) Level 1 — 2011–2013 F-150 Owner's Manuals

Important Notes on Capacity:

· Current Ford 6R80 documentation specifies 12.12 qt (11.47 L) approximate dry-fill capacity.
· Historical 2011–2013 F-150 owner's manuals list 12.1 qt (11.7 L) for the 3.7L application.
· Because Ford documentation differs by publication/year, verify the vehicle-specific service information for the exact configuration.
· Pan/filter service refill quantity varies with service procedure and cooling system configuration. Always set final fluid level using the Ford transmission-level checking procedure (vehicle level, engine running, fluid at operating temperature).

Torque Converter Stall Speed (Level 1/2 — Ford Service Reference):

Application Specification Evidence Level
2011–2014 F-150 3.7L 2300–2580 RPM Level 1/2 — Ford Service Reference (verify exact application)

Note: This is a Ford service-test reference and is application-dependent. Verify transmission calibration/configuration and exact service-manual application before using this as a diagnostic pass/fail range. Actual stall speed results vary with temperature, load, and test methodology. Do not generalize F-150 specifications to Mustang applications.

Brake Stall Test Procedure (Level 2 / Level 3):

· Perform in Drive on level ground with wheels chocked.
· Hold brake firmly, slowly apply throttle – record max RPM before wheels spin.
· Duration ≤4–5 seconds (Level 3 — typical practical guideline).
· Monitor Transmission Fluid Temperature (TFT).
· Follow the applicable Ford service procedure for maximum test duration and temperature limits.
· Do not repeat without allowing transmission to cool.

---

1E. Ti-VCT System (Level 2 / Level 4)

The 3.7L uses independent variable camshaft timing on the intake and exhaust camshafts. Ford documentation confirms the 3.7L's twin independent variable camshaft timing (Ti-VCT) architecture.

Ti-VCT Control Capability (Level 2 — Technical Reference):

Parameter Control Capability Evidence Level
Intake Cam Up to 60 degrees Level 2 — Ford 3.7L Technical Description
Exhaust Cam Up to 50 degrees Level 2 — Ford 3.7L Technical Description

Note: These values represent the system's stated control capability. Actual commanded cam positions are calibration/OSID-dependent (Level 4) and vary by operating condition, load, RPM, and OSID. Maximum commanded cam-angle values must be taken from the specific OSID.

HP Tuners Paths (Level 4):

· VCT Base Timing (part throttle): Engine → VCT → Base Timing
· VCT WOT Timing: Engine → VCT → WOT Timing (if exposed by OSID)

---

2. Diagnostic Observations & Heuristics

These are calibration heuristics and observed ranges, not factory specifications. Always compare to your own logs and verify against your specific OSID.

2A. Idle RPM Stability — Classification Table (Level 3)

Practical Idle Stability Classification — Diagnostic Heuristic

Classification P/N RPM P-P Drive RPM P-P Spark P-P Recovery Time Interpretation
Perfect / Exceptional ≤10 RPM ≤15 RPM 1°–3° Immediate Rare; near-perfect airflow/torque model. No action needed.
Excellent >10–<15 RPM >15–<20 RPM 2°–4° <1 sec Very stable. No action needed.
Good / Healthy ≥15–<30 RPM ≥20–<40 RPM 3°–6° <1–2 sec Typical healthy operation.
Acceptable ≥30–<40 RPM ≥40–<50 RPM 5°–8° <2 sec OK if recovery is consistent. If not, investigate.
Marginal ≥40–≤50 RPM ≥50–≤60 RPM 8°–10° 2–3 sec Investigate vacuum leak, throttle sludge, or idle airflow.
Poor / Severe Oscillation >50 RPM >60 RPM 10°+ rhythmic >3 sec Investigate before tuning.

Important Distinction: Excursion vs. Oscillation

Peak-to-peak magnitude alone does not define hunting.

A transient excursion (e.g., 650 → 700 → 650 RPM after A/C engagement) may be perfectly acceptable if it settles quickly.

Hunting is defined by repeated or rhythmic oscillation, not merely by the magnitude of a single RPM excursion. Oscillation frequency, persistence, damping behavior, and recovery time should be evaluated together with RPM P-P.

· Damped: 650 → 675 → 635 → 660 → 645 → 652 → 649 — Generally acceptable if recovery is rapid.
· Constant-amplitude: 650 → 675 → 625 → 675 → 625... — Control-loop instability / hunting.
· Increasing-amplitude: 650 → 680 → 620 → 690 → 610... — Strong indication of an unstable control response; stop tuning and diagnose.

RPM Error (Level 3 — Diagnostic Heuristic):

RPM Error = Actual RPM − Desired/Commanded RPM

Important: First verify that the Desired/Commanded RPM is appropriate for the current ECT, load, and transmission state. Otherwise, you could tune actual RPM toward an incorrect assumption about the commanded target.

RPM Error Interpretation
±0–5 RPM Excellent control
±5–10 RPM Very good
±10–20 RPM Acceptable
±20 RPM persistent Investigate
±30 RPM persistent Strong investigation required

Rules of Thumb:

· If RPM oscillates but spark is calm (≤5° P-P swing) and airflow/throttle remain stable, investigate mechanical causes first:
  · Vacuum leak
  · Ignition variation
  · Injector imbalance
  · Accessory load
  · Compressor engagement
  · Mechanical imbalance
· If spark swings significantly (>8° P-P) while RPM oscillates, the idle controller is actively compensating for a torque/airflow disturbance. Investigate modeled airflow, mechanical airflow, throttle control, load changes, and control-loop behavior before changing PID gains.

---

2B. Warm Idle RPM (Level 3 / Level 4)

· Principle: Warm idle target is calibration-dependent. Compare actual RPM against commanded/desired idle speed in the stock calibration.
· General Observation: Idle speeds typically range from ~550–750 RPM depending on platform and OSID.
· Cold Start: Varies considerably with ECT, ambient temperature, electrical load, and calibration.

HP Tuners Path (Level 4): Engine → Idle → Speed → Base Idle RPM vs. ECT

---

2C. Fuel Trims (Level 3)

Practical Diagnostic Thresholds — Not Ford Pass/Fail Specifications

Parameter Typical Healthy Range Notes
STFT Near 0% Short-term corrections
LTFT Near 0% Long-term learned corrections
Combined (STFT + LTFT) Near 0% Diagnostic target

Diagnostic Notes:

· Values consistently deviating from 0% should prompt further investigation, particularly if persistent across operating conditions.
· DTC thresholds are monitor-, load-, temperature-, time-, and OSID-dependent (Level 4).
· Persistent bank-to-bank differences of roughly >3–5% suggest injector imbalance, intake/exhaust leakage, O2 sensor variation, or possible cylinder-specific combustion/contribution problems.

Fuel Trim Diagnostic Quick Reference (Level 3):

Observation Interpretation Possible Causes (Partial List)
LTFT > +10% Significant positive correction Vacuum leak, dirty MAF, exhaust leak, low fuel pressure, O2 sensor bias
LTFT < -10% Significant negative correction Excess fuel pressure, leaking injector, incorrect injector characterization, purge-related fuel vapor, biased O2/A/F sensor
Bank-to-bank difference Roughly >3–5% persistent Exhaust leak, O2 sensor variation, injector imbalance, possible cylinder-specific combustion/contribution problem

---

2D. MAF Sensor (2011–2014 Only) (Level 3)

Observed Calibration Starting Range — Not Factory Specification

A commonly used diagnostic rule of thumb is approximately 1 gram per second per liter of engine displacement at warm idle. For a 3.7L engine, this equates to roughly 3.7 g/s (approximately 0.49 lb/min) under normal sea-level conditions. This is only a rough diagnostic heuristic and is affected by idle speed, engine volumetric efficiency, cam timing, barometric pressure, accessory load, and calibration.

Observed MAF Ranges (Level 3 — Working/Observed Ranges, Not Acceptance Limits):

Condition Typical Airflow (lb/min) Typical Airflow (g/s) Typical MAF Period (μs)
P/N 0.42 – 0.48 3.17 – 3.63 1950 – 2150
Drive 0.52 – 0.60 3.93 – 4.53 2200 – 2350

Important Notes:

· These ranges assume a warmed, mechanically healthy engine at approximately normal atmospheric conditions with stable accessory load. They are not acceptance limits.
· MAF period is especially sensitive to sensor electronics, transfer function, and sampling implementation. Values are highly sensor/OSID dependent.
· Warning: 2015–2017 3.7L Mustang is Speed Density (no MAF sensor). These values apply only to 2011–2014 MAF-based applications.

MAF Tuning Method:

1. Log STFT and LTFT across the RPM/load range.
2. Create a histogram of MAF Error by MAF period (or frequency).
3. Apply corrections regionally by airflow zone—never blindly multiply the entire curve by a single percentage.
4. Use stabilized closed-loop conditions for each zone.

HP Tuners Path (Level 4): Engine → Airflow → General → MAF Transfer

---

2E. Idle Spark Advance (Level 3)

Typical Observed Calibration Range — Not Factory Specification

· Idle spark is deliberately used as a primary idle-speed control mechanism. Spark movement alone does not prove an airflow error.
· Typical idle spark values range from approximately 12–22° BTDC depending on load state and calibration.

Condition Typical Timing Range Evidence Level
Park/Neutral 16°–22° BTDC Level 3 — Observed Range
Drive (in gear) 12°–17° BTDC Level 3 — Observed Range
Typical Controlled Swing Approximately 3–5° P-P or equivalent directional correction Level 3 — Observed Range

Important Note on Spark Measurement:

· ±5° from baseline (10° peak-to-peak) is different from a 5° peak-to-peak swing. Be consistent in logging and interpretation. All values in this guide's idle classification use P-P measurements unless otherwise specified.
· The P/N and Drive values are approximate absolute idle spark-advance ranges. The "Typical Controlled Swing" value is a peak-to-peak variation.

---

2F. Idle Evaluation Sequence (Level 3)

Practical Diagnostic Workflow for Idle Calibration

1. Establish Baseline

· Warm engine.
· Record ECT.
· Record commanded idle RPM.
· Record actual RPM.
· Record RPM P-P.
· Record RPM error.
· Record spark P-P.
· Record desired/actual airflow.
· Record throttle angle.
· Record STFT/LTFT.

2. Determine the Type of Behavior

· Single transient → evaluate recovery.
· Damped oscillation → generally acceptable if small.
· Constant-amplitude oscillation → investigate control loop.
· Increasing-amplitude oscillation → stop calibration changes and diagnose.

3. Determine the Control Mechanism

· RPM moves + spark remains relatively stable → prioritize mechanical, airflow, combustion, or accessory-load causes before changing idle spark/PID calibration.
· RPM moves + spark moves significantly → investigate idle-control intervention and its interaction with airflow, torque estimation, throttle control, and load changes.
· RPM moves + throttle moves significantly → investigate ETC/airflow control.
· RPM error persists without oscillation → investigate base airflow/idle target/modeling.

4. Only Then Modify Calibration

· Mechanical problem → fix hardware first.
· Airflow error → correct airflow.
· Control-loop problem → evaluate PID.
· Transient problem → evaluate dashpot/decay.
· Load-response problem → evaluate idle adders/load compensation.

---

3. HP Tuners Navigation References

Parameter names, table accessibility, and exact paths vary by OSID and strategy version. Use Advanced view where required. Tables marked with an asterisk (*) may not be exposed by all OSIDs.

Important Note: HP Tuners menu paths shown here are representative navigation references (Level 4), not Ford service-manual procedures. The actual parameter name and location must be confirmed in the applicable HP Tuners definition file for the vehicle's specific OSID.

Function HP Tuners Path
Idle Control 
Base Idle RPM vs. ECT Engine → Idle → Speed → Base Idle RPM vs. ECT
Base Idle Airflow Engine → Idle → Airflow → Base Airflow
Dashpot / Deceleration Airflow Engine → Idle → Airflow → Dashpot Decay / Airflow Adders
Idle Spark (Base) Engine → Spark → Idle → Base
Idle Spark Limits* Engine → Spark → Idle → Min/Max Spark (if exposed by OSID)
Idle PID Gains* Engine → Idle → RPM Control (if exposed by OSID)
Fuel & Air 
Fuel Cutoff RPM vs. Gear Engine → Fuel → Cutoff/DFCO → Fuel Cutoff RPM vs. Gear
MAF Transfer Function (2011–2014) Engine → Airflow → General → MAF Transfer
Speed-Density / VE Calibration (2015+ SD, if exposed by OSID) Engine → Airflow → Speed Density → VE Coefficients
Injector Data Engine → Fuel → General → Injector Control
Power Enrichment (WOT Fuel) Engine → Fuel → Power Enrichment → EQ Ratio vs. RPM
DFCO Parameters Engine → Fuel → Cutoff/DFCO
VCT 
VCT Base Timing Engine → VCT → Base Timing
VCT WOT Timing* Engine → VCT → WOT Timing (if exposed by OSID)
Transmission (6R80) 
Upshift MPH vs. Throttle vs. Gear Transmission → Shift Scheduling → Upshift MPH vs. Throttle vs. Gear
Shift Pressure / Fill Time* Transmission → Shift Properties (if exposed by OSID; Advanced view)
Vehicle Speed / Speedometer Configuration Transmission → General → Speedometer (if exposed)
Gear Ratio / Final Drive Verify the actual OSID-specific transmission/axle tables
Torque Model 
Friction Torque* Engine → Torque Model → Friction Torque vs. RPM (if exposed by OSID)
Driver Demand → Engine → Torque Model / Driver Demand (exact location and table name OSID-dependent)
Torque Management Engine → Torque Management → applicable torque-management tables (if exposed by OSID)
Spark & ETC 
WOT Spark Advance Engine → Spark → Advance → Base / Borderline / MBT
ETC Limits / Mapping* Engine → Throttle → General (if exposed by OSID)
Protection 
Catalyst Overheat* Engine → Fuel → Catalyst Overheat (if exposed by OSID)

---

4. Calibration Methodology

4A. Idle Tuning (Level 3 / Level 4)

· Log Desired Idle Airflow vs. Actual MAF (or MAP/SD airflow for 2015+).
· Adjust Base Airflow in small, controlled increments and evaluate the resulting idle error, airflow, and spark response before making another change.
· A conservative starting adjustment is 3–5%, but the appropriate step size depends on the magnitude of the idle error and the specific calibration.
· The PCM's modeled desired airflow and the physical MAF reading serve different functions and are not numerically identical.

HP Tuners Path (Level 4): Engine → Idle → Airflow → Base Airflow

---

4B. Idle PID Gains (Level 3 / Level 4)

HP Tuners Path (Level 4): Engine → Idle → RPM Control → Proportional / Integral / Derivative

Gain Typical Range Notes
Proportional OSID-dependent Immediate response; scales with RPM error
Integral OSID-dependent Long-term drift correction
Derivative OSID-dependent; may be zero/disabled in some strategies Damping; rarely used

Tuning Note (Level 3): For aftermarket camshafts or throttle bodies, a 20–30% reduction in proportional gain may be used as an initial calibration experiment when excessive control-loop hunting has been confirmed. Validate the result against RPM error, spark correction, and recovery time; do not treat 20–30% as a universal target.

After significant calibration changes, reset the applicable adaptive idle/KAM learning using the appropriate scan-tool procedure when available. Battery disconnection may clear adaptive memory on some vehicles but should not be assumed equivalent to a strategy-specific adaptive reset.

---

4C. Transmission Tuning (6R80) (Level 3 / Level 4)

· Line Pressure: Stock commanded pressure varies by gear, load, and temperature. Do not apply arbitrary increases without verified engineering limits.
· Shift Firmness: Adjust Oncoming/Offgoing pressures and Desired Shift Time based on measured shift behavior, not arbitrary percentages.
· Clutch Fill Time: Do not reduce fill time without comparing commanded vs. actual shift execution. Monitor adaptive learning data.
· Shift Scheduling: Some tables use Vehicle Speed (MPH) as a primary axis; actual shift execution is influenced by torque management, engine load, and adaptive strategies.

4C.1. Adaptive Shift Behavior — Level 2 / Level 3 / Level 4

The 6R80 uses adaptive strategies that can modify clutch pressure/fill behavior based on learned shift results. Therefore, a shift that changes after repeated cycles is not automatically evidence of a mechanical fault or an incorrect pressure/fill table.

When diagnosing or tuning a shift, log where available:

· Commanded gear
· Actual gear
· Turbine/input speed
· Output speed
· Engine RPM
· Engine torque
· Throttle angle
· Shift time
· Torque-management intervention
· Adaptive/learned shift values

Evaluate several repeatable shifts under the same conditions before changing pressure or fill-time calibration.

After significant transmission-calibration changes, perform the applicable adaptive relearn/reset procedure for the specific OSID.

HP Tuners Paths (Level 4 — if exposed by OSID):

· Shift Pressure / Fill Time: Transmission → Shift Properties (Advanced view)
· Upshift MPH vs. Throttle vs. Gear: Transmission → Shift Scheduling → Upshift MPH vs. Throttle vs. Gear

---

4D. DFCO Tuning (Level 3 / Level 4)

Typical Calibration Starting References — Not Ford Specifications (Level 3):

Parameter Typical Value Evidence Level
DFCO Enable RPM ~1500 RPM (gear-dependent) Level 3 — Observed Range
DFCO Disable RPM ~1150–1200 RPM Level 3 — Observed Range
DFCO Enable ECT ~140°F Level 3 — Observed Range
DFCO Enable VSS OSID-dependent Level 4 — Read from calibration
DFCO Delay Time ~0.50 sec Level 3 — Observed Range
Fuel Re-entry Ramp OSID-dependent Level 4 — Read from calibration

Note: Values are representative calibration observations and may differ substantially by OSID, transmission state, vehicle speed, ECT, and calibration strategy. Always read the actual stock values before changing them.

HP Tuners Path (Level 4): Engine → Fuel → Cutoff/DFCO

---

4E. Power Enrichment (WOT Fuel) (Level 3 / Level 4)

· Stock WOT Lambda targets are OSID-dependent (Level 4).
· Typical naturally aspirated calibrations target 0.85–0.87 Lambda (EQ ~1.15–1.18) (Level 3 — Observed Range).
· For modified/forced-induction applications, establish commanded lambda from the specific engine/fuel/boost combination rather than applying a generic target.
· Verify injector capacity, fuel system capability, combustion characteristics, and knock response before making WOT fuel changes.

HP Tuners Path (Level 4): Engine → Fuel → Power Enrichment → EQ Ratio vs. RPM

---

4F. WOT Spark Advance (Level 3 / Level 4)

Typical Naturally Aspirated Calibration Observation — Not Target Values (Level 3)

· Stock WOT spark is calibration-, octane-, load-, temperature-, and knock-strategy-dependent.
· Typical naturally aspirated calibrations: ~20–24° BTDC at peak torque (~4500 RPM), tapering to ~16–18° at 6500 RPM.

Important: These values are not target values. Establish the stock OSID's actual spark curve first and validate against fuel, load, IAT, ECT, VCT, and knock response.

HP Tuners Path (Level 4): Engine → Spark → Advance → Base / Borderline / MBT

---

4G. Torque Model & Driver Demand (Level 3 / Level 4)

· Friction Torque (Level 3 — Observed Range): Warm idle ~22–35 lb-ft (calibration-dependent). Not a universal Ford specification.
· Driver Demand (Level 4): Converts driver input and relevant operating conditions into a desired torque request. Exact axes and implementation are OSID-dependent.
· Torque-model errors can produce incorrect calculated torque and can affect throttle control, load calculation, torque management, and transmission behavior.

HP Tuners Paths (Level 4):

· Friction Torque: Engine → Torque Model → Friction Torque vs. RPM (if exposed by OSID)
· Driver Demand: Engine → Torque Model / Driver Demand (exact location and table name OSID-dependent)

---

5. Adaptive Learning & Reset Procedures

5A. KAM Reset (Keep Alive Memory) (Level 3)

· Preferred Method: Use the scan tool's KAM reset function when available—this is the controlled procedure.
· Alternative: Battery disconnect may clear adaptives but is not universally equivalent for all modules.

5B. Idle Relearn Procedure (Level 3)

After resetting KAM, an idle relearn procedure may be necessary. The exact procedure varies by OSID. A common practical routine includes:

1. Start engine and allow it to reach operating temperature.
2. Allow engine to idle in Park/Neutral with A/C off until stable.
3. Shift to Drive (brake applied) and allow idle to stabilize.
4. Cycle A/C on and off to allow idle airflow adaptation.
5. Drive vehicle through a range of conditions to allow full adaptive learning.

Note: Consult your specific service documentation for the exact procedure for your OSID and model year.

---

6. Platform Reference Data (2011–2014)

Verify every item against your vehicle's service data.

Parameter Mustang F‑150 Evidence Level
Published Power 305 hp @ 6,500 RPM 302 hp @ 6,500 RPM Level 1
Published Torque 280 lb-ft @ 4,250 RPM 278 lb-ft @ 4,000 RPM Level 1
Motorcraft Service Part SP-520 SP-520 Level 1
Spark Plug Gap 0.049–0.053 in 0.049–0.053 in (verify 2011 manual) Level 1
Engineering Plug ID CYFS-12F-5 where confirmed CYFS-12F-5 where confirmed Level 2
Firing Order 1-4-2-5-3-6 1-4-2-5-3-6 Level 1
PCM Strategy Verify OSID from vehicle Verify OSID from vehicle Level 4
Throttle Body Application/part-number dependent; verify actual Ford part dimensions Application/part-number dependent; verify actual Ford part dimensions Level 2
Axle Ratios Varies by year/package Varies by year/package Level 2
Speed Limiter ~113–118 MPH (observed range) ~96–98 MPH (observed range) Level 3

Note: "Copperhead" is an informal PCM strategy family designation. The actual PCM strategy must be determined from the specific vehicle/OSID.

---

7. 2015+ Speed Density Note (Level 2)

2015–2017 North American 3.7L Mustang: Available service/aftermarket documentation identifies the 2015–2017 3.7L Mustang as a MAP-based speed-density strategy without a conventional MAF transfer function.

HP Tuners Path (Level 4 — if exposed): Engine → Airflow → Speed Density → VE Coefficients

Warning:

· Parameter names and table accessibility vary by OSID and strategy version.
· The system uses MAP/IAT/engine-speed/model-based airflow calculation with various inferred-airflow mechanisms. "Speed Density" describes the strategy, not the absence of adaptive logic.

---

8. Quick Diagnostic Reference Card (Level 3)

Practical Calibration Heuristics — Not Factory Specifications

This card compresses the six bands of the classification table in section 2A into
three columns. Its boundaries are the same boundaries; where a reading falls near
one, read section 2A rather than this card.

· Excellent = the Perfect / Exceptional and Excellent bands of section 2A
· Good = the Good / Healthy and Acceptable bands
· Investigate = the Marginal and Poor / Severe Oscillation bands

Parameter Excellent Good Investigate Evidence Level
P/N RPM P-P <15 RPM ≥15–<40 RPM ≥40 RPM Level 3
Drive RPM P-P <20 RPM ≥20–<50 RPM ≥50 RPM Level 3
Spark P-P ≤4° >4–<8° ≥8°, or any amplitude that is rhythmic Level 3
Idle Recovery Time <1 sec <2 sec ≥2 sec Level 3
RPM Error ±0–5 RPM >±5–±20 RPM >±20 RPM persistent Level 3
STFT Near 0% Moderate correction Persistent >±10% Level 3
LTFT Near 0% Moderate correction Persistent >±10% Level 3
Bank Trim Difference <3% 3–<5% ≥5% persistent Level 3
MAF (P/N) — 2011–2014 only ~0.49 lb/min (rule of thumb) — Varies with OSID Level 3
MAF (Drive) — 2011–2014 only ~0.52–0.60 lb/min — Varies with load Level 3

---

9. Final Verification Statement

Ford-Verified Specifications (Level 1):

· Firing order: 1-4-2-5-3-6
· Spark plug: Motorcraft SP-520 for documented 3.7L applications
· Spark plug gap: 0.049–0.053 in (1.25–1.35 mm) for 2014 F-150 and Mustang; 0.052–0.056 in for some 2011 F-150 applications
· 6R80 fluid: MERCON LV / WSS-M2C938-A
· 6R80 dry-fill capacity: Current Ford documentation: 12.12 qt (11.47 L) ; Historical 2011–2013 F-150 3.7L: 12.1 qt (11.7 L)
· 6R80 gear ratios (Ford Service Reference): 4.17, 2.34, 1.52, 1.14, 0.87, 0.69
· Engine power outputs: Mustang 305 hp / F-150 302 hp (common published ratings)

Technical Reference (Level 2):

· Ti-VCT control capability: up to 60° intake / up to 50° exhaust
· Stall-speed range: 2300–2580 RPM (F-150 3.7L service reference)
· Spark plug engineering ID: CYFS-12F-5 (where confirmed by Ford parts documentation)
· Installation torque specifications: 11 lb-ft / 53 lb-in (verify exact 3.7L application)
· Throttle body: application/part-number dependent

Calibration Heuristics / Observed Ranges (Level 3):

· Idle RPM stability classifications (P-P RPM, spark swing, recovery time)
· RPM Error = Actual − Desired
· Warm idle RPM ranges (~550–750 RPM)
· Fuel trim diagnostic thresholds (±10% investigation trigger, >3–5% bank difference trigger)
· MAF ~1 g/s per liter rule of thumb and observed ranges
· Idle spark ranges (12–22° BTDC typical)
· DFCO typical starting references
· WOT spark typical observed ranges
· Friction torque typical range (~22–35 lb-ft)
· Speed limiter observed ranges (~113–118 MPH Mustang / ~96–98 MPH F-150)

OSID-Specific (Level 4):

· All numerical calibration values (RPM limits, specific airflow numbers, VCT angles, shift MPH, DFCO thresholds, PID gains, injector characterization, etc.) must be sourced from the user's specific stock OSID file.

---

Appendix A: Optional Modification Notes

The following are tuning modifications, not stock calibration references.

A1. Burble/Pop Tuning (Level 3 — Modification Strategy)

If desired, adjustments can be made to DFCO Delay and Deceleration Spark tables to modify exhaust sound. However:

· Verify parameter availability for your specific OSID.
· Repeated intentional afterfire can increase exhaust/catalyst thermal loading and should not be treated as a harmless sound-only calibration change.
· This is a modification strategy, not a stock calibration reference.

HP Tuners Paths (Level 4):

· DFCO Delay: Engine → Fuel → Cutoff/DFCO → DFCO Delay Time
· Deceleration Spark: Engine → Spark → Deceleration Spark

A2. Forced Induction Lambda Considerations (Level 3 — Modification Strategy)

For modified/forced-induction applications:

· Establish commanded lambda from the specific engine/fuel/boost combination rather than applying a generic target.
· Factors include fuel type, compression ratio, boost level, combustion temperature, knock margin, injector/fuel-system capability, and catalyst configuration.
· Always verify with proper instrumentation (wideband O2, EGT, knock detection).

A3. Injector Data (Level 2 / Level 4)

OEM Injector Hardware (Level 2 — Aftermarket/Parts Cross-Reference):

· Bosch 62667 (Ford BR3E-F5A) – ~330 cc/min @ 43.5 psi.

Calibration values (Level 4 — OSID-Specific):

Parameter Notes
High Slope Verify from your stock calibration
Breakpoint Verify from your stock calibration
Offset Voltage-dependent; verify from your stock calibration
Minimum Pulsewidth Verify from your stock calibration

HP Tuners Path (Level 4): Engine → Fuel → General → Injector Control

Note: Calibration values cannot be inferred from physical flow rate alone. Always read from your specific stock OSID file.

A4. Transient Fuel (Liquid Puddle Compensation) (Level 3 / Level 4)

HP Tuners Path (Level 4): Engine → Fuel → Transient → Liquid Fuel Puddle

· Evaporation Time Constant (Level 3 — Typical Calibration Reference): Warm engine ~0.045–0.085 sec (calibration-dependent)
· Affects tip-in lean/rich behavior. E85 or modified intake runners may require recalibration.
· Use transient lambda response to determine whether the existing model is deficient before changing the table.

---

End of Complete Reference Guide