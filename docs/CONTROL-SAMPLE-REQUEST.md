# Getting a control sample — where the same engine lives, and what to ask for

The one measurement this investigation has never had is **another healthy engine
at warm idle**. Everything else has been exhausted. This is how to get it.

## The 3.7 Ti-VCT is not rare — it is just not in many F-150s

The same engine, in the same Cyclone family, was fitted to:

| Vehicle | Years | Note |
|---|---|---|
| **Ford Mustang V6** | 2011–2014 | Largest owner community by far |
| **Ford F-150** | 2011–2014 | This truck |
| **Lincoln MKZ / MKS / MKT / MKX** | ~2010–2016 | Sold in the Gulf |
| **Ford Taurus** | 2010–2019 | 3.7 in some trims and police models |
| **Ford Edge** | ~2011–2014 | Sport trim |
| **Ford Transit** | 2015+ | Fleet vans |
| **Mazda CX-9** | earlier 3.7 | Same family, different calibration |

**Second best, and far more common in Saudi Arabia: the 3.5 Ti-VCT.** Explorer,
Edge, Taurus, Flex and the Lincolns. Same Cyclone architecture, same twin
independent cam phasing, same PCM strategy family. It will not settle an absolute
spark number, **but it fully answers the structural question** — whether a
healthy engine of this family holds a clean, constant-amplitude oscillation at
idle for minutes on end.

**Third: literally any engine.** The structural question does not care about
displacement. If a healthy engine's idle wanders with no dominant frequency and
this one holds a 0.32 Hz line for three hours, that is the finding.

## What to capture — hand this to whoever has the car

Two channels, three minutes, and it is done.

1. Car Scanner, connect the adapter, **engine running and fully warm**
2. **Park or Neutral, standstill, A/C OFF, no loads**, foot off everything
3. Put **`Engine RPM`** and **`Tim. adv.`** on the graph
4. Let it record **three minutes** without touching anything
5. Export: **`CSV #2 (Horizontal layout)`**, with **"Round values" OFF**

Record alongside the file: year, model, engine, mileage, and **whether the car is
stock or tuned**. A tuned car has a modified idle calibration and is not a
control.

## A request to post on an owners' forum

The Mustang 3.7 community is the largest source. F150Forum, Mustang6G and
allfordmustangs all have active members with scan tools.

> **Asking for 2 minutes of idle datalog from a stock 3.7 (or 3.5) Ti-VCT**
>
> I am chasing a small idle vibration on a 2014 F-150 3.7 that has survived seven
> repairs and shows no codes. Logging shows the engine speed oscillating in a
> clean rhythm at 0.32 Hz — about one cycle every 3.1 seconds — roughly 40 rpm
> peak to peak in Park, holding steady for three hours. Timing advance follows
> engine speed 0.1 s later at r = −0.9, so the PCM is correcting a disturbance
> rather than causing it.
>
> What I cannot tell is whether that is abnormal, because I have never seen
> another one measured. If anyone with a **stock** 3.7 or 3.5 Ti-VCT can log
> **engine speed and spark advance at warm idle in Park for two minutes**, with
> A/C off, I would be very grateful — any scan tool that exports CSV. I am happy
> to share what I find back.
>
> Two things I am looking for: whether idle rpm shows a **dominant frequency** or
> just random wander, and what **spark advance** sits at in Park (mine reads
> 12°).

## What is already ruled out as a source

* **Datazap and similar log-sharing sites** carry overwhelmingly wide-open-throttle
  tuning pulls. Idle logs have no tuning value and are rarely uploaded. Worth a
  look, not worth relying on.
* **This project's own container cannot fetch any web page** — the network blocks
  it — so any download has to be done by the owner and uploaded here.
